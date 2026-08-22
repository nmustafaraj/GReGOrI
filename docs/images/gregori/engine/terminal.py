"""Terminal visualization, ANSI colored inspection, and progress spinners."""
from __future__ import annotations

import sys
import threading
import time
from typing import Any

from .alignment import is_wc_pair


def configure_terminal():
    """Configure terminal standard streams for UTF-8 encoding."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


class Spinner:
    """Threaded progress spinner for terminal operations."""

    def __init__(self, message: str):
        self.message = message
        self.stop_event = threading.Event()
        self.thread = None

    def __enter__(self):
        if sys.stderr.isatty():
            def animate():
                frames = "|/-\\"
                idx = 0
                while not self.stop_event.is_set():
                    sys.stderr.write(f"\r{frames[idx % len(frames)]} {self.message}")
                    sys.stderr.flush()
                    idx += 1
                    time.sleep(0.1)
            self.thread = threading.Thread(target=animate, daemon=True)
            self.thread.start()
        else:
            print(self.message)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=0.3)
            sys.stderr.write("\r" + " " * (len(self.message) + 4) + "\r")
            sys.stderr.flush()


def print_progress(current: int, total: int, message: str):
    """Render terminal progress bar."""
    percent = 100 if total == 0 else int(100 * current / total)
    width = 28
    done = int(width * percent / 100)
    bar = f"[{'#' * done}{'-' * (width - done)}] {percent:3d}%  {message}"
    print(bar)


def colorize_alignment_line(line: str) -> str:
    """Apply ANSI colors to Watson-Crick and gap characters."""
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    GREEN = "\033[92m"
    DIM = "\033[90m"
    RESET = "\033[0m"

    out = []
    for c in line:
        if c in "ATat":
            out.append(f"{CYAN}{c}{RESET}")
        elif c in "GCgc":
            out.append(f"{MAGENTA}{c}{RESET}")
        elif c == "|":
            out.append(f"{GREEN}|{RESET}")
        elif c == ".":
            out.append(f"{DIM}.{RESET}")
        else:
            out.append(c)
    return "".join(out)


def interactive_terminal_inspect(
    sequence: str,
    shanes: list[dict[str, Any]],
    chrom: str,
):
    """Interactive colored terminal inspection for discovered SHaNE candidates."""
    configure_terminal()
    print(f"\n==================================================")
    print(f" Interactive Inspection: {chrom} ({len(shanes)} SHaNEs)")
    print(f"==================================================")

    if not shanes:
        print("No SHaNEs discovered on this sequence.")
        return

    for idx, s in enumerate(shanes, 1):
        name = s.get("systematic_name") or f"SHaNE_{chrom}.{idx}"
        print(f"\n[{idx}/{len(shanes)}] {name}: {s['start']:,} - {s['end']:,} bp (Length: {s['end']-s['start']:,} bp, Islands: {len(s.get('islands', []))}, Score: {s.get('score', 0):.2f})")
        details = s.get("details", {})
        aln = details.get("folded_alignment") or ""
        if aln:
            print("\nFolded Watson-Crick Alignment:")
            for line in aln.splitlines()[:15]:
                print("  " + colorize_alignment_line(line))
            if len(aln.splitlines()) > 15:
                print(f"  ... ({len(aln.splitlines()) - 15} more lines)")
        genes = s.get("genes", [])
        if genes:
            print(f"  Superimposed Genes ({len(genes)}): " + ", ".join(f"{g.get('symbol','.')} ({g.get('relationship','overlap')})" for g in genes))
