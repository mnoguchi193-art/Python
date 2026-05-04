"""
Stack — LIFO data structure built on a Python list
"""


class Stack:
    def __init__(self):
        self._data = []

    def push(self, item) -> None:
        self._data.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._data[-1]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"Stack({self._data})"


def is_balanced(s: str) -> bool:
    """Check if brackets in `s` are balanced using a stack."""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = Stack()
    for ch in s:
        if ch in "([{":
            stack.push(ch)
        elif ch in ")]}":
            if stack.is_empty() or stack.pop() != pairs[ch]:
                return False
    return stack.is_empty()


if __name__ == "__main__":
    st = Stack()
    for v in [1, 2, 3]:
        st.push(v)
    print(st)
    print("peek:", st.peek())
    print("pop: ", st.pop())
    print(st)

    tests = ["({[]})", "([)]", "{[}", ""]
    for t in tests:
        print(f"  '{t}' balanced: {is_balanced(t)}")
