from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert
from app.routers.deps import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/")
def list_alerts(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query = db.query(Alert)
    if current_user.role not in ["SeniorManagement", "CompetentAuthority", "RB"]:
        query = query.filter((Alert.target_bureau_or_user == current_user.bureau_cell) | (Alert.target_bureau_or_user == current_user.username))

    alerts = query.order_by(Alert.created_at.desc()).all()
    return [
        {
            "id": a.id,
            "type": a.type,
            "case_id": a.case_id,
            "target_bureau_or_user": a.target_bureau_or_user,
            "is_read": a.is_read,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M")
        } for a in alerts
    ]

@router.post("/{alert_id}/read")
def mark_alert_read(alert_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    db.commit()
    return {"message": "Alert marked as read", "id": alert_id}
