"""
Core data structure indexes and query operations for the civic analytics engine.
"""
from collections import defaultdict
from typing import List, Dict, Set, Optional
from src.models import CivicRecord


class CivicDataEngine:
    def __init__(self, records: List[CivicRecord]):
        # 1. Master sequential list of all records
        self.records: List[CivicRecord] = records

        # 2. Hash map index: ID -> CivicRecord (O(1) average lookup)
        self.by_id: Dict[str, CivicRecord] = {}

        # 3. Hash map grouping: Category -> List[CivicRecord]
        self.by_category: Dict[str, List[CivicRecord]] = defaultdict(list)

        # 4. Hash set: Set of unique neighborhoods (O(1) average membership test)
        self.neighborhoods: Set[str] = set()

        # Build the indexes across the loaded records
        self._build_indexes()

    def _build_indexes(self) -> None:
        """Populates dictionary and set indexes from the master records list."""
        for record in self.records:
            # Map ID to the record
            self.by_id[record.record_id] = record

            # Group under category
            self.by_category[record.category].append(record)

            # Add neighborhood to unique set (normalized with .title())
            if record.neighborhood and record.neighborhood.title() != "Unknown":
                self.neighborhoods.add(record.neighborhood.title())

    # --- Milestone 4: Query Operations ---

    def find_by_id(self, record_id: str) -> Optional[CivicRecord]:
        """O(1) lookup: returns the record with the given ID or None."""
        return self.by_id.get(record_id)

    def find_by_category(self, category: str) -> List[CivicRecord]:
        """O(1) bucket retrieval: returns all records matching a category."""
        return self.by_category.get(category.title(), [])

    def find_by_street(self, street_name: str) -> List[CivicRecord]:
        """
        O(n) linear scan: finds all records containing the given street string.
        A list scan is required here because streets can be partial matches.
        """
        query = street_name.upper()
        return [r for r in self.records if query in r.street]

    def has_neighborhood(self, neighborhood: str) -> bool:
        """O(1) set membership check."""
        return neighborhood.title() in self.neighborhoods

    def category_counts(self) -> Dict[str, int]:
        """Computes summary distribution across all categories."""
        return {cat: len(recs) for cat, recs in self.by_category.items()}