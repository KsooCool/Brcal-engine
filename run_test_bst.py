from datetime import datetime
from src.models import CivicRecord
from src.bst import BinarySearchTree

# Create mock records across various dates
records = [
    CivicRecord("1", datetime(2026, 3, 10, 12, 0), "Drainage", "Plank Rd", "North BR", "Open", {}),
    CivicRecord("2", datetime(2026, 3, 4, 10, 0), "Blight", "Florida St", "Downtown", "Closed", {}),
    CivicRecord("3", datetime(2026, 3, 18, 14, 0), "Traffic", "Scenic Hwy", "North BR", "Pending", {}),
    CivicRecord("4", datetime(2026, 3, 7, 9, 30), "Drainage", "Evangeline St", "Scotlandville", "Open", {}),
    CivicRecord("5", datetime(2026, 3, 12, 11, 0), "Blight", "Government St", "Mid City", "Open", {}),
]

tree = BinarySearchTree()
for rec in records:
    tree.insert(rec.incident_date, rec)

print(f"Total records in BST: {len(tree)}")
print(f"Tree Height: {tree.get_height()}")

# Test Range Query: All records between March 5 and March 15
start = datetime(2026, 3, 5)
end = datetime(2026, 3, 15)
matched = tree.range_search(start, end)

print(f"\nRange Query [2026-03-05 to 2026-03-15] found {len(matched)} records:")
for m in matched:
    print(f"  - ID: {m.record_id} | Date: {m.incident_date.strftime('%Y-%m-%d')} | Cat: {m.category}")