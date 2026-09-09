import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import status

# Import your engine
# Adjust this if your engine file is somewhere else
from app.engine.engine import run_engine

app = FastAPI()

app.include_router(status.router, prefix="/status", tags=["status"])

# CORS (optional but recommended)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "GhostTrace backend running"}

@app.get("/run-engine")
def run_engine_endpoint():
    try:
        # Call run_engine with NO required argument
        result = run_engine(None)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# Render requires binding to PORT env var
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

