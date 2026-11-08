#!/usr/bin/env python3
"""
ollama_profile.py
-----------------
Benchmarks inference speed (tokens/sec) across multiple Ollama instances
reachable via SSH. Uses your ~/.ssh/config — just provide the Host alias.

Requirements:
    pip install rich

Configuration:
    Edit the HOSTS list below using the Host aliases from your ~/.ssh/config,
    then run:
        python ollama_profile.py
"""

import json
import re
import statistics
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich import box

# ── Configuration ─────────────────────────────────────────────────────────────

HOSTS = [
    #{
    #    "label":  "Desktop",
    #    "local":  True,         # ← runs commands locally, no SSH
    #    "ollama": "ollama",     # or full path e.g. /usr/local/bin/ollama
    #},
    {
        "label":  "Server",
        "alias":  "jm4",        # ← Host alias from ~/.ssh/config
        "ollama": "ollama",
    },
]

PROMPT     = "What is entropy? Answer in 2 sentences."
MAX_TOKENS = 50    # tokens to generate per run
RUNS       = 3     # runs per model (mean ± stdev reported)

# ── SSH helpers ───────────────────────────────────────────────────────────────



def run_cmd(h: dict, cmd: str) -> str:
    """Run a shell command locally or via ssh alias, returning combined stdout+stderr."""
    import subprocess
    if h.get("local"):
        full_cmd = cmd
    else:
        # Use system ssh directly — handles ProxyJump, keys, everything in ~/.ssh/config
        full_cmd = f"ssh {h['alias']} {cmd!r}"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=600)
    return (result.stdout + result.stderr).strip()


# ── Ollama queries ────────────────────────────────────────────────────────────

# Models larger than this (in GB) are skipped during benchmarking
MAX_MODEL_SIZE_GB = 20.0

def list_models(h: dict, ollama: str) -> list[dict]:
    """Return list of {name, size_gb} dicts, skipping non-model lines."""
    out = run_cmd(h, f"{ollama} list")
    models = []
    for line in out.splitlines()[1:]:   # skip header row
        parts = line.split()
        # Valid model lines: first column contains a colon (name:tag)
        if len(parts) < 3 or ":" not in parts[0]:
            continue
        name = parts[0]
        # Parse size — ollama list shows e.g. "4.7 GB" or "892 MB"
        size_gb = 0.0
        try:
            val  = float(parts[-2])
            unit = parts[-1].upper()
            if unit == "GB":
                size_gb = val
            elif unit == "MB":
                size_gb = val / 1024
        except (ValueError, IndexError):
            pass
        models.append({"name": name, "size_gb": size_gb})
    return models


def benchmark_model(h: dict, ollama: str, model: str) -> Optional[dict]:
    """
    Uses `ollama run --verbose` piped output to extract tokens/sec.
    Ollama prints lines like:
        eval rate:         23.45 tokens/s
        prompt eval rate:  312.1 tokens/s
    """
    # pipe prompt + /bye so the session exits cleanly
    cmd = (
        f"printf '/set verbose\\n{PROMPT}\\n/bye\\n' | "
        f"{ollama} run --nowordwrap {model} 2>&1"
    )

    runs_tps  = []
    runs_prompt_rate = []

    for _ in range(RUNS):
        out = run_cmd(h, cmd)
        tps_m  = re.search(r"eval rate:\s+([\d.]+)\s+tokens/s", out)
        prmp_m = re.search(r"prompt eval rate:\s+([\d.]+)\s+tokens/s", out)

        if tps_m:
            runs_tps.append(float(tps_m.group(1)))
        if prmp_m:
            runs_prompt_rate.append(float(prmp_m.group(1)))

    if not runs_tps:
        return None

    result: dict = {
        "tokens_per_sec": {
            "mean":  round(statistics.mean(runs_tps), 2),
            "stdev": round(statistics.stdev(runs_tps), 2) if len(runs_tps) > 1 else 0.0,
            "min":   round(min(runs_tps), 2),
            "max":   round(max(runs_tps), 2),
        },
        "successful_runs": len(runs_tps),
    }
    if runs_prompt_rate:
        result["prompt_eval_rate_mean"] = round(statistics.mean(runs_prompt_rate), 2)
    return result


# ── Per-host profiling ────────────────────────────────────────────────────────

def profile_host(h: dict, console: Console) -> dict:
    result = {
        "label":     h["label"],
        "host":      h.get("alias", "localhost"),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "reachable": False,
        "models":    [],
    }

    # Verify connectivity with a quick version check
    try:
        ver = run_cmd(h, f"{h['ollama']} --version")
        if not ver:
            raise RuntimeError("empty response")
    except Exception as e:
        result["error"] = str(e)
        console.print(f"  [red]❌ connection failed: {e}[/red]")
        return result

    result["reachable"] = True
    result["ollama_version"] = ver

    models = list_models(h, h["ollama"])
    skipped = [m for m in models if m["size_gb"] > MAX_MODEL_SIZE_GB]
    models   = [m for m in models if m["size_gb"] <= MAX_MODEL_SIZE_GB]
    names    = [m["name"] for m in models]
    console.print(f"  {len(models)} model(s): {', '.join(names)}")
    if skipped:
        console.print(f"  [dim]skipping {len(skipped)} large model(s) (>{MAX_MODEL_SIZE_GB}GB): "
                      f"{', '.join(m['name'] for m in skipped)}[/dim]")

    for m in models:
        model = m["name"]
        console.print(f"  [dim]  {model} ({m['size_gb']:.1f} GB) — running {RUNS} benchmark(s)…[/dim]")
        bench = benchmark_model(h, h["ollama"], model)
        entry: dict = {"model": model, "size_gb": m["size_gb"]}

        if bench:
            entry.update(bench)
            tps = bench["tokens_per_sec"]
            console.print(
                f"    ✅  {tps['mean']:.1f} tok/s  "
                f"(σ={tps['stdev']:.1f}  min={tps['min']:.1f}  max={tps['max']:.1f})"
            )
        else:
            entry["error"] = "Could not parse verbose output — is this model working?"
            console.print("    [red]❌  failed to parse output[/red]")

        result["models"].append(entry)

    return result


# ── Report ────────────────────────────────────────────────────────────────────

def render_report(profiles: list[dict], console: Console):
    console.rule("[bold]Results")

    for p in profiles:
        header = f"[bold cyan]{p['label']}[/bold cyan]  [dim]{p['host']}[/dim]"
        if not p["reachable"]:
            console.print(f"\n{header}  [red]UNREACHABLE — {p.get('error', '')}[/red]")
            continue

        console.print(f"\n{header}  [dim]{p.get('ollama_version', '')}[/dim]")

        t = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold")
        t.add_column("Model",        style="cyan", no_wrap=True)
        t.add_column("tok/s",        justify="right")
        t.add_column("± stdev",      justify="right", style="dim")
        t.add_column("min",          justify="right", style="dim")
        t.add_column("max",          justify="right", style="dim")
        t.add_column("prompt tok/s", justify="right", style="dim")
        t.add_column("runs",         justify="right", style="dim")

        for m in p["models"]:
            tps = m.get("tokens_per_sec")
            if tps:
                t.add_row(
                    m["model"],
                    f"{tps['mean']:.1f}",
                    f"{tps['stdev']:.1f}",
                    f"{tps['min']:.1f}",
                    f"{tps['max']:.1f}",
                    str(m.get("prompt_eval_rate_mean", "—")),
                    str(m.get("successful_runs", "?")),
                )
            else:
                t.add_row(m["model"], "—", "—", "—", "—", "—", "0", style="red dim")

        console.print(t)

    # ── Side-by-side comparison ───────────────────────────────────────────────
    reachable = [p for p in profiles if p["reachable"] and p["models"]]
    if len(reachable) < 2:
        return

    console.rule("[bold]Side-by-side Comparison")

    all_models: dict[str, dict] = {}
    for p in reachable:
        for m in p["models"]:
            all_models.setdefault(m["model"], {})
            tps = m.get("tokens_per_sec")
            all_models[m["model"]][p["label"]] = tps["mean"] if tps else None

    cmp = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold")
    cmp.add_column("Model", style="cyan", no_wrap=True)
    for p in reachable:
        cmp.add_column(p["label"], justify="right")
    cmp.add_column("Winner", justify="left", style="green")

    for model, scores in all_models.items():
        valid = {lbl: s for lbl, s in scores.items() if s is not None}
        winner = max(valid, key=valid.get) if valid else None

        row = [model]
        for p in reachable:
            s = scores.get(p["label"])
            cell = f"{s:.1f}" if s is not None else "—"
            if p["label"] == winner and len(valid) > 1:
                cell = f"[bold green]{cell}[/bold green]"
            row.append(cell)

        if winner and len(valid) > 1:
            vals = sorted(valid.values(), reverse=True)
            pct  = (vals[0] - vals[1]) / vals[1] * 100
            row.append(f"{winner}  +{pct:.0f}%")
        else:
            row.append("—")

        cmp.add_row(*row)

    console.print(cmp)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    console = Console()
    console.print(
        f"\n[bold]Ollama SSH Profiler[/bold]  "
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n"
        f"Prompt  : [italic]\"{PROMPT[:70]}\"[/italic]\n"
        f"Tokens  : {MAX_TOKENS}   Runs/model : {RUNS}\n"
    )

    profiles = []
    for h in HOSTS:
        console.rule(f"[bold]{h['label']}[/bold] — {h.get('alias', 'localhost')}")
        profiles.append(profile_host(h, console))

    render_report(profiles, console)

    out = f"ollama_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out, "w") as f:
        json.dump(profiles, f, indent=2)
    console.print(f"[dim]JSON saved → {out}[/dim]\n")


if __name__ == "__main__":
    main()
