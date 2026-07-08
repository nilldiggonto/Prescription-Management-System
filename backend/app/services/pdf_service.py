import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.doctor_profile import DoctorProfile
from app.models.patient import Patient
from app.models.prescription import Prescription

_STYLES = getSampleStyleSheet()

_DOCTOR_NAME_STYLE = ParagraphStyle(
    "DoctorName", parent=_STYLES["Normal"], fontName="Helvetica-Bold", fontSize=15, leading=18
)
_DOCTOR_DETAIL_STYLE = ParagraphStyle(
    "DoctorDetail", parent=_STYLES["Normal"], fontSize=9.5, leading=13, textColor=colors.HexColor("#444444")
)
_SECTION_LABEL_STYLE = ParagraphStyle(
    "SectionLabel",
    parent=_STYLES["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=13,
    textColor=colors.HexColor("#1a1a1a"),
    spaceBefore=10,
    spaceAfter=4,
)
_BODY_STYLE = ParagraphStyle("Body", parent=_STYLES["Normal"], fontSize=10, leading=14)
_RX_STYLE = ParagraphStyle(
    "Rx", parent=_STYLES["Normal"], fontName="Helvetica-Bold", fontSize=16, leading=20, spaceBefore=12, spaceAfter=6
)


def generate_prescription_pdf(*, doctor_profile: DoctorProfile, patient: Patient, prescription: Prescription) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        title=f"Prescription - {patient.full_name}",
    )

    story: list = []
    story.extend(_letterhead(doctor_profile))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#999999")))
    story.append(Spacer(1, 8))
    story.extend(_patient_summary(patient, prescription))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))

    if prescription.diagnosis:
        story.append(Paragraph("Diagnosis", _SECTION_LABEL_STYLE))
        story.append(Paragraph(prescription.diagnosis.replace("\n", "<br/>"), _BODY_STYLE))

    story.append(Paragraph("℞", _RX_STYLE))
    story.extend(_medicines_table(prescription))

    if prescription.advice:
        story.append(Paragraph("Advice", _SECTION_LABEL_STYLE))
        story.append(Paragraph(prescription.advice.replace("\n", "<br/>"), _BODY_STYLE))

    if prescription.follow_up_date:
        story.append(Paragraph("Follow-up", _SECTION_LABEL_STYLE))
        story.append(Paragraph(prescription.follow_up_date.strftime("%d %b %Y"), _BODY_STYLE))

    story.append(Spacer(1, 36))
    story.extend(_signature_block(doctor_profile))

    doc.build(story)
    return buffer.getvalue()


def _letterhead(doctor_profile: DoctorProfile) -> list:
    story: list = [Paragraph(doctor_profile.full_name, _DOCTOR_NAME_STYLE)]

    detail_lines = [doctor_profile.degrees]
    if doctor_profile.specialization:
        detail_lines.append(doctor_profile.specialization)
    detail_lines.append(f"Reg. No: {doctor_profile.registration_number}")
    story.append(Paragraph(" &nbsp;|&nbsp; ".join(detail_lines), _DOCTOR_DETAIL_STYLE))

    footer_lines = [part for part in [doctor_profile.hospital_name, doctor_profile.chamber_address] if part]
    if doctor_profile.phone:
        footer_lines.append(f"Phone: {doctor_profile.phone}")
    if footer_lines:
        story.append(Paragraph(" &nbsp;|&nbsp; ".join(footer_lines), _DOCTOR_DETAIL_STYLE))

    return story


def _patient_summary(patient: Patient, prescription: Prescription) -> list:
    details = [f"<b>Patient:</b> {patient.full_name}"]
    if patient.age is not None:
        details.append(f"<b>Age:</b> {patient.age}")
    details.append(f"<b>Gender:</b> {patient.gender.value.capitalize()}")
    if patient.phone:
        details.append(f"<b>Phone:</b> {patient.phone}")

    date_str = prescription.created_at.strftime("%d %b %Y")
    row = Table(
        [[Paragraph(" &nbsp;&nbsp; ".join(details), _BODY_STYLE), Paragraph(f"<b>Date:</b> {date_str}", _BODY_STYLE)]],
        colWidths=[130 * mm, 34 * mm],
    )
    row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 0), (1, 0), "RIGHT")]))
    return [row, Spacer(1, 4)]


def _medicines_table(prescription: Prescription) -> list:
    header = ["#", "Medicine", "Dosage", "Frequency", "Duration", "Instructions"]
    rows = [header]
    for index, medicine in enumerate(prescription.medicines, start=1):
        rows.append(
            [
                str(index),
                Paragraph(medicine.name, _BODY_STYLE),
                Paragraph(medicine.dosage, _BODY_STYLE),
                Paragraph(medicine.frequency, _BODY_STYLE),
                Paragraph(medicine.duration, _BODY_STYLE),
                Paragraph(medicine.instructions or "-", _BODY_STYLE),
            ]
        )

    table = Table(rows, colWidths=[8 * mm, 40 * mm, 28 * mm, 30 * mm, 24 * mm, 34 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return [table, Spacer(1, 6)]


def _signature_block(doctor_profile: DoctorProfile) -> list:
    story: list = [
        Table(
            [[""]],
            colWidths=[60 * mm],
            style=TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.75, colors.HexColor("#333333"))]),
            hAlign="RIGHT",
        ),
        Spacer(1, 2),
        Paragraph(f"{doctor_profile.full_name}<br/>Reg. No: {doctor_profile.registration_number}", _BODY_STYLE),
    ]
    return story
