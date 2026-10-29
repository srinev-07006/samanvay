from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
import io
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.database import get_db
from app.models import Case, Institution, OverlapFlag
from app.routers.deps import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/excel")
def export_excel(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    wb = Workbook()
    ws = wb.active
    ws.title = "SAMANVAY Cases & Overlaps"

    # Header
    ws.append(["Case ID", "Institution Permanent ID", "Institution Name", "Region", "Source Bureau", "Category", "Status", "Assigned Officer", "Expected Disposal Date"])

    cases = db.query(Case).join(Institution, Case.institution_id == Institution.permanent_id, isouter=True).all()
    for c in cases:
        inst = c.institution
        ws.append([
            c.case_id,
            c.institution_id,
            inst.name if inst else "Unresolved",
            inst.region if inst else "",
            c.source_bureau,
            c.category,
            c.status,
            c.assigned_officer,
            c.expected_disposal_date.strftime("%Y-%m-%d") if c.expected_disposal_date else ""
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=samanvay_report.xlsx"}
    )

@router.get("/pdf")
def export_pdf(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=12
    )

    elements.append(Paragraph("SAMANVAY – Unified Institution Complaint Radar Report", title_style))
    elements.append(Paragraph(f"Generated on: {db.bind.dialect.name} | User: {current_user.username} ({current_user.role})", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Summary table
    total_cases = db.query(Case).count()
    pending_cases = db.query(Case).filter(Case.status == "Pending").count()
    overlaps_count = db.query(OverlapFlag).count()

    summary_data = [
        ["Metric", "Count"],
        ["Total Cases", str(total_cases)],
        ["Pending Cases", str(pending_cases)],
        ["Total Overlap Flags", str(overlaps_count)]
    ]

    t = Table(summary_data, colWidths=[250, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f1f5f9")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1"))
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Recent Overlap Flags Requiring Coordination:", styles['Heading2']))
    elements.append(Spacer(1, 8))

    flags = db.query(OverlapFlag).limit(10).all()
    flag_data = [["Flag ID", "Institution ID", "Confidence", "State"]]
    for f in flags:
        flag_data.append([str(f.id), f.institution_id, f"{f.confidence_score}%", f.state])

    ft = Table(flag_data, colWidths=[60, 140, 100, 100])
    ft.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#dc2626")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1"))
    ]))
    elements.append(ft)

    doc.build(elements)
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=samanvay_report.pdf"}
    )
