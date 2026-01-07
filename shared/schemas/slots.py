from pydantic import BaseModel


class SlotData(BaseModel):
    consent_ok: bool | None = None
    chief_complaint: str | None = None
    symptom_track: str | None = None  # COGNITIVE, DIZZINESS, HEADACHE, TREMOR
    # TODO: expand remaining slots from scenario.json
