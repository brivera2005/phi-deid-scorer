from __future__ import annotations

import re

from app.deid import RARE_DIAGNOSES
from app.models import AnalyzeResponse, RiskFactor
from app.deid import redact_text


def _has_zip(text: str) -> bool:
 return bool(re.search(r"\b\d{5}(?:-\d{4})?\b", text))


def _has_rare_diagnosis(text: str) -> str | None:
 lower = text.lower()
 for dx in RARE_DIAGNOSES:
 if dx in lower:
 return dx
 return None


def _age_over_89(text: str) -> bool:
 return bool(re.search(r"\b(?:age|aged)\s+(?:9\d|[1-9]\d{2})\b", text, re.I))


def _small_population_zip(text: str) -> bool:
 # Demo: specific ZIPs flagged as small population
 small_zips = {"03601", "59901", "82001", "96799"}
 for z in small_zips:
 if z in text:
 return True
 return False


def _unique_occupation(text: str) -> bool:
 rare_jobs = ["astronaut", "judge", "ambassador", "olympic athlete", "congressman"]
 lower = text.lower()
 return any(j in lower for j in rare_jobs)


def _detailed_timeline(text: str) -> bool:
 dates = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text)
 return len(dates) >= 4


def score_risk(original_text: str, redacted_text: str, redaction_count: int) -> tuple[float, list[RiskFactor]]:
 factors: list[RiskFactor] = []

 zip_present = _has_zip(original_text)
 factors.append(
 RiskFactor(
 factor_id="zip_code",
 label="ZIP code present",
 weight=15.0,
 present=zip_present,
 detail="Geographic identifiers increase re-identification risk per HIPAA Safe Harbor.",
 )
 )

 rare = _has_rare_diagnosis(original_text)
 factors.append(
 RiskFactor(
 factor_id="rare_diagnosis",
 label="Rare diagnosis",
 weight=25.0,
 present=bool(rare),
 detail=f"Rare condition detected: {rare}" if rare else "No rare diagnosis patterns found.",
 )
 )

 age89 = _age_over_89(original_text)
 factors.append(
 RiskFactor(
 factor_id="age_over_89",
 label="Age > 89",
 weight=10.0,
 present=age89,
 detail="Ages over 89 are considered identifying under Safe Harbor.",
 )
 )

 small_zip = _small_population_zip(original_text)
 factors.append(
 RiskFactor(
 factor_id="small_pop_zip",
 label="Small-population ZIP",
 weight=20.0,
 present=small_zip,
 detail="ZIP in a low-population area increases quasi-identifier risk.",
 )
 )

 occupation = _unique_occupation(original_text)
 factors.append(
 RiskFactor(
 factor_id="unique_occupation",
 label="Distinctive occupation",
 weight=12.0,
 present=occupation,
 detail="Uncommon occupation can narrow identity in combination with other fields.",
 )
 )

 timeline = _detailed_timeline(original_text)
 factors.append(
 RiskFactor(
 factor_id="detailed_timeline",
 label="Detailed event timeline",
 weight=8.0,
 present=timeline,
 detail="Multiple specific dates enable record linkage attacks.",
 )
 )

 residual_phi = redaction_count < 3
 factors.append(
 RiskFactor(
 factor_id="residual_phi",
 label="Insufficient redaction",
 weight=18.0,
 present=residual_phi,
 detail=f"Only {redaction_count} PHI elements redacted - may leave quasi-identifiers.",
 )
 )

 # Base score from present factors
 raw = sum(f.weight for f in factors if f.present)
 # Residual risk from unredacted content length ratio
 residual_ratio = len(redacted_text) / max(len(original_text), 1)
 score = min(100.0, raw + (1 - residual_ratio) * 10)
 score = round(max(5.0, score), 1)

 return score, factors


def risk_level(score: float) -> str:
 if score >= 70:
 return "high"
 if score >= 40:
 return "moderate"
 return "low"


def analyze(clinical_note: str) -> AnalyzeResponse:
 redacted, redactions = redact_text(clinical_note)
 score, factors = score_risk(clinical_note, redacted, len(redactions))
 level = risk_level(score)

 summaries = {
 "high": "High re-identification risk - additional generalization or expert determination recommended before sharing.",
 "moderate": "Moderate risk - review quasi-identifiers and consider date shifting or ZIP truncation.",
 "low": "Low risk after redaction - suitable for internal analytics with standard safeguards.",
 }

 return AnalyzeResponse(
 original_text=clinical_note,
 redacted_text=redacted,
 redactions=redactions,
 redaction_count=len(redactions),
 risk_score=score,
 risk_level=level,
 risk_factors=factors,
 summary=summaries[level],
 )
