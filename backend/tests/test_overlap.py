import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Institution, Case, OverlapFlag
from app.services.overlap import check_and_create_overlap, decide_overlap_flag

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    inst = Institution(
        permanent_id="1-1111111",
        name="XYZ College of Engineering",
        address="123 Tech Park Road, Pune",
        region="West",
        pincode="411001"
    )
    session.add(inst)
    session.commit()

    yield session
    session.close()

def test_overlap_different_bureau_open_cases(db_session):
    # Case 1 in Regulation Bureau
    case1 = Case(
        case_id="C-001",
        institution_id="1-1111111",
        source_bureau="Regulation Bureau",
        category="Faculty Shortage",
        description="Faculty shortage issue",
        status="Pending",
        current_bureau="Regulation Bureau",
        assigned_officer="Officer A",
        last_action="Filed",
        next_action_required="Review",
        expected_disposal_date=datetime.utcnow() + timedelta(days=10)
    )
    db_session.add(case1)
    db_session.commit()

    # Case 2 in PGRC (different bureau, same institution, open status)
    case2 = Case(
        case_id="C-002",
        institution_id="1-1111111",
        source_bureau="PGRC",
        category="Faculty Shortage",
        description="Grievance on faculty",
        status="Pending",
        current_bureau="PGRC",
        assigned_officer="Officer B",
        last_action="Filed",
        next_action_required="Review",
        expected_disposal_date=datetime.utcnow() + timedelta(days=10)
    )
    db_session.add(case2)
    db_session.commit()

    flags = check_and_create_overlap(db_session, case2)
    assert len(flags) == 1
    assert flags[0].confidence_score >= 90.0
    assert "Coordination Required" in flags[0].reason

def test_overlap_same_bureau_no_flag(db_session):
    case1 = Case(
        case_id="C-001",
        institution_id="1-1111111",
        source_bureau="Regulation Bureau",
        category="Faculty Shortage",
        description="Faculty shortage issue",
        status="Pending",
        current_bureau="Regulation Bureau",
        assigned_officer="Officer A",
        last_action="Filed",
        next_action_required="Review",
        expected_disposal_date=datetime.utcnow() + timedelta(days=10)
    )
    db_session.add(case1)
    db_session.commit()

    case2 = Case(
        case_id="C-003",
        institution_id="1-1111111",
        source_bureau="Regulation Bureau", # Same bureau
        category="Fee Dispute",
        description="Fee issue",
        status="Pending",
        current_bureau="Regulation Bureau",
        assigned_officer="Officer C",
        last_action="Filed",
        next_action_required="Review",
        expected_disposal_date=datetime.utcnow() + timedelta(days=10)
    )
    db_session.add(case2)
    db_session.commit()

    flags = check_and_create_overlap(db_session, case2)
    assert len(flags) == 0

def test_overlap_closed_case_no_flag(db_session):
    case1 = Case(
        case_id="C-004",
        institution_id="1-1111111",
        source_bureau="Regulation Bureau",
        category="Faculty Shortage",
        description="Faculty shortage issue",
        status="Disposed", # Closed status
        current_bureau="Regulation Bureau",
        assigned_officer="Officer A",
        last_action="Closed",
        next_action_required="None",
        expected_disposal_date=datetime.utcnow()
    )
    db_session.add(case1)
    db_session.commit()

    case2 = Case(
        case_id="C-005",
        institution_id="1-1111111",
        source_bureau="PGRC",
        category="Faculty Shortage",
        description="Grievance on faculty",
        status="Pending",
        current_bureau="PGRC",
        assigned_officer="Officer B",
        last_action="Filed",
        next_action_required="Review",
        expected_disposal_date=datetime.utcnow() + timedelta(days=10)
    )
    db_session.add(case2)
    db_session.commit()

    flags = check_and_create_overlap(db_session, case2)
    assert len(flags) == 0

def test_dismissed_flag_does_not_refire(db_session):
    case1 = Case(
        case_id="C-006",
        institution_id="1-1111111",
        source_bureau="Regulation Bureau",
        category="Faculty Shortage",
        description="Faculty shortage issue",
        status="Pending",
        current_bureau="Regulation Bureau",
        assigned_officer="Officer A",
        last_action="Filed",
        next_action_required="Review",
        expected_disposal_date=datetime.utcnow() + timedelta(days=10)
    )
    case2 = Case(
        case_id="C-007",
        institution_id="1-1111111",
        source_bureau="PGRC",
        category="Faculty Shortage",
        description="Grievance on faculty",
        status="Pending",
        current_bureau="PGRC",
        assigned_officer="Officer B",
        last_action="Filed",
        next_action_required="Review",
        expected_disposal_date=datetime.utcnow() + timedelta(days=10)
    )
    db_session.add_all([case1, case2])
    db_session.commit()

    flags = check_and_create_overlap(db_session, case2)
    assert len(flags) == 1

    # Dismiss the flag
    decide_overlap_flag(db_session, flags[0].id, "Dismiss", "admin_user")

    # Re-running check should not create a new flag
    flags_retry = check_and_create_overlap(db_session, case2)
    assert len(flags_retry) == 0
