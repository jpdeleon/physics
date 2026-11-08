"""SSH tunnel management using the system ssh binary.

Uses ~/.ssh/config natively — ProxyJump, IdentityFile, and all other
directives are honoured exactly as they would be in a terminal session.
"""
from __future__ import annotations

import contextlib
import shutil
import socket
import subprocess
import time
from collections.abc import Generator


def _system_ssh() -> str:
    """Return the system ssh binary path, preferring /usr/bin/ssh over wrappers."""
    for candidate in ("/usr/bin/ssh", shutil.which("ssh")):
        if candidate:
            return candidate
    raise RuntimeError("ssh binary not found on this system")


def _port_open(port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except OSError:
        return False


@contextlib.contextmanager
def ssh_tunnel(
    host: str,
    local_port: int = 11434,
    remote_port: int = 11434,
) -> Generator[None, None, None]:
    """Open an SSH port-forward tunnel to *host* using the system ssh binary.

    Blocks until the local port is reachable, then yields.  Terminates the
    tunnel process on exit regardless of success or failure.

    The system ssh binary reads ~/.ssh/config, so ProxyJump through an
    intermediate host (e.g. m2) is handled automatically with no extra
    configuration here.
    """
    ssh = _system_ssh()
    cmd = [
        ssh,
        "-N",                              # no remote command — port-forward only
        "-L", f"{local_port}:localhost:{remote_port}",
        "-o", "ExitOnForwardFailure=yes",  # exit immediately if forward fails
        "-o", "ServerAliveInterval=10",
        "-o", "ServerAliveCountMax=3",
        host,
    ]
    print(f"  opening SSH tunnel: ssh -N -L {local_port}:localhost:{remote_port} {host}")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if _port_open(local_port):
                break
            if proc.poll() is not None:
                err = proc.stderr.read().decode(errors="replace").strip()
                raise RuntimeError(f"SSH tunnel exited early: {err or '(no stderr)'}")
            time.sleep(0.3)
        else:
            proc.terminate()
            raise RuntimeError(
                f"Timed out waiting for SSH tunnel on localhost:{local_port}"
            )
        print(f"  tunnel ready  localhost:{local_port} → {host}:{remote_port}")
        yield
    finally:
        proc.terminate()
        proc.wait()
        print("  SSH tunnel closed")
