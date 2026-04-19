#!/usr/bin/env python3
"""Run reasoner comparisons across all experiment folders.

This script understands the redo layout:
  <kb>/default/std-*.csv
  <kb>/<variant>/ming-*.csv

It compares each variant's learned reasoner output against the KB's default
baseline standard-reasoner CSV, saves a plot next to the learned CSV, and
writes a summary table for all comparisons.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

from compare_reasoners import load_results, make_plot, summarize


@dataclass(frozen=True)
class ComparisonPair:
    baseline_std_path: Path
    ming_path: Path

    @property
    def suffix(self) -> str:
        return self.ming_path.stem.removeprefix("ming-")

    @property
    def plot_path(self) -> Path:
        return self.ming_path.with_name(f"reasoner_comparison-vs-default-{self.suffix}.png")

    @property
    def report_path(self) -> Path:
        return self.ming_path.with_name(f"reasoner_comparison-vs-default-{self.suffix}.txt")

    @property
    def size_tag(self) -> str:
        parts = self.baseline_std_path.stem.split("-")
        if len(parts) < 2:
            return "unknown"
        return parts[-1]

    @property
    def kb_name(self) -> str:
        return self.ming_path.parent.parent.name

    @property
    def variant(self) -> str:
        return self.ming_path.parent.name

    @property
    def embed_size(self) -> str:
        stem = self.ming_path.stem
        parts = stem.split("-")
        if len(parts) >= 2:
            return parts[-1]
        return "unknown"


@dataclass(frozen=True)
class ComparisonTarget:
    kb_root: Path
    variant_dir: Path
    baseline_std_path: Path | None
    ming_path: Path | None

    @property
    def kb_name(self) -> str:
        return self.kb_root.name

    @property
    def variant(self) -> str:
        return self.variant_dir.name

    @property
    def ready(self) -> bool:
        return self.baseline_std_path is not None and self.ming_path is not None


def _is_hidden_path(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return any(part.startswith(".") for part in parts)


def _find_baseline_std(kb_root: Path) -> Path | None:
    default_dir = kb_root / "default"
    if not default_dir.exists():
        return None

    exact = sorted(default_dir.glob("std-*-50.csv"))
    if exact:
        return exact[0]

    fallback = sorted(default_dir.glob("std-*.csv"))
    if fallback:
        return fallback[0]

    return None


def _find_variant_ming(variant_dir: Path) -> Path | None:
    matches = sorted(variant_dir.glob("ming-*.csv"))
    if matches:
        return matches[0]
    return None


def _find_variant_mings(variant_dir: Path) -> list[Path]:
    return sorted(variant_dir.glob("ming-*.csv"))


def _iter_kb_roots(root: Path) -> list[Path]:
    kb_roots: list[Path] = []
    for path in sorted(root.iterdir()):
        if not path.is_dir():
            continue
        if path.name.startswith("."):
            continue
        default_dir = path / "default"
        if default_dir.is_dir():
            kb_roots.append(path)
    return kb_roots


def find_targets(root: Path) -> list[ComparisonTarget]:
    targets: list[ComparisonTarget] = []
    for kb_root in _iter_kb_roots(root):
        baseline_std = _find_baseline_std(kb_root)
        for variant in ("default", "embed", "mod"):
            variant_dir = kb_root / variant
            if not variant_dir.is_dir():
                continue
            ming_paths = _find_variant_mings(variant_dir)
            if ming_paths:
                for ming_path in ming_paths:
                    targets.append(
                        ComparisonTarget(
                            kb_root=kb_root,
                            variant_dir=variant_dir,
                            baseline_std_path=baseline_std,
                            ming_path=ming_path,
                        )
                    )
            else:
                targets.append(
                    ComparisonTarget(
                        kb_root=kb_root,
                        variant_dir=variant_dir,
                        baseline_std_path=baseline_std,
                        ming_path=None,
                    )
                )
    return targets


def find_pairs(root: Path) -> list[ComparisonPair]:
    pairs: list[ComparisonPair] = []
    for target in find_targets(root):
        if target.ready:
            assert target.baseline_std_path is not None
            assert target.ming_path is not None
            pairs.append(
                ComparisonPair(
                    baseline_std_path=target.baseline_std_path,
                    ming_path=target.ming_path,
                )
            )
    return pairs


def write_summary(summary_rows: Iterable[dict[str, object]], output_path: Path) -> None:
    rows = list(summary_rows)
    if not rows:
        return

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(
    pair: ComparisonPair,
    summary: dict[str, float],
    output_path: Path,
    root: Path,
) -> None:
    text = (
        "Reasoner comparison\n"
        f"  baseline std file: {pair.baseline_std_path.relative_to(root)}\n"
        f"  ming file: {pair.ming_path.relative_to(root)}\n"
        f"  plot:      {pair.plot_path.relative_to(root)}\n"
        f"  txt file:   {pair.report_path.relative_to(root)}\n"
        "\n"
        f"Queries compared: {int(summary['queries'])}\n"
        f"std mean nodes:   {summary['std_mean_nodes']:.2f}\n"
        f"std median nodes: {summary['std_median_nodes']:.2f}\n"
        f"std total time:   {summary['std_total_time']:.2f}\n"
        f"ming mean nodes:  {summary['ming_mean_nodes']:.2f}\n"
        f"ming median nodes: {summary['ming_median_nodes']:.2f}\n"
        f"ming total time:  {summary['ming_total_time']:.2f}\n"
        "\n"
        f"std wins:         {int(summary['std_wins'])}\n"
        f"ming wins:        {int(summary['ming_wins'])}\n"
        f"ties:             {int(summary['ties'])}\n"
        "\n"
        f"both success:     {int(summary['both_success'])}\n"
        f"std only success: {int(summary['std_success_only'])}\n"
        f"ming only success: {int(summary['ming_success_only'])}\n"
        f"both fail:        {int(summary['both_fail'])}\n"
        "\n"
        f"mean(std - ming) nodes: {summary['mean_node_delta_std_minus_ming']:.2f}\n"
        f"total(std - ming) time:  {summary['total_time_delta_std_minus_ming']:.2f}\n"
    )
    output_path.write_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare every std/ming CSV pair under the current directory."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Directory to scan recursively. Default: current directory.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("reasoner_comparison_summary.csv"),
        help="Output CSV file for the combined summary.",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait until every std CSV has a matching ming CSV before comparing.",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=30,
        help="Seconds between wait checks when --wait is set. Default: 30.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=0,
        help="Maximum seconds to wait when --wait is set. Default: 0 (no timeout).",
    )
    args = parser.parse_args()

    root = args.root.resolve()

    if args.wait:
        start_ts = None
        while True:
            targets = find_targets(root)
            ready_targets = [target for target in targets if target.ready]
            missing_items: list[str] = []
            for target in targets:
                if target.baseline_std_path is None:
                    missing_items.append(f"{target.kb_name}/default: std")
                if target.ming_path is None:
                    missing_items.append(f"{target.kb_name}/{target.variant}: ming")

            if targets and len(ready_targets) == len(targets):
                break
            if start_ts is None:
                start_ts = time.time()
            elif args.timeout > 0 and time.time() - start_ts >= args.timeout:
                print(
                    f"Timed out waiting for comparison files under {root}",
                    file=sys.stderr,
                )
                return 1
            print(
                f"Waiting for comparison files: {len(ready_targets)}/{len(targets)} ready under {root}"
            )
            if missing_items:
                preview = ", ".join(missing_items[:8])
                if len(missing_items) > 8:
                    preview += ", ..."
                print(f"  missing: {preview}")
            time.sleep(args.poll_interval)
        pairs = find_pairs(root)
    else:
        pairs = find_pairs(root)
        if not pairs:
            print(f"No comparison pairs found under {root}")
            return 1

    summary_rows: list[dict[str, object]] = []
    for pair in tqdm(pairs, desc="Comparing reasoners", unit="pair"):
        std = load_results(pair.baseline_std_path)
        ming = load_results(pair.ming_path)
        summary = summarize(std, ming)
        make_plot(std, ming, pair.plot_path)

        row: dict[str, object] = {
            "kb": pair.kb_name,
            "variant": pair.variant,
            "embed_size": pair.embed_size if pair.variant == "embed" else "",
            "baseline_std_file": str(pair.baseline_std_path.relative_to(root)),
            "ming_file": str(pair.ming_path.relative_to(root)),
            "plot_file": str(pair.plot_path.relative_to(root)),
            "report_file": str(pair.report_path.relative_to(root)),
            "queries": int(summary["queries"]),
            "std_mean_nodes": f"{summary['std_mean_nodes']:.2f}",
            "std_median_nodes": f"{summary['std_median_nodes']:.2f}",
            "std_total_time": f"{summary['std_total_time']:.2f}",
            "ming_mean_nodes": f"{summary['ming_mean_nodes']:.2f}",
            "ming_median_nodes": f"{summary['ming_median_nodes']:.2f}",
            "ming_total_time": f"{summary['ming_total_time']:.2f}",
            "std_wins": int(summary["std_wins"]),
            "ming_wins": int(summary["ming_wins"]),
            "ties": int(summary["ties"]),
            "both_success": int(summary["both_success"]),
            "std_only_success": int(summary["std_success_only"]),
            "ming_only_success": int(summary["ming_success_only"]),
            "both_fail": int(summary["both_fail"]),
            "mean_node_delta_std_minus_ming": f"{summary['mean_node_delta_std_minus_ming']:.2f}",
            "total_time_delta_std_minus_ming": f"{summary['total_time_delta_std_minus_ming']:.2f}",
        }
        summary_rows.append(row)
        write_report(pair, summary, pair.report_path, root)

        print(
            f"{pair.kb_name}/{pair.variant}: "
            f"size={pair.size_tag}, "
            f"embed={pair.embed_size if pair.variant == 'embed' else '-'}, "
            f"std mean={summary['std_mean_nodes']:.2f}, "
            f"ming mean={summary['ming_mean_nodes']:.2f}, "
            f"std time={summary['std_total_time']:.2f}, "
            f"ming time={summary['ming_total_time']:.2f}, "
            f"plot={pair.plot_path.name}, "
            f"txt={pair.report_path.name}"
        )

    summary_path = args.summary
    if not summary_path.is_absolute():
        summary_path = root / summary_path
    write_summary(summary_rows, summary_path)
    print(f"\nWrote summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
