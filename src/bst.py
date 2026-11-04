"""
Custom Binary Search Tree implementation for date-based range queries.
CMPS 201B Honors Project - Real-World Simulation
"""
from datetime import datetime
from typing import List, Optional
from src.models import CivicRecord


class BSTNode:
    """Represents a single node in the Binary Search Tree."""
    def __init__(self, key: datetime, record: CivicRecord):
        self.key: datetime = key
        # Handle duplicate dates by holding a list of records per node
        self.records: List[CivicRecord] = [record]
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None


class BinarySearchTree:
    """Custom BST supporting insertion, tree height calculation, and range search."""
    def __init__(self):
        self.root: Optional[BSTNode] = None
        self._size: int = 0

    def insert(self, key: datetime, record: CivicRecord) -> None:
        """Inserts a record using its datetime timestamp as the key."""
        if self.root is None:
            self.root = BSTNode(key, record)
            self._size += 1
        else:
            self._insert_recursive(self.root, key, record)

    def _insert_recursive(self, current: BSTNode, key: datetime, record: CivicRecord) -> None:
        if key == current.key:
            current.records.append(record)
            self._size += 1
        elif key < current.key:
            if current.left is None:
                current.left = BSTNode(key, record)
                self._size += 1
            else:
                self._insert_recursive(current.left, key, record)
        else:
            if current.right is None:
                current.right = BSTNode(key, record)
                self._size += 1
            else:
                self._insert_recursive(current.right, key, record)

    def search(self, key: datetime) -> List[CivicRecord]:
        """Exact match search: returns all records matching the exact timestamp."""
        node = self._search_recursive(self.root, key)
        return node.records if node else []

    def _search_recursive(self, current: Optional[BSTNode], key: datetime) -> Optional[BSTNode]:
        if current is None or current.key == key:
            return current
        if key < current.key:
            return self._search_recursive(current.left, key)
        return self._search_recursive(current.right, key)

    def range_search(self, start_date: datetime, end_date: datetime) -> List[CivicRecord]:
        """
        Retrieves all records with timestamps within [start_date, end_date].
        Runs in O(h + k) time by pruning branches outside the range window.
        """
        results: List[CivicRecord] = []
        self._range_recursive(self.root, start_date, end_date, results)
        return results

    def _range_recursive(
        self,
        current: Optional[BSTNode],
        start_date: datetime,
        end_date: datetime,
        results: List[CivicRecord],
    ) -> None:
        if current is None:
            return

        # Pruning optimization: only explore left if current key is strictly > start_date
        if current.key > start_date:
            self._range_recursive(current.left, start_date, end_date, results)

        # Collect records if within interval
        if start_date <= current.key <= end_date:
            results.extend(current.records)

        # Pruning optimization: only explore right if current key is strictly < end_date
        if current.key < end_date:
            self._range_recursive(current.right, start_date, end_date, results)

    def get_height(self) -> int:
        """Returns the maximum depth (height) of the tree."""
        return self._height_recursive(self.root)

    def _height_recursive(self, current: Optional[BSTNode]) -> int:
        if current is None:
            return 0
        left_h = self._height_recursive(current.left)
        right_h = self._height_recursive(current.right)
        return 1 + max(left_h, right_h)

    def __len__(self) -> int:
        return self._size