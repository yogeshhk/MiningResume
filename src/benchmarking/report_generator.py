"""
Report generator.

Reads results/raw_results.json produced by benchmark_runner.py
and writes:
  - results/report.csv   — flat table, one row per parser × file
  - results/report.html  — colour-coded HTML table with per-parser summary

Usage:
    python report_generator.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from collections import defaultdict

_THIS_DIR = Path(__file__).parent
_REPO_ROOT = _THIS_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

RESULTS_DIR = _THIS_DIR / "results"

# Columns that appear in the detail table (order matters for readability)
DETAIL_COLS = [
    "parser", "file", "format", "success",
    "parse_time_s", "peak_memory_mb",
    "word_count", "char_count",
    "heading_count", "table_row_count", "blank_line_ratio", "avg_line_length",
    "rouge1_recall", "rouge1_precision", "rouge1_f1",
    "email_detected", "email_count", "phone_detected", "phone_count",
    "url_count", "section_count", "section_coverage", "sections_detected",
    "error",
]

# Numeric columns used for the heatmap (higher = better)
HEATMAP_COLS = {
    "word_count", "heading_count", "section_count",
    "section_coverage", "rouge1_recall", "rouge1_f1",
}
# Lower = better for these
LOWER_BETTER = {"parse_time_s", "peak_memory_mb", "blank_line_ratio"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_records() -> list[dict]:
    raw = RESULTS_DIR / "raw_results.json"
    if not raw.exists():
        print(f"ERROR: {raw} not found. Run benchmark_runner.py first.")
        sys.exit(1)
    with open(raw, encoding="utf-8") as fh:
        return json.load(fh)


def _safe(val) -> str:
    if val is None:
        return ""
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val)


def _colour(col: str, val, col_min: float, col_max: float) -> str:
    """Return a green-to-red background colour based on relative value."""
    if val is None or col_max == col_min:
        return "#f5f5f5"
    try:
        fval = float(val)
    except (TypeError, ValueError):
        return "#f5f5f5"

    ratio = (fval - col_min) / (col_max - col_min)  # 0 (bad) -> 1 (good)
    if col in LOWER_BETTER:
        ratio = 1 - ratio

    r = int(255 * (1 - ratio))
    g = int(200 * ratio)
    return f"rgb({r},{g},100)"


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def write_csv(records: list[dict]):
    out = RESULTS_DIR / "report.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=DETAIL_COLS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"CSV saved -> {out}")


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Resume Parser Benchmark Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; font-size: 13px; margin: 20px; }}
    h1   {{ color: #333; }}
    h2   {{ color: #555; margin-top: 30px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
    th    {{ background: #2c3e50; color: white; padding: 6px 8px; text-align: left; font-size: 12px; }}
    td    {{ padding: 5px 8px; border: 1px solid #ddd; white-space: nowrap; }}
    tr:hover td {{ filter: brightness(0.92); }}
    .success-true  {{ color: green; font-weight: bold; }}
    .success-false {{ color: red;   font-weight: bold; }}
    .na {{ color: #aaa; }}
  </style>
</head>
<body>
<h1>Resume Parser Benchmark Report</h1>
<p>Generated: {timestamp}</p>

<h2>Summary — per parser</h2>
{summary_table}

<h2>Detail — per file × parser</h2>
{detail_table}
</body>
</html>
"""


def _build_summary(records: list[dict]) -> str:
    buckets: dict[str, list] = defaultdict(list)
    for r in records:
        buckets[r["parser"]].append(r)

    summary_cols = [
        "Parser", "Files", "Success", "Rate",
        "Avg Time (s)", "Avg Mem (MB)",
        "Avg Words", "Avg Sections", "Avg Section Coverage",
        "Avg ROUGE-1 F1",
    ]

    rows_html = ""
    for parser, runs in sorted(buckets.items()):
        ok = [r for r in runs if r["success"]]
        n = len(runs)
        k = len(ok)

        def avg(col):
            vals = [r[col] for r in ok if r.get(col) is not None and r[col] != ""]
            return round(sum(float(v) for v in vals) / len(vals), 4) if vals else None

        cells = [
            parser, n, k,
            f"{k/n:.0%}" if n else "0%",
            _safe(avg("parse_time_s")),
            _safe(avg("peak_memory_mb")),
            _safe(avg("word_count")),
            _safe(avg("section_count")),
            _safe(avg("section_coverage")),
            _safe(avg("rouge1_f1")),
        ]
        rows_html += "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>\n"

    header = "".join(f"<th>{c}</th>" for c in summary_cols)
    return f"<table><thead><tr>{header}</tr></thead><tbody>{rows_html}</tbody></table>"


def _build_detail(records: list[dict]) -> str:
    # Pre-compute column min/max for heatmap columns
    col_stats: dict[str, tuple] = {}
    for col in HEATMAP_COLS | LOWER_BETTER:
        vals = [float(r[col]) for r in records if r.get(col) not in (None, "", False, True)]
        col_stats[col] = (min(vals, default=0), max(vals, default=1))

    display_cols = [c for c in DETAIL_COLS if c not in ("error",)] + ["error"]
    header = "".join(f"<th>{c}</th>" for c in display_cols)

    rows_html = ""
    for r in records:
        cells = ""
        for col in display_cols:
            val = r.get(col)
            raw = _safe(val)

            if col == "success":
                cls = "success-true" if val else "success-false"
                cells += f'<td class="{cls}">{raw}</td>'
            elif col in HEATMAP_COLS | LOWER_BETTER and raw:
                cmin, cmax = col_stats.get(col, (0, 1))
                bg = _colour(col, val, cmin, cmax)
                cells += f'<td style="background:{bg}">{raw}</td>'
            elif raw == "":
                cells += '<td class="na">—</td>'
            else:
                cells += f"<td>{raw}</td>"

        rows_html += f"<tr>{cells}</tr>\n"

    return (
        f"<table><thead><tr>{header}</tr></thead>"
        f"<tbody>{rows_html}</tbody></table>"
    )


def generate_html(records: list[dict]):
    from datetime import datetime
    html = _HTML_TEMPLATE.format(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        summary_table=_build_summary(records),
        detail_table=_build_detail(records),
    )
    out = RESULTS_DIR / "report.html"
    out.write_text(html, encoding="utf-8")
    print(f"HTML saved -> {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    records = _load_records()
    print(f"Loaded {len(records)} records from raw_results.json")
    write_csv(records)
    generate_html(records)


if __name__ == "__main__":
    main()
