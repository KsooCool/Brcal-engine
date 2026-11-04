import os
from src.ingest import load_and_clean_csv

dummy_csv_content = """ID,Date,Category,Street,Neighborhood,Status
101,2026-03-04 10:15:00,blight,florida st,Downtown,Closed
102,2026-03-10 14:30:00,DRAINAGE,plank rd,North BR,Open
103,2026-03-18 09:00:00,traffic,scenic hwy,,Pending
104,,invalid_row,,,
"""

with open("test_sample.csv", "w") as f:
    f.write(dummy_csv_content.strip())

records, skipped = load_and_clean_csv("test_sample.csv")
print(f"Successfully loaded: {len(records)} records")
print(f"Skipped invalid rows: {skipped}")
for r in records:
    print(r, f"| Street: {r.street} | Area: {r.neighborhood}")

if os.path.exists("test_sample.csv"):
    os.remove("test_sample.csv")