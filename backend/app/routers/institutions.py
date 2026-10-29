from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Institution, Case, OverlapFlag
from app.routers.deps import get_current_user

router = APIRouter(prefix="/institutions", tags=["Institutions"])

@router.get("/")
def list_institutions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query = db.query(Institution)
    if current_user.role == "RegionalOffice" and current_user.region and current_user.region != "All":
        query = query.filter(Institution.region == current_user.region)

    institutions = query.all()
    return [
        {
            "permanent_id": inst.permanent_id,
            "name": inst.name,
            "address": inst.address,
            "region": inst.region,
            "pincode": inst.pincode,
            "cases_count": len(inst.cases)
        } for inst in institutions
    ]

@router.get("/{permanent_id}")
def get_institution_profile(permanent_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    inst = db.query(Institution).filter(Institution.permanent_id == permanent_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    if current_user.role == "RegionalOffice" and current_user.region != "All" and inst.region != current_user.region:
        raise HTTPException(status_code=403, detail="Access denied to institutions outside your region")

    cases = []
    for c in inst.cases:
        cases.append({
            "case_id": c.case_id,
            "source_bureau": c.source_bureau,
            "category": c.category,
            "description": c.description,
            "status": c.status,
            "current_bureau": c.current_bureau,
            "assigned_officer": c.assigned_officer,
            "last_action": c.last_action,
            "next_action_required": c.next_action_required,
            "expected_disposal_date": c.expected_disposal_date.strftime("%Y-%m-%d") if c.expected_disposal_date else None,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M")
        })

    flags = db.query(OverlapFlag).filter(OverlapFlag.institution_id == permanent_id).all()

    return {
        "permanent_id": inst.permanent_id,
        "name": inst.name,
        "address": inst.address,
        "region": inst.region,
        "pincode": inst.pincode,
        "cases": cases,
        "overlap_flags": [
            {
                "id": f.id,
                "case_a_id": f.case_a_id,
                "case_b_id": f.case_b_id,
                "confidence_score": f.confidence_score,
                "reason": f.reason,
                "state": f.state
            } for f in flags
        ]
    }
