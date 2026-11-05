"""Local web API for BeyondBinary. Uploaded files are processed on this host."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from beyondbinary.ml.pipeline import run_pipeline

ROOT = Path(__file__).resolve().parents[1]
STATIC = Path(__file__).resolve().parent / "static"
MODEL_DEFAULT = Path(os.getenv("BEYONDBINARY_MODEL", ROOT / "artifacts/ddos_model.joblib"))
app = FastAPI(title="BeyondBinary", description="Local-first SOC triage")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "model_configured": MODEL_DEFAULT.is_file()}


@app.post("/api/analyze")
async def analyze(csv_file: UploadFile = File(...), model_path: str = Form("")):
    if not csv_file.filename or not csv_file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Upload a .csv flow export.")
    model = Path(model_path).expanduser() if model_path.strip() else MODEL_DEFAULT
    if not model.is_file():
        raise HTTPException(400, "Model file not found. Set BEYONDBINARY_MODEL or provide a valid local model path.")
    with tempfile.TemporaryDirectory(prefix="beyondbinary-") as tmp:
        input_path = Path(tmp) / "input.csv"
        output_path = Path(tmp) / "incident_queue.csv"
        input_path.write_bytes(await csv_file.read())
        try:
            queue = run_pipeline(str(input_path), str(model))
        except Exception as exc:
            raise HTTPException(422, f"Analysis failed: {exc}") from exc
        queue.to_csv(output_path, index=False)
        suspicious = int(queue["human_review_required"].sum())
        incidents = int(queue.loc[queue["incident_id"].ne(""), "incident_id"].nunique())
        return {
            "processed": len(queue),
            "review_required": suspicious,
            "incidents": incidents,
            "preview": queue.head(100).where(pd.notna(queue.head(100)), None).to_dict(orient="records"),
            "csv": queue.to_csv(index=False),
            "note": "Review flags are model-generated leads, not confirmed attacks.",
        }
