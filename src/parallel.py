"""
Multiprocessing module and benchmarking utilities for BRCAL Engine.
CMPS 201B Honors Project - Milestones 7 & 8
"""
import time
from collections import Counter
from multiprocessing import Pool
from typing import List, Dict, Tuple
from src.models import CivicRecord


def _worker_count_categories(records_chunk: List[CivicRecord]) -> Dict[str, int]:
    """
    Worker function executed by each child process.
    Counts categories within its assigned slice of records.
    """
    counts = Counter()
    for record in records_chunk:
        counts[record.category] += 1
    return dict(counts)


def single_process_category_counts(records: List[CivicRecord]) -> Dict[str, int]:
    """Baseline single-process implementation."""
    return _worker_count_categories(records)


def parallel_category_counts(records: List[CivicRecord], num_workers: int = 4) -> Dict[str, int]:
    """
    Splits records into chunks, processes them in parallel across worker processes,
    and merges the resulting dictionaries.
    """
    if not records:
        return {}

    # Ensure we don't spawn more workers than available records
    workers = min(num_workers, len(records))
    chunk_size = max(1, len(records) // workers)

    # Slice the master list into sub-lists
    chunks = [
        records[i : i + chunk_size]
        for i in range(0, len(records), chunk_size)
    ]

    # Spawn process pool and distribute chunks
    with Pool(processes=workers) as pool:
        partial_results = pool.map(_worker_count_categories, chunks)

    # Merge partial dictionaries back into a single total
    final_counts: Dict[str, int] = {}
    for partial in partial_results:
        for category, count in partial.items():
            final_counts[category] = final_counts.get(category, 0) + count

    return final_counts


def run_benchmark(records: List[CivicRecord], num_workers: int = 4) -> Tuple[float, float, bool]:
    """
    Benchmarks single-process vs. multiprocessing execution times.
    Returns: (single_time_sec, multi_time_sec, outputs_match)
    """
    # 1. Time Single Process
    start_single = time.perf_counter()
    single_res = single_process_category_counts(records)
    single_time = time.perf_counter() - start_single

    # 2. Time Multiprocessing
    start_multi = time.perf_counter()
    multi_res = parallel_category_counts(records, num_workers=num_workers)
    multi_time = time.perf_counter() - start_multi

    # 3. Verify identical output
    is_valid = (single_res == multi_res)

    return single_time, multi_time, is_valid