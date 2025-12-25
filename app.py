from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import time
import logging
import os

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ---------- FastAPI ----------
app = FastAPI(title="Sentiment Service")

from transformers import pipeline as hf_pipeline

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

logger.info("Loading HuggingFace model directly (no MLflow)...")
pipeline = hf_pipeline(
    "sentiment-analysis",
    model=MODEL_NAME
)
logger.info("Model loaded successfully")

# ---------- Schemas ----------
class TextRequest(BaseModel):
    texts: List[str]

# ---------- Routes ----------
@app.get("/health")
def health():
    return {"status": "OK"}

@app.post("/predict")
def predict(req: TextRequest):
    start_time = time.time()

    outputs = pipeline(req.texts)

    latency_ms = (time.time() - start_time) * 1000

    results = [
        {
            "label": o["label"],
            "score": o["score"]
        }
        for o in outputs
    ]

    logger.info(
        f"batch_size={len(req.texts)} | latency_ms={latency_ms:.2f}"
    )

    return {
        "latency_ms": round(latency_ms, 2),
        "batch_size": len(req.texts),
        "results": results
    }