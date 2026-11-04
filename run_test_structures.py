import os
from src.ingest import load_and_clean_csv
from src.structures import CivicDataEngine

# Create a small dataset with multiple records across categories
sample_csv = """ID,Date,Category,Street,Neighborhood,Status
SR-1001,2026-03-01 08:30:00,Drainage,Plank Rd,North BR,Open
SR-1002,2026-03-02 09:15:00,Blight,Florida St,Downtown,Closed
SR-1003,2026-03-03 11:00:00,Drainage,Scenic Hwy,North BR,Open
SR-1004,2026-03-05 14:20:00,Traffic,Florida Blvd,Downtown,Open
SR-1005,2026-03-07 16:45:00,Blight,Government St,Mid City,Closed
"""

with open("test_structures.csv", "w") as f:
    f.write(sample_csv.strip())

# 1. Ingest
records, _ = load_and_clean_csv("test_structures.csv")
engine = CivicDataEngine(records)

print(f"Total indexed records: {len(engine.records)}")

# 2. Test ID Lookup - O(1)
rec = engine.find_by_id("SR-1003")
print(f"Lookup SR-1003: {rec.street} | Cat: {rec.category}")

# 3. Test Category Retrieval - O(1)
drainage_recs = engine.find_by_category("Drainage")
print(f"Drainage incidents ({len(drainage_recs)}): {[r.record_id for r in drainage_recs]}")

# 4. Test Partial Street Search - O(n)
florida_recs = engine.find_by_street("FLORIDA")
print(f"Florida street incidents ({len(florida_recs)}): {[r.record_id for r in florida_recs]}")

# 5. Test Neighborhood Set Membership - O(1)
print(f"Has 'Downtown'? {engine.has_neighborhood('Downtown')}")
print(f"Has 'Shenandoah'? {engine.has_neighborhood('Shenandoah')}")

# 6. Test Category Counts
print(f"Category counts: {engine.category_counts()}")

# Cleanup
if os.path.exists("test_structures.csv"):
    os.remove("test_structures.csv")
    