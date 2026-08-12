# PHI De-ID + Re-ID Risk Scorer - Portfolio brief (4/10)

## Why this exists

Shows **privacy engineering for health data** - de-identification is not binary; residual quasi-identifiers can still enable re-identification.

## Interview pitch

*"I built a clinical text de-ID pipeline that redacts 12 PHI categories via pattern matching, then scores re-identification risk from quasi-identifiers like rare diagnoses, ZIP codes, and detailed timelines - with a before/after view for data governance teams."*

## Skills

- PHI detection & redaction (regex-based)
- Re-identification risk modeling
- HIPAA Safe Harbor factor awareness
- Privacy UX (before/after, factor breakdown)

## Run in 30 seconds

```powershell
.\run.ps1
# → http://127.0.0.1:8093 → Load rare diagnosis sample → Analyze
```

## Next in series

**#5 Hospital Bed Flow Optimizer** - operations research for capacity management.
