"""
Command-Line Interface (CLI) driver for the Baton Rouge Civic Analytics Lab (BRCAL) engine.
CMPS 201B Honors Project - Milestone 9
"""
import argparse
import os
import sys
from datetime import datetime
from src.ingest import load_and_clean_csv
from src.structures import CivicDataEngine
from src.bst import BinarySearchTree
from src.parallel import (
    single_process_category_counts,
    parallel_category_counts,
    run_benchmark,
)


def parse_cli_date(date_str: str) -> datetime:
    """Validates and parses YYYY-MM-DD dates from CLI arguments."""
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Expected YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="brcal-engine",
        description="Baton Rouge Civic Analytics Lab (BRCAL) Data Processing Engine",
    )
    parser.add_argument(
        "--file",
        default="data/civic_data.csv",
        help="Path to the input CSV dataset (default: data/civic_data.csv)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available analytics commands")

    # 1. summary
    subparsers.add_parser("summary", help="Display dataset overview, unique neighborhoods, and BST height")

    # 2. find-id
    id_parser = subparsers.add_parser("find-id", help="Lookup a specific record by ID (O(1) hash lookup)")
    id_parser.add_argument("record_id", help="The unique ID of the civic record")

    # 3. street
    street_parser = subparsers.add_parser("street", help="Search incidents along a street (O(n) scan)")
    street_parser.add_argument("street_name", help="Street name or partial street string")

    # 4. date-range
    range_parser = subparsers.add_parser("date-range", help="Query incidents between two dates via Custom BST (O(h + k))")
    range_parser.add_argument("start_date", help="Start date (YYYY-MM-DD)")
    range_parser.add_argument("end_date", help="End date (YYYY-MM-DD)")

    # 5. counts
    counts_parser = subparsers.add_parser("counts", help="Count incidents by category")
    counts_parser.add_argument(
        "--mp",
        action="store_true",
        help="Use multiprocessing across worker processes instead of single-process execution",
    )
    counts_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker processes when --mp is enabled (default: 4)",
    )

    # 6. benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Benchmark single-process vs. multiprocessing execution")
    bench_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker processes to benchmark (default: 4)",
    )

    args = parser.parse_args()

    # Validate file existence
    if not os.path.exists(args.file):
        print(f"Error: Dataset file not found at '{args.file}'.", file=sys.stderr)
        sys.exit(1)

    # Load and index data
    records, skipped = load_and_clean_csv(args.file)
    engine = CivicDataEngine(records)

    # --- Execute Commands ---
    if args.command == "summary":
        bst = BinarySearchTree()
        for r in records:
            bst.insert(r.incident_date, r)

        print("=== BRCAL Dataset Summary ===")
        print(f"Dataset File:         {args.file}")
        print(f"Valid Records Loaded: {len(records):,}")
        print(f"Skipped/Invalid Rows: {skipped:,}")
        print(f"Unique Categories:    {len(engine.by_category)}")
        print(f"Unique Neighborhoods: {len(engine.neighborhoods)}")
        print(f"Custom BST Height:    {bst.get_height()}")

    elif args.command == "find-id":
        rec = engine.find_by_id(args.record_id)
        if rec:
            print("=== Record Found ===")
            print(f"ID:           {rec.record_id}")
            print(f"Date:         {rec.incident_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Category:     {rec.category}")
            print(f"Street:       {rec.street}")
            print(f"Neighborhood: {rec.neighborhood}")
            print(f"Status:       {rec.status}")
        else:
            print(f"No record found with ID '{args.record_id}'.")

    elif args.command == "street":
        matches = engine.find_by_street(args.street_name)
        print(f"=== Incidents matching street '{args.street_name.upper()}' ({len(matches)} found) ===")
        for r in matches[:20]:  # Cap display at 20 rows for readability
            print(f"  [{r.record_id}] {r.incident_date.strftime('%Y-%m-%d')} | {r.category} | {r.street} ({r.status})")
        if len(matches) > 20:
            print(f"  ... and {len(matches) - 20} more records.")

    elif args.command == "date-range":
        start_dt = parse_cli_date(args.start_date)
        # Set end_dt to end of the specified day (23:59:59)
        end_dt = parse_cli_date(args.end_date).replace(hour=23, minute=59, second=59)

        if start_dt > end_dt:
            print("Error: start_date cannot be after end_date.", file=sys.stderr)
            sys.exit(1)

        bst = BinarySearchTree()
        for r in records:
            bst.insert(r.incident_date, r)

        matches = bst.range_search(start_dt, end_dt)
        print(f"=== BST Date-Range Query [{args.start_date} to {args.end_date}] ({len(matches)} found) ===")
        for r in matches[:20]:
            print(f"  [{r.record_id}] {r.incident_date.strftime('%Y-%m-%d')} | {r.category} | {r.neighborhood}")
        if len(matches) > 20:
            print(f"  ... and {len(matches) - 20} more records.")

    elif args.command == "counts":
        if args.mp:
            counts = parallel_category_counts(records, num_workers=args.workers)
            mode_label = f"Multiprocessing ({args.workers} workers)"
        else:
            counts = single_process_category_counts(records)
            mode_label = "Single-Process"

        print(f"=== Category Counts [{mode_label}] ===")
        for cat, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat:<25} {count:,}")

    elif args.command == "benchmark":
        if len(records) == 0:
            print("Error: Cannot benchmark an empty dataset.", file=sys.stderr)
            sys.exit(1)

        single_t, multi_t, matched = run_benchmark(records, num_workers=args.workers)
        print(f"=== Performance Benchmark ({len(records):,} records, {args.workers} workers) ===")
        print(f"Outputs Match:       {matched}")
        print(f"Single-Process Time: {single_t:.6f} sec")
        print(f"Multiprocessing Time:{multi_t:.6f} sec")
        if multi_t < single_t:
            print(f"Result:              {single_t / multi_t:.2f}x Speedup")
        else:
            print(f"Result:              {multi_t / single_t:.2f}x Slowdown (process spawn & IPC overhead)")


if __name__ == "__main__":
    main()