import csv
import io
from datetime import datetime

class RBAdapter:
    """Adapter for Regulation Bureau (RB) case data format"""
    @staticmethod
    def parse_row(row: dict) -> dict:
        return {
            "case_id": row.get("rb_case_id") or row.get("case_id"),
            "institution_id": row.get("institution_id"),
            "source_bureau": "Regulation Bureau",
            "category": row.get("category", "General"),
            "description": row.get("description", ""),
            "status": row.get("status", "Pending"),
            "current_bureau": "Regulation Bureau",
            "assigned_officer": row.get("officer", "Unassigned"),
            "last_action": row.get("last_action", "Case filed"),
            "next_action_required": row.get("next_action", "Initial review"),
            "expected_disposal_date": datetime.strptime(row["expected_disposal_date"], "%Y-%m-%d") if row.get("expected_disposal_date") else datetime.utcnow(),
            "created_at": datetime.utcnow()
        }

class PGRCAdapter:
    """Adapter for PGRC (Public Grievance Redressal Cell) case data format"""
    @staticmethod
    def parse_row(row: dict) -> dict:
        return {
            "case_id": row.get("grievance_id") or row.get("case_id"),
            "institution_id": row.get("institution_id"),
            "source_bureau": "PGRC",
            "category": row.get("grievance_category", row.get("category", "General")),
            "description": row.get("grievance_text", row.get("description", "")),
            "status": row.get("status", "Pending"),
            "current_bureau": "PGRC",
            "assigned_officer": row.get("assigned_to", "Unassigned"),
            "last_action": row.get("last_action", "Grievance received"),
            "next_action_required": row.get("next_action", "Verify grievance"),
            "expected_disposal_date": datetime.strptime(row["expected_disposal_date"], "%Y-%m-%d") if row.get("expected_disposal_date") else datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
