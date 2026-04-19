#!/usr/bin/env python3
"""Reconstruct evaluation console output from a saved CSV and query file.

This version intentionally avoids importing any project modules. It reads the
CSV plus the raw query text file and recreates the console-style output.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path


def _find_column(fieldnames: list[str], needle: str) -> str:
    matches = [name for name in fieldnames if needle in name]
    if not matches:
        raise ValueError(f"Could not find a column containing {needle!r}")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous columns for {needle!r}: {matches}")
    return matches[0]


def _load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"No CSV header found in {path}")
        return reader.fieldnames, list(reader)


def _load_queries(path: Path) -> list[str]:
    queries: list[str] = []
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%"):
            continue
        if line.endswith("."):
            line = line[:-1]
        queries.append(line)
    if not queries:
        raise ValueError(f"No queries found in {path}")
    return queries


def _format_time(seconds: float) -> str:
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


def replay_output(
    csv_path: Path,
    query_file: Path,
    reasoner_label: str | None,
    include_header: bool,
    device_label: str,
    embedding_model: str | None,
    scoring_model: str | None,
) -> str:
    fieldnames, rows = _load_csv(csv_path)
    queries = _load_queries(query_file)

    if len(rows) != len(queries):
        raise ValueError(
            f"CSV rows ({len(rows)}) and queries ({len(queries)}) do not match"
        )

    query_col = _find_column(fieldnames, "query")
    nodes_col = _find_column(fieldnames, "nodes explored")
    depth_col = _find_column(fieldnames, "min depth")
    success_col = _find_column(fieldnames, "success")
    time_col = _find_column(fieldnames, "time")
    reasoner_col = _find_column(fieldnames, "reasoner")

    if reasoner_label is None:
        reasoner_label = rows[0][reasoner_col].strip() if rows else "ming"

    lines: list[str] = []
    if include_header:
        lines.append(f"using {device_label} device")
        if reasoner_label == "std":
            lines.append("STANDARD")
        else:
            lines.append(f"UNITY: {reasoner_label}")
            if embedding_model:
                lines.append(f"\tEmbedding Model: {embedding_model}")
            if scoring_model:
                lines.append(f"\tScoring Model: {scoring_model}")
        lines.append("")

    fail_count = 0
    total_time = 0.0
    node_total = 0

    for idx, (query, row) in enumerate(zip(queries, rows), start=1):
        nodes = int(row[nodes_col])
        depth = int(row[depth_col])
        success = row[success_col].strip().lower() == "true"
        elapsed = float(row[time_col])

        if not success:
            fail_count += 1
        node_total += nodes
        total_time += elapsed

        lines.append(f"Query {idx}: [{query}]")
        if not success:
            lines.append("Query failed!!!")
        lines.append(
            f"{nodes} :: {depth} - {_format_time(elapsed)} "
            f"({int(nodes / elapsed) if elapsed > 0 else '-'} nps)"
        )
        lines.append("")

    avg_nodes = node_total / len(rows) if rows else 0.0
    lines.append(f"{reasoner_label}: {avg_nodes} nodes/query")
    if fail_count > 0:
        lines.append(f"{fail_count} queries failed")
    lines.append(f"Time to run all queries: {total_time}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconstruct evaluation console output from a CSV."
    )
    parser.add_argument("--csv", required=True, type=Path, help="Path to the eval CSV")
    parser.add_argument(
        "--qfile",
        required=True,
        type=Path,
        help="Path to the plain query file used for the evaluation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write the reconstructed output to this file instead of stdout.",
    )
    parser.add_argument(
        "--reasoner-label",
        default=None,
        help="Override the reasoner label used in the replay header and summary.",
    )
    parser.add_argument(
        "--device-label",
        default="cuda",
        help="Device label to show in the replay header. Default: cuda",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Skip the header lines and print only per-query output.",
    )
    parser.add_argument(
        "--embedding-model",
        default=None,
        help="Optional embedding model path to echo in the replay header.",
    )
    parser.add_argument(
        "--scoring-model",
        default=None,
        help="Optional scoring model path to echo in the replay header.",
    )
    args = parser.parse_args()

    text = replay_output(
        csv_path=args.csv,
        query_file=args.qfile,
        reasoner_label=args.reasoner_label,
        include_header=not args.no_header,
        device_label=args.device_label,
        embedding_model=args.embedding_model,
        scoring_model=args.scoring_model,
    )

    if args.output is None:
        sys.stdout.write(text)
    else:
        args.output.write_text(text)
        print(f"Wrote replay output to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
