"""
Performance metrics.

parse_time_s and peak_memory_mb are already captured inside BaseParser.parse().
This module provides helpers for summarising them across a result set.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..parsers.base_parser import ParseResult


def summarise_perf(results: list) -> dict:
    """
    Return per-parser average time and memory across all successful runs.

    Args:
        results: list of raw record dicts (as produced by benchmark_runner)

    Returns:
        dict keyed by parser name → {avg_time_s, avg_memory_mb, success_rate}
    """
    from collections import defaultdict

    buckets: dict[str, list] = defaultdict(list)
    for r in results:
        buckets[r["parser"]].append(r)

    summary = {}
    for parser, runs in buckets.items():
        total = len(runs)
        ok = [r for r in runs if r["success"]]
        summary[parser] = {
            "total_files": total,
            "success_count": len(ok),
            "success_rate": round(len(ok) / total, 4) if total else 0.0,
            "avg_time_s": round(
                sum(r["parse_time_s"] for r in ok) / len(ok), 4
            ) if ok else None,
            "avg_memory_mb": round(
                sum(r["peak_memory_mb"] for r in ok) / len(ok), 3
            ) if ok else None,
        }
    return summary
