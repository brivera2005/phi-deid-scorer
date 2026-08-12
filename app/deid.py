from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import RedactionItem


@dataclass
class Pattern:
    category: str
    regex: re.Pattern[str]
    replacement: str


PATTERNS: list[Pattern] = [
    Pattern("name", re.compile(r"\b(?:Patient|Mr\.|Mrs\.|Ms\.|Dr\.)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-z]+)\b"), "[NAME]"),
    Pattern("name", re.compile(r"\b([A-Z][a-z]+,\s+[A-Z][a-z]+(?:\s+[A-Z]\.?)?)\b"), "[NAME]"),
    Pattern("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[EMAIL]"),
    Pattern("phone", re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE]"),
    Pattern("mrn", re.compile(r"\b(?:MRN|Medical Record|Record\s*#?)[:\s#]*(\d{6,12})\b", re.I), "[MRN]"),
    Pattern("mrn", re.compile(r"\bMRN\s+(\d{6,12})\b"), "[MRN]"),
    Pattern("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    Pattern("date", re.compile(r"\b(?:DOB|Date of Birth|born)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", re.I), "[DATE]"),
    Pattern("date", re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b"), "[DATE]"),
    Pattern("date", re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"), "[DATE]"),
    Pattern("address", re.compile(r"\b\d{1,5}\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct)\.?(?:\s+(?:Apt|Suite|#)\s*\w+)?\b", re.I), "[ADDRESS]"),
    Pattern("zip", re.compile(r"\b\d{5}(?:-\d{4})?\b"), "[ZIP]"),
    Pattern("ip", re.compile(r"\b(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-z]{2,}(?:/\S*)?\b"), "[URL]"),
]

# Rare diagnoses that increase re-ID risk (demo list)
RARE_DIAGNOSES = [
    "ehlers-danlos",
    "progeria",
    "als amyotrophic",
    "cystic fibrosis",
    "huntington",
    "guillain-barre",
    "marfan syndrome",
    "wilson disease",
    "hemophilia a",
]


def redact_text(text: str) -> tuple[str, list[RedactionItem]]:
    redactions: list[RedactionItem] = []
    spans: list[tuple[int, int, str, str, str]] = []

    for pat in PATTERNS:
        for m in pat.regex.finditer(text):
            original = m.group(0)
            spans.append((m.start(), m.end(), pat.category, original, pat.replacement))

    # Merge overlapping spans (keep earliest/longest)
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
    merged: list[tuple[int, int, str, str, str]] = []
    last_end = -1
    for span in spans:
        if span[0] >= last_end:
            merged.append(span)
            last_end = span[1]

    # Build redacted text right-to-left
    result = text
    for start, end, cat, orig, repl in sorted(merged, key=lambda s: s[0], reverse=True):
        redactions.append(
            RedactionItem(category=cat, original=orig, replacement=repl, start=start, end=end)
        )
        result = result[:start] + repl + result[end:]

    redactions.sort(key=lambda r: r.start)
    return result, redactions
