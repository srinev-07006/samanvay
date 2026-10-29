import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Institution
from app.services.matcher import resolve_institution, normalize_text

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed test institution
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

def test_text_normalization():
    assert normalize_text("XYZ Engg. College, Pune!") == "xyz engineering college pune"
    assert normalize_text("ABC Inst. of Tech.") == "abc institute of technology"

def test_exact_and_abbreviation_matching(db_session):
    # Test "XYZ Engg College, Pune" resolving to "XYZ College of Engineering"
    result = resolve_institution(
        db=db_session,
        query_name="XYZ Engg College, Pune",
        query_address="123 Tech Park Rd, Pune",
        query_pincode="411001",
        query_region="West"
    )
    assert result["permanent_id"] == "1-1111111"
    assert result["status"] == "auto_resolved"
    assert result["confidence"] >= 85.0

def test_misspelling_matching(db_session):
    # Test minor misspelling
    result = resolve_institution(
        db=db_session,
        query_name="XY_Z Coll of Engg",
        query_address="123 Tech Park",
        query_pincode="411001",
        query_region="West"
    )
    assert result["permanent_id"] == "1-1111111"
    assert result["confidence"] >= 70.0

def test_manual_confirm_threshold(db_session):
    # Test completely unrelated institution falling below threshold
    result = resolve_institution(
        db=db_session,
        query_name="Totally Unrelated University",
        query_address="999 Nowhere Street",
        query_pincode="999999",
        query_region="East",
        threshold=85.0
    )
    assert result["status"] == "manual_confirm"
    assert result["confidence"] < 85.0
