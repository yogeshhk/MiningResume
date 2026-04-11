"""
Field-detection metrics.

Checks how many resume-specific fields and section headers a parser
successfully surfaced in its output text.
"""

import re


# Common resume section keywords
SECTIONS = [
    "skills",
    "experience",
    "education",
    "employment",
    "work history",
    "work experience",
    "accomplishments",
    "achievements",
    "projects",
    "certifications",
    "summary",
    "objective",
    "profile",
    "publications",
    "awards",
    "languages",
    "interests",
    "volunteer",
    "references",
    "contact",
]

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s\-(). ]{7,15}")
URL_RE = re.compile(r"https?://[^\s]+|linkedin\.com/[^\s]+|github\.com/[^\s]+")


def detect_emails(text: str) -> list:
    return EMAIL_RE.findall(text)


def detect_phones(text: str) -> list:
    return PHONE_RE.findall(text)


def detect_urls(text: str) -> list:
    return URL_RE.findall(text)


def detect_sections(text: str) -> list:
    lower = text.lower()
    return [s for s in SECTIONS if re.search(rf"\b{re.escape(s)}\b", lower)]


def compute_field_metrics(text: str) -> dict:
    emails = detect_emails(text)
    phones = detect_phones(text)
    urls = detect_urls(text)
    sections = detect_sections(text)

    return {
        "email_detected": bool(emails),
        "email_count": len(emails),
        "phone_detected": bool(phones),
        "phone_count": len(phones),
        "url_count": len(urls),
        "sections_detected": sections,            # list — stringified in report
        "section_count": len(sections),
        "section_coverage": round(len(sections) / len(SECTIONS), 4),
    }
