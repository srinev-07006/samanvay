from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Case, Institution, TimelineEvent, AuditLog, OverlapFlag
from app.routers.deps import get_current_user
from app.services.matcher import resolve_institution
from app.services.overlap import check_and_create_overlap

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.get("/")
def list_cases(
    search: Optional[str] = None,
    bureau: Optional[str] = None,
    region: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Case).join(Institution, Case.institution_id == Institution.permanent_id, isouter=True)

    # RBAC filtering: Regional Office sees only their assigned region
    if current_user.role == "RegionalOffice" and current_user.region and current_user.region != "All":
        query = query.filter(Institution.region == current_user.region)

    if search:
        search_filter = f"%{search}%"
        query = query.filter((Case.case_id.ilike(search_filter)) | (Case.description.ilike(search_filter)) | (Institution.name.ilike(search_filter)))
    if bureau:
        query = query.filter(Case.source_bureau == bureau)
    if region:
        query = query.filter(Institution.region == region)
    if status:
        query = query.filter(Case.status == status)
    if category:
        query = query.filter(Case.category == category)

    cases = query.all()

    result = []
    for c in cases:
        inst = c.institution
        result.append({
            "case_id": c.case_id,
            "institution_id": c.institution_id,
            "institution_name": inst.name if inst else "Unresolved",
            "region": inst.region if inst else "Unknown",
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
    return result

@router.get("/{case_id}")
def get_case_detail(case_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    c = db.query(Case).filter(Case.case_id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")

    inst = c.institution
    # RBAC check for regional office
    if current_user.role == "RegionalOffice" and inst and current_user.region != "All" and inst.region != current_user.region:
        raise HTTPException(status_code=403, detail="Access denied to cases outside your region")

    # Audit log view
    audit = AuditLog(
        user_id=current_user.username,
        action="VIEW_CASE",
        entity=f"Case:{case_id}",
        timestamp=datetime.utcnow(),
        details=f"User viewed case {case_id}"
    )
    db.add(audit)
    db.commit()

    timeline = db.query(TimelineEvent).filter(TimelineEvent.case_id == case_id).order_by(TimelineEvent.timestamp.asc()).all()
    overlap_flags = db.query(OverlapFlag).filter((OverlapFlag.case_a_id == case_id) | (OverlapFlag.case_b_id == case_id)).all()

    return {
        "case_id": c.case_id,
        "institution_id": c.institution_id,
        "institution": {
            "permanent_id": inst.permanent_id if inst else None,
            "name": inst.name if inst else "Unresolved",
            "address": inst.address if inst else "",
            "region": inst.region if inst else "",
            "pincode": inst.pincode if inst else ""
        } if inst else None,
        "source_bureau": c.source_bureau,
        "category": c.category,
        "description": c.description,
        "status": c.status,
        "current_bureau": c.current_bureau,
        "assigned_officer": c.assigned_officer,
        "last_action": c.last_action,
        "next_action_required": c.next_action_required,
        "expected_disposal_date": c.expected_disposal_date.strftime("%Y-%m-%d") if c.expected_disposal_date else None,
        "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
        "timeline": [
            {
                "id": t.id,
                "officer": t.officer,
                "bureau_cell": t.bureau_cell,
                "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M"),
                "remarks": t.remarks,
                "attached_documents": t.attached_documents,
                "transfer_escalation_info": t.transfer_escalation_info
            } for t in timeline
        ],
        "overlap_flags": [
            {
                "id": f.id,
                "case_a_id": f.case_a_id,
                "case_b_id": f.case_b_id,
                "confidence_score": f.confidence_score,
                "reason": f.reason,
                "state": f.state
            } for f in overlap_flags
        ]
    }

@router.post("/")
def create_case(payload: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # 1. Resolve institution using entity resolution matcher if institution_id not provided
    inst_id = payload.get("institution_id")
    inst_name = payload.get("institution_name", "")
    inst_address = payload.get("institution_address", "")
    inst_pincode = payload.get("institution_pincode", "")
    inst_region = payload.get("institution_region", "")

    if not inst_id and inst_name:
        match_res = resolve_institution(db, inst_name, inst_address, inst_pincode, inst_region)
        inst_id = match_res.get("permanent_id")

    case_id = payload.get("case_id") or f"AICTE-2026-{int(datetime.utcnow().timestamp())}"

    new_case = Case(
        case_id=case_id,
        institution_id=inst_id,
        source_bureau=payload.get("source_bureau", current_user.bureau_cell or "Regulation Bureau"),
        category=payload.get("category", "General"),
        description=payload.get("description", ""),
        status=payload.get("status", "Pending"),
        current_bureau=payload.get("current_bureau", current_user.bureau_cell or "Regulation Bureau"),
        assigned_officer=payload.get("assigned_officer", current_user.username),
        last_action=payload.get("last_action", "Case created and logged"),
        next_action_required=payload.get("next_action_required", "Initial review"),
        expected_disposal_date=datetime.strptime(payload["expected_disposal_date"], "%Y-%m-%d") if payload.get("expected_disposal_date") else datetime.utcnow() + timedelta(days=15),
        created_at=datetime.utcnow()
    )
    db.add(new_case)
    db.commit()

    # Add initial timeline event
    timeline = TimelineEvent(
        case_id=new_case.case_id,
        officer=current_user.username,
        bureau_cell=current_user.bureau_cell or "Regulation Bureau",
        timestamp=datetime.utcnow(),
        remarks=f"Case created in {new_case.source_bureau}.",
        attached_documents=payload.get("document", "complaint.pdf")
    )
    db.add(timeline)
    db.commit()

    # Check for overlapping cases
    flags = check_and_create_overlap(db, new_case)

    # Audit log
    audit = AuditLog(
        user_id=current_user.username,
        action="CREATE_CASE",
        entity=f"Case:{new_case.case_id}",
        timestamp=datetime.utcnow(),
        details=f"Created case {new_case.case_id} for institution {inst_id}"
    )
    db.add(audit)
    db.commit()

    return {
        "message": "Case created successfully",
        "case_id": new_case.case_id,
        "institution_id": inst_id,
        "overlap_flags_created": len(flags)
    }
