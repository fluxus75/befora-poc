from __future__ import annotations

from html import escape

from shared.schemas.report import ReportData
from shared.schemas.session import SessionDetail


def build_report_data(detail: SessionDetail) -> ReportData:
    return ReportData(
        session_id=detail.session_id,
        patient_id=detail.patient_id,
        status=detail.status,
        created_at=detail.created_at,
        completed_at=detail.completed_at,
        reviewed_at=detail.reviewed_at,
        confirmed_at=detail.confirmed_at,
        slots=detail.slots,
        notes=detail.notes,
    )


def build_report_html(detail: SessionDetail) -> str:
    slots_html = "".join(
        f"<tr><th>{escape(slot.slot_key)}</th><td>{escape(slot.slot_value or '')}</td></tr>"
        for slot in detail.slots
    )
    notes_html = "".join(
        f"<li>{escape(note.note)} - {escape(note.doctor_id)}</li>"
        for note in detail.notes
    )
    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <title>Session Report</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 32px; }}
          h1 {{ margin-bottom: 8px; }}
          table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
          th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
          ul {{ margin-top: 8px; }}
        </style>
      </head>
      <body>
        <h1>Session Report</h1>
        <p><strong>Session:</strong> {escape(detail.session_id)}</p>
        <p><strong>Status:</strong> {escape(detail.status)}</p>
        <p><strong>Patient ID:</strong> {escape(detail.patient_id or "")}</p>
        <h2>Slots</h2>
        <table>
          <tbody>
            {slots_html}
          </tbody>
        </table>
        <h2>Notes</h2>
        <ul>
          {notes_html or "<li>No notes</li>"}
        </ul>
      </body>
    </html>
    """.strip()
