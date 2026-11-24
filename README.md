# Brcal-engine 
# BRCAL Civic Data Processing Engine (`brcal-engine`)

**CMPS 201B Honors Project** | Southern University and A&M College  
**Author:** Kimaathi Kweku Yeboah  
**Instructor:** Dr. Sheryl LaFleur  

## Overview
A modular civic data analytics engine built for the Baton Rouge Civic Analytics Lab (BRCAL) simulation. The engine ingests and cleans messy CSV datasets, constructs $O(1)$ hash map and set indexes, implements a custom Binary Search Tree (BST) from scratch for $O(h + k)$ date-range queries, and benchmarks single-process versus multiprocessing category aggregations.

## Project Structure
```text
Brcal-engine/
├── data/               # Civic dataset samples
├── docs/               # PRD, Design Review, Benchmarks, and Stakeholder reports
├── src/
│   ├── models.py       # CivicRecord dataclass schema
│   ├── ingest.py       # CSV ingestion, normalization, and validation pipeline
│   ├── structures.py   # Core in-memory indexes (list, dict, defaultdict, set)
│   ├── bst.py          # Custom BSTNode and BinarySearchTree range search
│   ├── parallel.py     # Multiprocessing chunking and performance benchmarking
│   └── cli.py          # Command-line interface driver
└── tests/
    └── test_engine.py  # Automated unittest validation suite