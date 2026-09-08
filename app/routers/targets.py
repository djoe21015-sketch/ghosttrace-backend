from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.target import Target
from app.models.domain_recon import run_domain_recon
from app.models.email_intel import run_email_intel
from app.models.username_intel import run_username_intel
from app.models.ip_intel import run_ip_intel
from app.models.social_intel import run_social_intel
from app.models.darkweb_intel import run_darkweb_intel

router = APIRouter(prefix="/targets", tags=["Targets"])

# Dependency: get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new target
@router.post("/create")
def create_target(name: str, target_type: str, value: str, db: Session = Depends(get_db)):
    existing = db.query(Target).filter(Target.value == value).first()
    if existing:
        raise HTTPException(status_code=400, detail="Target already exists")

    target = Target(name=name, target_type=target_type, value=value)
    db.add(target)
    db.commit()
    db.refresh(target)

    return {"message": "Target created", "target_id": target.id}

# List all targets
@router.get("/list")
def list_targets(db: Session = Depends(get_db)):
    return db.query(Target).all()

# Get a single target
@router.get("/{target_id}")
def get_target(target_id: int, db: Session = Depends(get_db)):
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target

# Run a full OSINT scan (placeholder for now)

@router.post("/{target_id}/scan")
def scan_target(target_id: int, db: Session = Depends(get_db)):
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    target.status = "scanning"

    # Domain recon
    if target.target_type == "domain":
        recon_result = run_domain_recon(target.value)
        if not target.intelligence:
            target.intelligence = {}
        target.intelligence["domain_recon"] = recon_result

    # Email intelligence
    elif target.target_type == "email":
        email_result = run_email_intel(target.value)
        if not target.intelligence:
            target.intelligence = {}
        target.intelligence["email_intel"] = email_result

    # Username intelligence
    elif target.target_type == "username":
        username_result = run_username_intel(target.value)
        if not target.intelligence:
            target.intelligence = {}
        target.intelligence["username_intel"] = username_result

    # IP intelligence
    elif target.target_type == "ip":
        ip_result = run_ip_intel(target.value)
        if not target.intelligence:
            target.intelligence = {}
        target.intelligence["ip_intel"] = ip_result

    # Social intelligence
    elif target.target_type == "social":
        social_result = run_social_intel(target.value)
        if not target.intelligence:
            target.intelligence = {}
        target.intelligence["social_intel"] = social_result

    # Dark web intelligence
    elif target.target_type == "darkweb":
        darkweb_result = run_darkweb_intel(target.value)
        if not target.intelligence:
            target.intelligence = {}
        target.intelligence["darkweb_intel"] = darkweb_result

    else:
        if not target.intelligence:
            target.intelligence = {}
        target.intelligence["message"] = (
            "Scan available for domains, emails, usernames, IPs, social handles, and dark web queries only (for now)."
        )

    db.commit()
    db.refresh(target)

    return {"message": "Scan complete", "target_id": target.id}


# Get intelligence results
@router.get("/{target_id}/intelligence")
def get_intelligence(target_id: int, db: Session = Depends(get_db)):
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    return target.intelligence

# Run AI analysis (placeholder)
@router.post("/{target_id}/ai")
def ai_analysis(target_id: int, db: Session = Depends(get_db)):
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    # Placeholder: real AI integration will be added next
    target.ai_summary = "AI analysis placeholder. Real model integration coming next."
    target.risk_score = 0.0
    target.recommendations = {"message": "AI recommendations will appear here."}

    db.commit()
    db.refresh(target)

    return {"message": "AI analysis complete", "target_id": target.id}

# Generate report (placeholder)
@router.get("/{target_id}/report")
def generate_report(target_id: int, db: Session = Depends(get_db)):
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    return {
        "target": target.value,
        "type": target.target_type,
        "intelligence": target.intelligence,
        "ai_summary": target.ai_summary,
        "risk_score": target.risk_score,
        "recommendations": target.recommendations,
    }
