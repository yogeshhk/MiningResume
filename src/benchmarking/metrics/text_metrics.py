"""
Text-quality metrics computed on the raw extracted string.

All functions accept a plain string and return scalars.
"""

import re


# ---------------------------------------------------------------------------
# Basic counts
# ---------------------------------------------------------------------------

def word_count(text: str) -> int:
    return len(text.split())


def char_count(text: str) -> int:
    return len(text)


# ---------------------------------------------------------------------------
# Layout / structure signals
# ---------------------------------------------------------------------------

def heading_count(text: str) -> int:
    """
    Count lines that look like headings:
      - Markdown headings  (#, ##, ###)
      - Short ALL-CAPS lines (3–8 words) — common in plain-text resumes
      - Bold markdown (**text**)
    """
    count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            count += 1
        elif re.match(r"^\*\*.+\*\*$", stripped):
            count += 1
        elif stripped.isupper() and 2 <= len(stripped.split()) <= 8:
            count += 1
    return count


def table_row_count(text: str) -> int:
    """Count lines that look like markdown table rows (| col | col |)."""
    return sum(
        1 for line in text.splitlines()
        if "|" in line and line.strip().startswith("|")
    )


def blank_line_ratio(text: str) -> float:
    """Fraction of lines that are blank.  Low → dense; high → well-spaced."""
    lines = text.splitlines()
    if not lines:
        return 0.0
    blank = sum(1 for ln in lines if not ln.strip())
    return round(blank / len(lines), 4)


def avg_line_length(text: str) -> float:
    """Average characters per non-blank line — proxy for layout continuity."""
    non_blank = [ln for ln in text.splitlines() if ln.strip()]
    if not non_blank:
        return 0.0
    return round(sum(len(ln) for ln in non_blank) / len(non_blank), 2)


# ---------------------------------------------------------------------------
# Reference-based metric (ROUGE-1 recall, no external library)
# ---------------------------------------------------------------------------

def rouge1_recall(hypothesis: str, reference: str) -> float:
    """
    Token-overlap ROUGE-1 recall against a reference text.
    recall = |hyp_tokens ∩ ref_tokens| / |ref_tokens|

    Uses a bag-of-words (multiset) approach to avoid inflating recall
    for repeated tokens.
    """
    ref_tokens = reference.lower().split()
    hyp_tokens = set(hypothesis.lower().split())
    if not ref_tokens:
        return 0.0
    hits = sum(1 for t in ref_tokens if t in hyp_tokens)
    return round(hits / len(ref_tokens), 4)


def rouge1_precision(hypothesis: str, reference: str) -> float:
    """
    Token-overlap ROUGE-1 precision.
    precision = |hyp_tokens ∩ ref_tokens| / |hyp_tokens|
    """
    ref_set = set(reference.lower().split())
    hyp_tokens = hypothesis.lower().split()
    if not hyp_tokens:
        return 0.0
    hits = sum(1 for t in hyp_tokens if t in ref_set)
    return round(hits / len(hyp_tokens), 4)


def rouge1_f1(hypothesis: str, reference: str) -> float:
    r = rouge1_recall(hypothesis, reference)
    p = rouge1_precision(hypothesis, reference)
    if r + p == 0:
        return 0.0
    return round(2 * r * p / (r + p), 4)


# ---------------------------------------------------------------------------
# Composite call
# ---------------------------------------------------------------------------

def compute_text_metrics(text: str, reference_text: str = "") -> dict:
    m: dict = {
        "word_count": word_count(text),
        "char_count": char_count(text),
        "heading_count": heading_count(text),
        "table_row_count": table_row_count(text),
        "blank_line_ratio": blank_line_ratio(text),
        "avg_line_length": avg_line_length(text),
    }
    if reference_text.strip():
        m["rouge1_recall"] = rouge1_recall(text, reference_text)
        m["rouge1_precision"] = rouge1_precision(text, reference_text)
        m["rouge1_f1"] = rouge1_f1(text, reference_text)
    else:
        m["rouge1_recall"] = None
        m["rouge1_precision"] = None
        m["rouge1_f1"] = None
    return m
