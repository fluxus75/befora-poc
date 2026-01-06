from typing import Optional

from pydantic import BaseModel


class SlotData(BaseModel):
    consent_ok: Optional[bool] = None
    chief_complaint: Optional[str] = None
    symptom_track: Optional[str] = None  # COGNITIVE, DIZZINESS, HEADACHE, TREMOR
    # TODO: expand remaining slots from scenario.json
