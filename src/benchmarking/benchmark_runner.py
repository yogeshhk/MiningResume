"""
Benchmark runner — entry point.

Usage:
    cd src/benchmarking
    python benchmark_runner.py

    # or from repo root
    python -m src.benchmarking.benchmark_runner

Iterates over every file in data/ × every loaded parser.
Results are written to src/benchmarking/results/raw_results.json.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

# Allow running directly from the benchmarking folder or from repo root
_THIS_DIR = Path(__file__).parent
_REPO_ROOT = _THIS_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.benchmarking.parsers import get_all_parsers
from src.benchmarking.metrics.text_metrics import compute_text_metrics
from src.benchmarking.metrics.field_metrics import compute_field_metrics
from src.benchmarking.metrics.perf_metrics import summarise_perf

DATA_DIR = _REPO_ROOT / "data"
RESULTS_DIR = _THIS_DIR / "results"

# File extensions to include in the benchmark run
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# TXT files treated purely as reference corpus (not parsed themselves)
REFERENCE_ONLY_STEMS = {"resume", "resume1", "resume2"}


def _load_reference(stem: str) -> str:
    """Return content of <stem>.txt from DATA_DIR, or '' if not found."""
    txt_path = DATA_DIR / f"{stem}.txt"
    if txt_path.exists():
        return txt_path.read_text(encoding="utf-8", errors="replace")
    return ""


def _collect_files() -> list[Path]:
    """Return all benchmark target files (excludes pure-reference TXT files)."""
    files = []
    for f in sorted(DATA_DIR.iterdir()):
        if f.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        # Skip .txt files that are reference-only (avoid parsing plain text)
        if f.suffix.lower() == ".txt" and f.stem in REFERENCE_ONLY_STEMS:
            continue
        files.append(f)
    return files


def run_benchmark() -> list[dict]:
    print("\n=== Loading parsers ===")
    parsers = get_all_parsers()
    if not parsers:
        print("No parsers loaded — install at least one dependency.")
        return []

    files = _collect_files()
    print(f"\n=== Found {len(files)} benchmark files in {DATA_DIR} ===\n")

    records: list[dict] = []

    for file_path in files:
        ref_text = _load_reference(file_path.stem)

        for parser in parsers:
            if not parser.supports(file_path):
                continue

            label = f"[{parser.name:15s}] {file_path.name}"
            print(f"  Parsing {label} ...", end=" ", flush=True)
            result = parser.parse(file_path)

            if result.success:
                text_m = compute_text_metrics(result.text, ref_text)
                field_m = compute_field_metrics(result.text)
                # Flatten sections list to a semicolon-separated string for JSON compat
                field_m["sections_detected"] = "; ".join(field_m["sections_detected"])
            else:
                text_m = {
                    "word_count": 0, "char_count": 0,
                    "heading_count": 0, "table_row_count": 0,
                    "blank_line_ratio": None, "avg_line_length": None,
                    "rouge1_recall": None, "rouge1_precision": None, "rouge1_f1": None,
                }
                field_m = {
                    "email_detected": False, "email_count": 0,
                    "phone_detected": False, "phone_count": 0,
                    "url_count": 0,
                    "sections_detected": "", "section_count": 0,
                    "section_coverage": 0.0,
                }

            record = {
                "parser": result.parser_name,
                "file": result.file_name,
                "format": result.file_format,
                "success": result.success,
                "error": result.error or "",
                "parse_time_s": result.parse_time_s,
                "peak_memory_mb": result.peak_memory_mb,
                **text_m,
                **field_m,
            }
            records.append(record)

            status = "OK" if result.success else f"FAIL ({result.error[:60]})"
            print(f"{status}  [{result.parse_time_s:.2f}s]")

    return records


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    started = datetime.now()
    print(f"Benchmark started at {started.isoformat()}")

    records = run_benchmark()

    # ── raw JSON ──────────────────────────────────────────────────────────
    raw_path = RESULTS_DIR / "raw_results.json"
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2, default=str)
    print(f"\nRaw results -> {raw_path}")

    # ── performance summary ───────────────────────────────────────────────
    if records:
        perf = summarise_perf(records)
        print("\n=== Performance Summary ===")
        header = f"{'Parser':<18} {'Files':>6} {'OK':>4} {'Rate':>6} {'AvgTime':>9} {'AvgMem':>9}"
        print(header)
        print("-" * len(header))
        for parser_name, s in perf.items():
            print(
                f"{parser_name:<18} {s['total_files']:>6} {s['success_count']:>4} "
                f"{s['success_rate']:>6.1%} "
                f"{(str(s['avg_time_s'])+'s') if s['avg_time_s'] is not None else 'N/A':>9} "
                f"{(str(s['avg_memory_mb'])+'MB') if s['avg_memory_mb'] is not None else 'N/A':>9}"
            )

    elapsed = (datetime.now() - started).total_seconds()
    print(f"\nTotal: {len(records)} runs in {elapsed:.1f}s")
    print("Run report_generator.py to produce CSV + HTML report.")
    return records


if __name__ == "__main__":
    main()
