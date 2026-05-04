"""
Queue and PriorityQueue
-----------------------
Queue        — FIFO, backed by collections.deque for O(1) enqueue/dequeue
PriorityQueue — min-heap backed by heapq
"""

from collections import deque
import heapq


class Queue:
    def __init__(self):
        self._data: deque = deque()

    def enqueue(self, item) -> None:
        self._data.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._data.popleft()

    def front(self):
        if self.is_empty():
            raise IndexError("front of empty queue")
        return self._data[0]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"Queue({list(self._data)})"


class PriorityQueue:
    """Min-priority queue — lowest priority value is dequeued first."""

    def __init__(self):
        self._heap = []
        self._counter = 0  # tie-breaker

    def push(self, item, priority: int | float) -> None:
        heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1

    def pop(self):
        if not self._heap:
            raise IndexError("pop from empty priority queue")
        _, _, item = heapq.heappop(self._heap)
        return item

    def peek(self):
        if not self._heap:
            raise IndexError("peek at empty priority queue")
        return self._heap[0][2]

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)


if __name__ == "__main__":
    q = Queue()
    for task in ["task1", "task2", "task3"]:
        q.enqueue(task)
    print(q)
    while not q.is_empty():
        print("dequeue:", q.dequeue())

    pq = PriorityQueue()
    pq.push("low-priority",    10)
    pq.push("critical",         1)
    pq.push("medium-priority",  5)
    print("\nPriority order:")
    while not pq.is_empty():
        print(" ", pq.pop())
