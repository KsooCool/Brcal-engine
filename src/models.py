"""
Data models for the Baton Rouge Civic Analytics Lab (BRCAL) engine.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CivicRecord:
    record_id: str
    incident_date: datetime
    category: str
    street: str
    neighborhood: str
    status: str
    raw_data: dict

    def __repr__(self) -> str:
        date_str = self.incident_date.strftime("%Y-%m-%d")
        return f"<CivicRecord ID={self.record_id} Date={date_str} Cat='{self.category}'>"