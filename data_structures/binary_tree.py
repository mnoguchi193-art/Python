"""
Binary Search Tree (BST)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterator, Optional


@dataclass
class TreeNode:
    value: Any
    left:  Optional[TreeNode] = field(default=None, repr=False)
    right: Optional[TreeNode] = field(default=None, repr=False)


class BinarySearchTree:
    def __init__(self):
        self.root: Optional[TreeNode] = None

    def insert(self, value: Any) -> None:
        self.root = self._insert(self.root, value)

    def _insert(self, node: Optional[TreeNode], value: Any) -> TreeNode:
        if node is None:
            return TreeNode(value)
        if value < node.value:
            node.left = self._insert(node.left, value)
        elif value > node.value:
            node.right = self._insert(node.right, value)
        return node  # duplicates ignored

    def search(self, value: Any) -> bool:
        node = self.root
        while node:
            if value == node.value:
                return True
            node = node.left if value < node.value else node.right
        return False

    def delete(self, value: Any) -> None:
        self.root = self._delete(self.root, value)

    def _delete(self, node: Optional[TreeNode], value: Any) -> Optional[TreeNode]:
        if node is None:
            return None
        if value < node.value:
            node.left = self._delete(node.left, value)
        elif value > node.value:
            node.right = self._delete(node.right, value)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Replace with in-order successor (min of right subtree)
            successor = node.right
            while successor.left:
                successor = successor.left
            node.value = successor.value
            node.right = self._delete(node.right, successor.value)
        return node

    def inorder(self) -> Iterator:
        yield from self._inorder(self.root)

    def _inorder(self, node: Optional[TreeNode]) -> Iterator:
        if node:
            yield from self._inorder(node.left)
            yield node.value
            yield from self._inorder(node.right)

    def preorder(self) -> Iterator:
        yield from self._preorder(self.root)

    def _preorder(self, node: Optional[TreeNode]) -> Iterator:
        if node:
            yield node.value
            yield from self._preorder(node.left)
            yield from self._preorder(node.right)

    def height(self) -> int:
        return self._height(self.root)

    def _height(self, node: Optional[TreeNode]) -> int:
        if node is None:
            return 0
        return 1 + max(self._height(node.left), self._height(node.right))

    def is_balanced(self) -> bool:
        def check(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            lh = check(node.left)
            if lh == -1:
                return -1
            rh = check(node.right)
            if rh == -1:
                return -1
            if abs(lh - rh) > 1:
                return -1
            return 1 + max(lh, rh)
        return check(self.root) != -1


if __name__ == "__main__":
    bst = BinarySearchTree()
    for v in [5, 3, 7, 1, 4, 6, 8]:
        bst.insert(v)
    print("Inorder: ", list(bst.inorder()))
    print("Preorder:", list(bst.preorder()))
    print("Height:  ", bst.height())
    print("Balanced:", bst.is_balanced())
    print("Search 4:", bst.search(4))
    bst.delete(3)
    print("After deleting 3:", list(bst.inorder()))
