from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.report import Report

router = APIRouter()

# Dependency: get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# List all reports
@router.get("/list")
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).all()
    return reports

# Get a single report
@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

# Get all reports for a specific target
@router.get("/target/{target_id}")
def get_reports_for_target(target_id: int, db: Session = Depends(get_db)):
    reports = db.query(Report).filter(Report.target_id == target_id).all()
    return reports
