from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.models import AnalyzeRequest, AnalyzeResponse, SampleInfo
from app.risk_scorer import analyze

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
SAMPLES = ROOT / "samples"

SAMPLE_META = [
 SampleInfo(
 id="case-rare-diagnosis",
 title="Rare diagnosis + full PHI",
 description="Ehlers-Danlos with names, MRN, address - high re-ID risk.",
 ),
 SampleInfo(
 id="case-routine-visit",
 title="Routine follow-up note",
 description="Standard visit note with moderate PHI density.",
 ),
]

app = FastAPI(
 title="PHI De-ID + Re-ID Risk Scorer",
 description="Redact PHI from clinical notes and score re-identification risk.",
 version="1.0.0",
)


@app.get("/api/health")
def health():
 return {"status": "ok", "service": "phi-deid-scorer"}


@app.get("/api/samples", response_model=list[SampleInfo])
def list_samples():
 return SAMPLE_META


@app.get("/api/samples/{sample_id}")
def get_sample(sample_id: str):
 path = SAMPLES / f"{sample_id}.txt"
 if not path.exists():
 raise HTTPException(404, "Sample not found")
 meta = next((s for s in SAMPLE_META if s.id == sample_id), None)
 return {
 "id": sample_id,
 "content": path.read_text(encoding="utf-8"),
 "meta": meta.model_dump() if meta else None,
 }


@app.post("/api/analyze", response_model=AnalyzeResponse)
def run_analyze(body: AnalyzeRequest):
 return analyze(body.clinical_note)


@app.get("/")
def index():
 return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
