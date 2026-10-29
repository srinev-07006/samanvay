from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models import Case, Alert
from app.routers import auth, cases, institutions, overlaps, alerts, reports

app = FastAPI(
    title="SAMANVAY – Unified Institution Complaint Radar API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(institutions.router)
app.include_router(overlaps.router)
app.include_router(alerts.router)
app.include_router(reports.router)

# WebSocket Connection Manager for real-time updates and overlap radar banners
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or handle ping
            await websocket.send_json({"status": "connected", "echo": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background scheduler for SLA warnings and reminders
scheduler = BackgroundScheduler()

def check_sla_warnings():
    db = SessionLocal()
    try:
        # Check cases nearing expected disposal date (e.g. within 3 days)
        now = datetime.utcnow()
        cases = db.query(Case).all()
        for c in cases:
            if c.expected_disposal_date and (c.expected_disposal_date - now).days <= 3 and c.status not in ["Disposed"]:
                # Check if alert already exists
                existing = db.query(Alert).filter(Alert.case_id == c.case_id, Alert.type == "sla_warning").first()
                if not existing:
                    alert = Alert(
                        type="sla_warning",
                        case_id=c.case_id,
                        target_bureau_or_user=c.source_bureau,
                        is_read=False
                    )
                    db.add(alert)
        db.commit()
    except Exception as e:
        print(f"SLA background check error: {e}")
    finally:
        db.close()

scheduler.add_job(check_sla_warnings, 'interval', minutes=60)

@app.on_event("startup")
def startup_event():
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.get("/")
def read_root():
    return {
        "project": "SAMANVAY – Unified Institution Complaint Radar",
        "version": "1.0.0",
        "status": "active"
    }
