#!/usr/bin/env python3
"""scripts/serve.py

Convenience utility to preview the GitHub Pages site locally.

Usage::

    python scripts/serve.py [--port 8000] [--dir docs]

The script performs the following steps:
1. Checks whether the requested TCP port is already in use.
2. If so, terminates the processes holding that port.
3. Launches a simple HTTP server to serve the specified directory.

Requires `lsof` to be available (installed by default on macOS and most Linux).
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path


def _find_pids(port: int) -> list[int]:
    """Return a list of PIDs currently listening on *port* (TCP)."""
    try:
        output = subprocess.check_output(["lsof", "-ti", f"tcp:{port}"], text=True)
        return [int(pid) for pid in output.strip().splitlines() if pid.strip()]
    except subprocess.CalledProcessError:
        # lsof exits with non-zero status if no processes found
        return []


def _kill_pids(pids: list[int], port: int) -> None:
    for pid in pids:
        try:
            print(f"Killing process {pid} occupying port {port}…")
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            # Process may have already exited
            pass


def _run_server(directory: Path, port: int) -> None:
    print(f"Serving '{directory}' at http://localhost:{port} (Ctrl+C to stop)")
    subprocess.run([sys.executable, "-m", "http.server", str(port), "--directory", str(directory)], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve local website, freeing port first if needed.")
    parser.add_argument("--port", type=int, default=8000, help="Port to serve on (default: 8000)")
    parser.add_argument("--dir", dest="directory", default="docs", help="Directory to serve (default: docs)")
    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    if not directory.exists():
        print(f"Error: directory '{directory}' does not exist.")
        sys.exit(1)

    pids = _find_pids(args.port)
    if pids:
        _kill_pids(pids, args.port)
    else:
        print(f"Port {args.port} is free.")

    _run_server(directory, args.port)


if __name__ == "__main__":
    main()
