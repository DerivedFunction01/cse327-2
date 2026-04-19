#!/usr/bin/env python3
"""Compact terminal dashboard for training/evaluation log files.

This watches the `logs/` directory in the repo root, shows one summary line
per `screen` log file, and trims oversized logs so progress bars do not grow
the files forever.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from pathlib import Path


LOG_RE = re.compile(
    r"^c327-(?P<kb>countries|size200|size300|size400)-(?P<variant>default|embed|mod)(?P<eval>-eval)?$"
)


@dataclass(frozen=True)
class LogEntry:
    path: Path
    session: str
    kb: str
    variant: str
    is_eval: bool


WAIT_RE = re.compile(r"Waiting for files:|Waiting for comparison pairs:|Waiting for expected files")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Live dashboard for log files.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repo root containing logs/. Default: parent of scripts/.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Seconds between refreshes. Default: 5.",
    )
    parser.add_argument(
        "--tail",
        type=int,
        default=1,
        help="How many trailing lines to use for the status excerpt. Default: 1.",
    )
    parser.add_argument(
        "--max-log-bytes",
        type=int,
        default=1_000_000,
        help="Trim logs down to this many trailing bytes when they exceed the limit. Default: 1,000,000.",
    )
    parser.add_argument(
        "--show-eval",
        action="store_true",
        help="Also show evaluation logs. Enabled by default.",
    )
    parser.add_argument(
        "--hide-eval",
        action="store_true",
        help="Hide evaluation logs and show only training logs.",
    )
    return parser.parse_args()


def clear_screen() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def read_tail(path: Path, limit: int) -> list[str]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.read().replace("\r", "\n").splitlines()
            return lines[-limit:]
    except FileNotFoundError:
        return []


def trim_log(path: Path, max_bytes: int) -> int:
    if max_bytes <= 0 or not path.exists():
        return 0

    size = path.stat().st_size
    if size <= max_bytes:
        return size

    with path.open("rb") as f:
        f.seek(-max_bytes, 2)
        data = f.read()

    nl = data.find(b"\n")
    if nl != -1 and nl + 1 < len(data):
        data = data[nl + 1 :]

    with NamedTemporaryFile("wb", delete=False, dir=str(path.parent)) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)

    tmp_path.replace(path)
    return len(data)


def screen_sessions() -> set[str]:
    try:
        result = subprocess.run(
            ["screen", "-ls"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return set()

    sessions: set[str] = set()
    for line in (result.stdout or "").splitlines():
        match = re.search(r"\s+\d+\.(?P<name>[^\s]+)\s+\(", line)
        if match:
            sessions.add(match.group("name"))
    return sessions


def discover_logs(root: Path, include_eval: bool) -> list[LogEntry]:
    logs_dir = root / "logs"
    if not logs_dir.exists():
        return []

    entries: list[LogEntry] = []
    for path in sorted(logs_dir.glob("c327-*.log")):
        stem = path.stem
        match = LOG_RE.match(stem)
        if not match:
            continue
        is_eval = bool(match.group("eval"))
        if is_eval and not include_eval:
            continue
        entries.append(
            LogEntry(
                path=path,
                session=stem,
                kb=match.group("kb"),
                variant=match.group("variant"),
                is_eval=is_eval,
            )
        )
    return entries


def fmt_age(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    if seconds < 3600:
        return f"{int(seconds // 60)}m"
    return f"{int(seconds // 3600)}h"


def last_meaningful_line(lines: list[str]) -> str:
    for line in reversed(lines):
        cleaned = line.replace("\x1b", "").strip()
        if cleaned:
            return cleaned
    return ""


def classify_status(entry: LogEntry, active: set[str], line: str) -> str:
    if entry.session not in active:
        return "done"
    if WAIT_RE.search(line):
        return "WAIT"
    return "RUN"


def render(root: Path, tail: int, include_eval: bool, max_log_bytes: int) -> None:
    entries = discover_logs(root, include_eval=include_eval)
    active = screen_sessions()
    now = time.time()

    clear_screen()
    print(f"Log Dashboard - {root}")
    print(f"Refresh: {time.strftime('%Y-%m-%d %H:%M:%S')}  tail={tail}  max_log_bytes={max_log_bytes}")
    print(f"Active screen sessions detected: {len(active)}")
    print()

    if not entries:
        print("No log files found yet in logs/.")
        return

    header = f"{'status':<6} {'job':<30} {'age':>6} {'size':>9}  line"
    print(header)
    print("-" * len(header))

    for entry in entries:
        stat = entry.path.stat() if entry.path.exists() else None
        age = fmt_age(now - stat.st_mtime) if stat else "n/a"
        running = "RUN" if entry.session in active else "done"
        size = stat.st_size if stat else 0
        if size > max_log_bytes:
            size = trim_log(entry.path, max_log_bytes)
            stat = entry.path.stat() if entry.path.exists() else None
            age = fmt_age(now - stat.st_mtime) if stat else "n/a"

        lines = read_tail(entry.path, tail)
        line = last_meaningful_line(lines) or "<no content yet>"
        line = line.replace("\t", " ").replace("\r", " ")
        if len(line) > 110:
            line = line[:107] + "..."
        status = classify_status(entry, active, line)
        print(f"{status:<6} {entry.session:<30} {age:>6} {size:>9}  {line}")


def main() -> int:
    args = parse_args()
    include_eval = True
    if args.hide_eval:
        include_eval = False
    root = args.root.resolve()

    if not os.environ.get("TERM"):
        os.environ["TERM"] = "xterm"

    try:
        while True:
            render(root, args.tail, include_eval=include_eval, max_log_bytes=args.max_log_bytes)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
