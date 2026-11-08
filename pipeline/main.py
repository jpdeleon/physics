"""CLI orchestrator: fetch → summarize → render → generate _toc.yml."""
from __future__ import annotations

import argparse
import contextlib
import subprocess
import sys
import time
from pathlib import Path

import yaml

from pipeline.fetch import fetch_video, extract_video_id
from pipeline.render import render_chapter, _slug, CHAPTERS_DIR
from pipeline.summarize import summarize, _OLLAMA_MODEL, _ANTHROPIC_MODEL
from pipeline.tunnel import ssh_tunnel

BOOK_DIR = Path(__file__).parent.parent / "book"
TOC_PATH = BOOK_DIR / "_toc.yml"


def build_toc(chapter_slugs: list[str]) -> None:
    toc = {
        "format": "jb-book",
        "root": "intro",
        "chapters": [{"file": f"chapters/{slug}"} for slug in chapter_slugs],
    }
    TOC_PATH.write_text(
        yaml.dump(toc, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    print(f"  wrote {TOC_PATH}")


def _load_config(settings: str) -> tuple[dict, Path]:
    config_path = Path(settings)
    if not config_path.exists():
        print(f"Error: {config_path} not found", file=sys.stderr)
        sys.exit(1)
    with config_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f), config_path


def _backend_params(config: dict) -> tuple[str, str, str, str | None]:
    """Return (backend, ollama_model, anthropic_model, tunnel_host)."""
    backend = config.get("backend", "ollama")
    if backend not in ("ollama", "anthropic"):
        print(f"Error: unknown backend '{backend}'. Use 'ollama' or 'anthropic'.", file=sys.stderr)
        sys.exit(1)
    ollama_cfg = config.get("ollama", {})
    ollama_host = ollama_cfg.get("host", "local")
    ollama_model = ollama_cfg.get("model", _OLLAMA_MODEL)
    anthropic_cfg = config.get("anthropic", {})
    anthropic_model = anthropic_cfg.get("model", _ANTHROPIC_MODEL)
    tunnel_host = ollama_host if (backend == "ollama" and ollama_host != "local") else None
    return backend, ollama_model, anthropic_model, tunnel_host


def _process_video(
    url: str,
    title_override: str | None,
    backend: str,
    ollama_model: str,
    anthropic_model: str,
    skip_existing: bool,
    index: str = "",
) -> str | None:
    """Fetch, summarize, and render one video. Returns slug or None on skip."""
    video_id = extract_video_id(url)
    slug = _slug(video_id)
    out_path = CHAPTERS_DIR / f"{slug}.md"

    prefix = f"[{index}] " if index else ""
    print(f"\n{prefix}{url}")

    if skip_existing and out_path.exists():
        print(f"  skipping (chapter already exists): {out_path.name}")
        return slug

    print("  fetching transcript...")
    video = fetch_video(url, title_override)
    print(f"  title: {video.title}")
    print(f"  transcript: {'yes' if video.transcript else 'NO TRANSCRIPT'}")

    summary = None
    if video.transcript:
        print(f"  summarizing via {backend}...")
        try:
            summary = summarize(
                video.transcript,
                video.title,
                backend=backend,
                ollama_model=ollama_model,
                anthropic_model=anthropic_model,
            )
        except Exception as exc:
            print(f"  [warn] summarize failed: {exc}. Using placeholder.")
        time.sleep(0.5)

    rendered = render_chapter(video, summary)
    print(f"  rendered: {rendered}")
    return slug


def cmd_run(args: argparse.Namespace) -> None:
    config, _ = _load_config(args.settings)
    backend, ollama_model, anthropic_model, tunnel_host = _backend_params(config)
    entries = config.get("videos", [])
    if not entries:
        print("No videos found in config.", file=sys.stderr)
        sys.exit(1)

    print(f"Backend: {backend}", end="")
    if backend == "ollama":
        print(f"  model: {ollama_model}  host: {config.get('ollama', {}).get('host', 'local')}")
    else:
        print(f"  model: {anthropic_model}")

    tunnel_ctx = ssh_tunnel(tunnel_host) if tunnel_host else contextlib.nullcontext()
    chapter_slugs: list[str] = []

    with tunnel_ctx:
        for i, entry in enumerate(entries, 1):
            slug = _process_video(
                url=entry["url"],
                title_override=entry.get("title_override"),
                backend=backend,
                ollama_model=ollama_model,
                anthropic_model=anthropic_model,
                skip_existing=args.skip_existing,
                index=f"{i}/{len(entries)}",
            )
            if slug:
                chapter_slugs.append(slug)

    print(f"\nGenerating _toc.yml with {len(chapter_slugs)} chapter(s)...")
    build_toc(chapter_slugs)
    print("\nDone. Run: uv run jupyter-book build book/")


def cmd_build(args: argparse.Namespace) -> None:
    subprocess.run(["uv", "run", "jupyter-book", "build", "book", "--all"], check=True)


def cmd_clean(args: argparse.Namespace) -> None:
    subprocess.run(["uv", "run", "jupyter-book", "clean", "book"], check=True)


def cmd_add(args: argparse.Namespace) -> None:
    config, config_path = _load_config(args.settings)
    backend, ollama_model, anthropic_model, tunnel_host = _backend_params(config)

    # Add URL to settings.yml if not already present
    entries = config.setdefault("videos", [])
    existing_urls = {e["url"] for e in entries}
    if args.url not in existing_urls:
        entries.append({"url": args.url, "title_override": None})
        with config_path.open("w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"Added {args.url} to {config_path}")
    else:
        print(f"{args.url} already in {config_path}")

    print(f"Backend: {backend}", end="")
    if backend == "ollama":
        print(f"  model: {ollama_model}  host: {config.get('ollama', {}).get('host', 'local')}")
    else:
        print(f"  model: {anthropic_model}")

    tunnel_ctx = ssh_tunnel(tunnel_host) if tunnel_host else contextlib.nullcontext()

    with tunnel_ctx:
        new_slug = _process_video(
            url=args.url,
            title_override=None,
            backend=backend,
            ollama_model=ollama_model,
            anthropic_model=anthropic_model,
            skip_existing=False,
        )

    # Rebuild _toc from all chapters present on disk (preserves order from settings)
    all_slugs = [_slug(extract_video_id(e["url"])) for e in entries]
    print(f"\nGenerating _toc.yml with {len(all_slugs)} chapter(s)...")
    build_toc(all_slugs)

    if args.build:
        print("\nBuilding Jupyter Book...")
        subprocess.run(["uv", "run", "jupyter-book", "build", "book/"], check=True)
    else:
        print("\nDone. Run: uv run jupyter-book build book/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Jupyter Book from YouTube URLs")
    parser.add_argument("--settings", default="settings.yml", help="Path to settings YAML file")
    parser.set_defaults(func=cmd_run)

    # Global skip-existing flags (for cmd_run)
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip videos whose chapter .md already exists (default: true)",
    )
    parser.add_argument(
        "--no-skip-existing",
        dest="skip_existing",
        action="store_false",
        help="Re-process videos even if chapter .md already exists",
    )

    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add", help="Add a video and optionally build the book")
    add_parser.add_argument("url", help="YouTube URL to add")
    add_parser.add_argument("--build", action="store_true", help="Run jupyter-book build after rendering")
    add_parser.set_defaults(func=cmd_add)

    subparsers.add_parser("build", help="Build the Jupyter Book HTML").set_defaults(func=cmd_build)
    subparsers.add_parser("clean", help="Remove the Jupyter Book build cache").set_defaults(func=cmd_clean)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
