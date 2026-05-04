"""
Singly Linked List
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterator, Optional


@dataclass
class Node:
    value: Any
    next: Optional[Node] = field(default=None, repr=False)


class LinkedList:
    def __init__(self):
        self.head: Optional[Node] = None
        self._size: int = 0

    def append(self, value: Any) -> None:
        node = Node(value)
        if self.head is None:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node
        self._size += 1

    def prepend(self, value: Any) -> None:
        self.head = Node(value, self.head)
        self._size += 1

    def delete(self, value: Any) -> bool:
        cur = self.head
        prev = None
        while cur:
            if cur.value == value:
                if prev:
                    prev.next = cur.next
                else:
                    self.head = cur.next
                self._size -= 1
                return True
            prev, cur = cur, cur.next
        return False

    def search(self, value: Any) -> bool:
        return any(v == value for v in self)

    def reverse(self) -> None:
        prev, cur = None, self.head
        while cur:
            nxt = cur.next
            cur.next = prev
            prev, cur = cur, nxt
        self.head = prev

    def __iter__(self) -> Iterator:
        cur = self.head
        while cur:
            yield cur.value
            cur = cur.next

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return " → ".join(str(v) for v in self)


def remove_duplicates(ll: LinkedList) -> LinkedList:
    """Return a new linked list with duplicates removed (order preserved)."""
    seen = set()
    result = LinkedList()
    for v in ll:
        if v not in seen:
            seen.add(v)
            result.append(v)
    return result


if __name__ == "__main__":
    ll = LinkedList()
    for v in [1, 2, 3, 4, 5]:
        ll.append(v)
    print("List:    ", ll)
    print("Length:  ", len(ll))
    ll.prepend(0)
    print("Prepend: ", ll)
    ll.delete(3)
    print("Delete 3:", ll)
    ll.reverse()
    print("Reversed:", ll)

    dup = LinkedList()
    for v in [1, 2, 2, 3, 1, 4]:
        dup.append(v)
    print("\nWith dups:    ", dup)
    print("Without dups: ", remove_duplicates(dup))
