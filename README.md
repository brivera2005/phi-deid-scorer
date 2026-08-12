# PHI De-ID + Re-ID Risk Scorer

**Project 4 of 10** in a healthcare portfolio series - **privacy engineering & de-identification**.

Paste clinical note text to **redact PHI** (names, dates, phones, MRNs, addresses, emails) and receive a **re-identification risk score** with factor breakdown and before/after comparison.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green) ![License](https://img.shields.io/badge/License-MIT-lightgrey)

**Repo:** [github.com/brivera2005/phi-deid-scorer](https://github.com/brivera2005/phi-deid-scorer)

## Demo

1. Start server (`run.bat` or below)
2. Open **http://127.0.0.1:8093**
3. Load **Rare diagnosis + full PHI** sample
4. Click **Analyze & redact** → see redacted text, risk score, and factor breakdown

## Quick start (Windows)

```powershell
cd C:\Users\brive\Projects\phi-deid-scorer
.\run.ps1
```

Open **http://127.0.0.1:8093**

## Features

- Pattern-based PHI redaction (names, DOB, MRN, SSN, phone, email, address, ZIP, URLs)
- Re-identification risk scoring (0 - 100)
- Risk factors: ZIP codes, rare diagnoses, age >89, small-population ZIP, distinctive occupation, detailed timelines
- Before/after side-by-side text comparison
- Redaction log with category tags
- Two sample cases in `samples/`

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/samples` | List sample notes |
| GET | `/api/samples/{id}` | Get sample text |
| POST | `/api/analyze` | Redact PHI and score risk |

## Portfolio series

| # | Project | Status |
|---|---------|--------|
| 1 | FHIR Patient Timeline | ✅ |
| 2 | Prior Authorization Copilot | ✅ |
| 3 | Medication Reconciliation | ✅ |
| 4 | **De-ID + Re-ID Risk Scorer** | ✅ This repo |
| 5 - 10 | … | Planned |

## Disclaimer

Demo de-identification using regex patterns only. Not HIPAA Safe Harbor certified. Not for production PHI processing.

## License

MIT
