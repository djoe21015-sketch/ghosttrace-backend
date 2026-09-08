import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your engine
# This matches your folder structure:
# GhostTrace/app/engine/engine.py
from app.engine.engine import run_engine

app = FastAPI()

# CORS (optional but recommended)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {"status": "GhostTrace backend running"}

# Engine endpoint
@app.get("/run-engine")
def run_engine_endpoint():
    try:
        result = run_engine()
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# Render requires binding to PORT env var
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
