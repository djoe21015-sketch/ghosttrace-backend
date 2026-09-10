import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import status

from app.engine.engine import run_engine

app = FastAPI()

app.include_router(status.router, prefix="/status", tags=["status"])

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
        result = run_engine(None)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# ============================
# AUTOMATION BLOCK (CLEAN)
# ============================

from apscheduler.schedulers.background import BackgroundScheduler
from app.engine.leadfinder import find_leads
from app.engine.webhook import send_alert
from app.engine.reportgen import generate_report

def auto_cycle():
    leads = find_leads()
    send_alert(f"GhostTrace found {len(leads)} new leads.")
    
    for lead in leads:
        result = run_engine(lead)
        report_file = generate_report(result)
        if report_file:
            send_alert(f"New report generated: {report_file}")

scheduler = BackgroundScheduler()
scheduler.add_job(run_engine, "interval", minutes=30)
scheduler.add_job(find_leads, "interval", hours=6)
scheduler.add_job(auto_cycle, "interval", hours=12)
scheduler.start()

# ============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)


