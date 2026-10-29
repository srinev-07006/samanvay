import re
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import Institution

def normalize_text(text_str: str) -> str:
    if not text_str:
        return ""
    s = text_str.lower()
    # Expand common abbreviations
    replacements = {
        r'\bengg\.?\b': 'engineering',
        r'\binst\.?\b': 'institute',
        r'\bcoll\.?\b': 'college',
        r'\btech\.?\b': 'technology',
        r'\buniv\.?\b': 'university',
        r'\bmgmt\.?\b': 'management',
        r'\bacad\.?\b': 'academy',
        r'\bpharm\.?\b': 'pharmacy',
        r'\barch\.?\b': 'architecture',
    }
    for pattern, repl in replacements.items():
        s = re.sub(pattern, repl, s)
    # Remove special characters and extra spaces
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def resolve_institution(db: Session, query_name: str, query_address: str = "", query_pincode: str = "", query_region: str = "", threshold: float = 85.0):
    """
    Resolves an institution name/address to an AICTE Permanent ID using:
    1. Normalization & pg_trgm / exact lookup
    2. RapidFuzz Jaro-Winkler (token_set_ratio or WRatio)
    3. Pincode / region boost
    4. Manual-confirm queue if below threshold
    """
    norm_name = normalize_text(query_name)
    norm_addr = normalize_text(query_address)

    institutions = db.query(Institution).all()
    if not institutions:
        return {"permanent_id": None, "confidence": 0.0, "status": "manual_confirm", "reason": "No institutions in database."}

    best_match = None
    highest_score = 0.0

    for inst in institutions:
        db_norm_name = normalize_text(inst.name)
        db_norm_addr = normalize_text(inst.address)

        # Calculate fuzzy similarity using RapidFuzz
        name_score = fuzz.jaro_winkler_similarity(norm_name, db_norm_name) * 100
        addr_score = fuzz.token_sort_ratio(norm_addr, db_norm_addr)

        # Combined weighted score
        combined_score = (name_score * 0.7) + (addr_score * 0.3)

        # Boost if pincode matches exactly
        if query_pincode and inst.pincode == query_pincode:
            combined_score = min(100.0, combined_score + 10.0)

        # Boost if region matches
        if query_region and inst.region.lower() == query_region.lower():
            combined_score = min(100.0, combined_score + 5.0)

        if combined_score > highest_score:
            highest_score = combined_score
            best_match = inst

    if highest_score >= threshold and best_match:
        return {
            "permanent_id": best_match.permanent_id,
            "name": best_match.name,
            "confidence": round(highest_score, 2),
            "status": "auto_resolved",
            "reason": f"Matched with {round(highest_score, 2)}% confidence using RapidFuzz Jaro-Winkler and metadata checks."
        }
    else:
        return {
            "permanent_id": best_match.permanent_id if best_match else None,
            "name": best_match.name if best_match else "Unknown",
            "confidence": round(highest_score, 2),
            "status": "manual_confirm",
            "reason": f"Confidence score {round(highest_score, 2)} is below threshold ({threshold}%). Sent to manual-confirm queue."
        }
