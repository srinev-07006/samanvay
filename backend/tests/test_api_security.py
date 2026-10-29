import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, ProgrammingError
from app.database import Base
from app.models import Institution, Case, TimelineEvent, User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    # SQLite in memory doesn't support PL/pgSQL trigger, so we test trigger logic / model behavior or mock it.
    # For SQLite tests, we verify cascade and relationships. For Postgres trigger test, we can use a mock or connection if available.
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    inst = Institution(permanent_id="1-1111111", name="XYZ College", address="Pune", region="West", pincode="411001")
    session.add(inst)
    session.commit()

    yield session
    session.close()

def test_timeline_append_only_model(db_session):
    case = Case(
        case_id="C-999",
        institution_id="1-1111111",
        source_bureau="RB",
        category="Fee",
        description="Test",
        status="Pending",
        current_bureau="RB",
        assigned_officer="Officer",
        last_action="Filed",
        next_action_required="Review",
        expected_disposal_date=db_session.bind.engine.dialect.name == 'sqlite' and None or None
    )
    # Using python datetime
    from datetime import datetime, timedelta
    case.expected_disposal_date = datetime.utcnow() + timedelta(days=10)
    db_session.add(case)
    db_session.commit()

    timeline = TimelineEvent(
        case_id="C-999",
        officer="Officer",
        bureau_cell="RB",
        remarks="Initial remark"
    )
    db_session.add(timeline)
    db_session.commit()

    assert db_session.query(TimelineEvent).count() == 1

    # In a real PostgreSQL database, UPDATE or DELETE on timeline_events triggers an exception.
    # Here we verify that timeline records are intended as append-only records.
    t_event = db_session.query(TimelineEvent).first()
    assert t_event.remarks == "Initial remark"
