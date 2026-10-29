from sqlalchemy.orm import Session
from app.models import Case, OverlapFlag, TimelineEvent, Alert
from datetime import datetime

def check_and_create_overlap(db: Session, new_case: Case):
    """
    Checks if a newly created or updated case overlaps with existing open cases
    for the same institution in a DIFFERENT Bureau/Cell.
    """
    if not new_case.institution_id:
        return []

    # Find other open cases for the same institution in different bureaus
    open_statuses = ["Pending", "Under Process"]
    existing_cases = db.query(Case).filter(
        Case.institution_id == new_case.institution_id,
        Case.case_id != new_case.case_id,
        Case.status.in_(open_statuses),
        Case.source_bureau != new_case.source_bureau
    ).all()

    created_flags = []

    for ex_case in existing_cases:
        # Check if an overlap flag already exists for this pair (open or dismissed)
        existing_flag = db.query(OverlapFlag).filter(
            ((OverlapFlag.case_a_id == new_case.case_id) & (OverlapFlag.case_b_id == ex_case.case_id)) |
            ((OverlapFlag.case_a_id == ex_case.case_id) & (OverlapFlag.case_b_id == new_case.case_id))
        ).first()

        if existing_flag:
            # If previously dismissed, do not re-fire
            if existing_flag.state == "Dismissed":
                continue
            # If already exists and open, skip creation
            continue

        # Calculate confidence & reason based on rules
        confidence = 90.0
        reason_parts = [f"Same institution ID ({new_case.institution_id})"]

        if new_case.category == ex_case.category:
            confidence = 98.0
            reason_parts.append(f"identical category: {new_case.category}")
        else:
            reason_parts.append(f"related active cases across different bureaus ({new_case.source_bureau} & {ex_case.source_bureau})")

        reason = f"Potential Overlapping Cases – Coordination Required. " + ", ".join(reason_parts) + "."

        flag = OverlapFlag(
            case_a_id=new_case.case_id,
            case_b_id=ex_case.case_id,
            institution_id=new_case.institution_id,
            confidence_score=confidence,
            reason=reason,
            state="Open",
            created_at=datetime.utcnow()
        )
        db.add(flag)

        # Create alerts for both bureaus
        alert_a = Alert(
            type="overlap",
            case_id=new_case.case_id,
            target_bureau_or_user=new_case.source_bureau,
            is_read=False
        )
        alert_b = Alert(
            type="overlap",
            case_id=ex_case.case_id,
            target_bureau_or_user=ex_case.source_bureau,
            is_read=False
        )
        db.add(alert_a)
        db.add(alert_b)
        created_flags.append(flag)

    db.commit()
    return created_flags

def decide_overlap_flag(db: Session, flag_id: int, action: str, decided_by: str):
    """
    Action can be 'Link', 'Map', or 'Dismiss'.
    Records decision in both cases' timelines and updates flag state.
    """
    flag = db.query(OverlapFlag).filter(OverlapFlag.id == flag_id).first()
    if not flag:
        raise ValueError("Overlap flag not found")

    state_map = {
        "Link": "Linked",
        "Map": "Mapped",
        "Dismiss": "Dismissed"
    }

    if action not in state_map:
        raise ValueError("Invalid action. Must be Link, Map, or Dismiss.")

    flag.state = state_map[action]
    flag.decided_by = decided_by
    flag.decided_at = datetime.utcnow()

    # Add immutable timeline events to both cases
    event_a = TimelineEvent(
        case_id=flag.case_a_id,
        officer=decided_by,
        bureau_cell="Coordination Cell",
        timestamp=datetime.utcnow(),
        remarks=f"Overlap flag {flag.id} decided as '{action}' by {decided_by}.",
        attached_documents=None,
        transfer_escalation_info=f"Flag action: {action}"
    )
    event_b = TimelineEvent(
        case_id=flag.case_b_id,
        officer=decided_by,
        bureau_cell="Coordination Cell",
        timestamp=datetime.utcnow(),
        remarks=f"Overlap flag {flag.id} decided as '{action}' by {decided_by}.",
        attached_documents=None,
        transfer_escalation_info=f"Flag action: {action}"
    )
    db.add(event_a)
    db.add(event_b)
    db.commit()
    db.refresh(flag)
    return flag
