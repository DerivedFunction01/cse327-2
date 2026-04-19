#!/usr/bin/env python3
"""Compare standard and learned reasoner CSV outputs.

This script reads the `std` and `ming` CSV files produced by evaluate.py,
matches rows by query number, and reports which reasoner explored fewer nodes.
It also saves a simple comparison plot.
"""

from __future__ import annotations

import argparse
import csv
import os
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


@dataclass(frozen=True)
class QueryResult:
    query: int
    nodes: int
    success: bool
    time: float


def _find_column(fieldnames: list[str], needle: str) -> str:
    matches = [name for name in fieldnames if needle in name]
    if not matches:
        raise ValueError(f"Could not find a column containing {needle!r}")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous columns for {needle!r}: {matches}")
    return matches[0]


def load_results(path: Path) -> list[QueryResult]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"No CSV header found in {path}")

        query_col = _find_column(reader.fieldnames, "query")
        nodes_col = _find_column(reader.fieldnames, "nodes explored")
        success_col = _find_column(reader.fieldnames, "success")
        time_col = _find_column(reader.fieldnames, "time")

        results: list[QueryResult] = []
        for row in reader:
            results.append(
                QueryResult(
                    query=int(row[query_col]),
                    nodes=int(row[nodes_col]),
                    success=row[success_col].strip().lower() == "true",
                    time=float(row[time_col]),
                )
            )
    return results


def summarize(std: list[QueryResult], ming: list[QueryResult]) -> dict[str, float]:
    std_by_query = {row.query: row for row in std}
    ming_by_query = {row.query: row for row in ming}
    common_queries = sorted(set(std_by_query) & set(ming_by_query))
    if not common_queries:
        raise ValueError("No overlapping query ids between the two CSV files")

    std_nodes = []
    ming_nodes = []
    std_times = []
    ming_times = []
    std_wins = 0
    ming_wins = 0
    ties = 0
    both_success = 0
    std_success_only = 0
    ming_success_only = 0
    both_fail = 0

    for q in common_queries:
        std_row = std_by_query[q]
        ming_row = ming_by_query[q]
        std_nodes.append(std_row.nodes)
        ming_nodes.append(ming_row.nodes)
        std_times.append(std_row.time)
        ming_times.append(ming_row.time)

        if std_row.nodes < ming_row.nodes:
            std_wins += 1
        elif ming_row.nodes < std_row.nodes:
            ming_wins += 1
        else:
            ties += 1

        if std_row.success and ming_row.success:
            both_success += 1
        elif std_row.success and not ming_row.success:
            std_success_only += 1
        elif ming_row.success and not std_row.success:
            ming_success_only += 1
        else:
            both_fail += 1

    return {
        "queries": float(len(common_queries)),
        "std_mean_nodes": mean(std_nodes),
        "std_median_nodes": median(std_nodes),
        "ming_mean_nodes": mean(ming_nodes),
        "ming_median_nodes": median(ming_nodes),
        "std_total_time": sum(std_times),
        "ming_total_time": sum(ming_times),
        "std_wins": float(std_wins),
        "ming_wins": float(ming_wins),
        "ties": float(ties),
        "both_success": float(both_success),
        "std_success_only": float(std_success_only),
        "ming_success_only": float(ming_success_only),
        "both_fail": float(both_fail),
        "mean_node_delta_std_minus_ming": mean([s - m for s, m in zip(std_nodes, ming_nodes)]),
        "total_time_delta_std_minus_ming": sum(std_times) - sum(ming_times),
    }


def make_plot(std: list[QueryResult], ming: list[QueryResult], output_path: Path) -> None:
    std_by_query = {row.query: row for row in std}
    ming_by_query = {row.query: row for row in ming}
    common_queries = sorted(set(std_by_query) & set(ming_by_query))

    std_nodes = [std_by_query[q].nodes for q in common_queries]
    ming_nodes = [ming_by_query[q].nodes for q in common_queries]

    plt.figure(figsize=(10, 6))
    plt.boxplot(
        [std_nodes, ming_nodes],
        tick_labels=["std", "ming"],
        showfliers=True,
        whis=(5, 95),
    )
    plt.yscale("log")
    plt.ylabel("Nodes explored (log scale)")
    plt.title("Reasoner node exploration distribution")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare std and ming reasoner CSVs.")
    parser.add_argument("--std", required=True, type=Path, help="Path to std CSV file")
    parser.add_argument("--ming", required=True, type=Path, help="Path to ming CSV file")
    parser.add_argument(
        "--plot",
        type=Path,
        default=Path("reasoner_comparison.png"),
        help="Output path for the comparison plot",
    )
    args = parser.parse_args()

    std = load_results(args.std)
    ming = load_results(args.ming)
    summary = summarize(std, ming)
    make_plot(std, ming, args.plot)

    print("Reasoner comparison")
    print(f"  std file:  {args.std}")
    print(f"  ming file: {args.ming}")
    print(f"  plot:      {args.plot}")
    print()
    print(f"Queries compared: {int(summary['queries'])}")
    print(f"std mean nodes:   {summary['std_mean_nodes']:.2f}")
    print(f"std median nodes: {summary['std_median_nodes']:.2f}")
    print(f"std total time:   {summary['std_total_time']:.2f}")
    print(f"ming mean nodes:  {summary['ming_mean_nodes']:.2f}")
    print(f"ming median nodes:{summary['ming_median_nodes']:.2f}")
    print(f"ming total time:  {summary['ming_total_time']:.2f}")
    print()
    print(f"std wins:         {int(summary['std_wins'])}")
    print(f"ming wins:        {int(summary['ming_wins'])}")
    print(f"ties:             {int(summary['ties'])}")
    print()
    print(f"both success:     {int(summary['both_success'])}")
    print(f"std only success: {int(summary['std_success_only'])}")
    print(f"ming only success:{int(summary['ming_success_only'])}")
    print(f"both fail:        {int(summary['both_fail'])}")
    print()
    print(f"mean(std - ming) nodes: {summary['mean_node_delta_std_minus_ming']:.2f}")
    print(
        f"total(std - ming) time: {summary['total_time_delta_std_minus_ming']:.2f}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
