from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import OverlapFlag, Institution
from app.routers.deps import get_current_user
from app.services.overlap import decide_overlap_flag

router = APIRouter(prefix="/overlaps", tags=["Overlaps"])

@router.get("/")
def list_overlap_flags(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query = db.query(OverlapFlag).join(Institution, OverlapFlag.institution_id == Institution.permanent_id)
    if current_user.role == "RegionalOffice" and current_user.region and current_user.region != "All":
        query = query.filter(Institution.region == current_user.region)

    flags = query.all()
    result = []
    for f in flags:
        inst = f.institution
        result.append({
            "id": f.id,
            "case_a_id": f.case_a_id,
            "case_b_id": f.case_b_id,
            "institution_id": f.institution_id,
            "institution_name": inst.name if inst else "Unknown",
            "region": inst.region if inst else "",
            "confidence_score": f.confidence_score,
            "reason": f.reason,
            "state": f.state,
            "decided_by": f.decided_by,
            "decided_at": f.decided_at.strftime("%Y-%m-%d %H:%M") if f.decided_at else None,
            "created_at": f.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return result

@router.post("/{flag_id}/decide")
def decide_overlap(flag_id: int, payload: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    action = payload.get("action") # Link, Map, Dismiss
    if not action:
        raise HTTPException(status_code=400, detail="Action (Link, Map, Dismiss) is required")

    try:
        updated_flag = decide_overlap_flag(db, flag_id, action, current_user.username)
        return {
            "message": f"Overlap flag {flag_id} updated to {updated_flag.state}",
            "flag_id": updated_flag.id,
            "state": updated_flag.state
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
