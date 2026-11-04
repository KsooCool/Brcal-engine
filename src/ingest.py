"""
Data ingestion and cleaning pipeline for civic CSV datasets.
"""
import csv
from datetime import datetime
from typing import List, Tuple
from src.models import CivicRecord


def parse_date(date_str: str) -> datetime:
    """
    Attempts to parse multiple standard civic date formats.
    Falls back to a default timestamp if parsing fails.
    """
    date_str = date_str.strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y",
        "%m/%d/%y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return datetime(1970, 1, 1)


def load_and_clean_csv(file_path: str) -> Tuple[List[CivicRecord], int]:
    """
    Reads a CSV dataset, cleans invalid or missing data,
    and returns a list of valid CivicRecords and a count of skipped rows.
    """
    records: List[CivicRecord] = []
    skipped_count = 0

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row_idx, row in enumerate(reader, start=1):
            cleaned_row = {
                (k.strip() if k else ""): (v.strip() if v else "")
                for k, v in row.items()
            }

            record_id = (
                cleaned_row.get("ID")
                or cleaned_row.get("Service Request ID")
                or cleaned_row.get("id")
                or str(row_idx)
            )

            raw_category = cleaned_row.get("Category") or cleaned_row.get("Type") or "Unspecified"
            category = raw_category.title()

            raw_street = cleaned_row.get("Street") or cleaned_row.get("Address") or "Unknown"
            street = raw_street.upper()

            raw_neighborhood = cleaned_row.get("Neighborhood") or cleaned_row.get("District") or "Unknown"
            neighborhood = raw_neighborhood.title()

            status = (cleaned_row.get("Status") or "OPEN").upper()

            raw_date = cleaned_row.get("Date") or cleaned_row.get("Created Date") or ""
            incident_date = parse_date(raw_date)

            if not record_id or category == "Unspecified":
                skipped_count += 1
                continue

            record = CivicRecord(
                record_id=record_id,
                incident_date=incident_date,
                category=category,
                street=street,
                neighborhood=neighborhood,
                status=status,
                raw_data=cleaned_row,
            )
            records.append(record)

    return records, skipped_count