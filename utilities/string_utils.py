"""
String utility helpers
"""

import re
from collections import Counter


def slugify(text: str) -> str:
    """'Hello World!' → 'hello-world'"""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_]+", "-", text)


def truncate(text: str, max_len: int, suffix: str = "...") -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def count_words(text: str) -> dict[str, int]:
    words = re.findall(r"\b\w+\b", text.lower())
    return dict(Counter(words).most_common())


def is_palindrome(s: str) -> bool:
    cleaned = re.sub(r"[^a-z0-9]", "", s.lower())
    return cleaned == cleaned[::-1]


def camel_to_snake(name: str) -> str:
    """'camelCaseWord' → 'camel_case_word'"""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s).lower()


if __name__ == "__main__":
    print(slugify("Hello World! & Python"))
    print(truncate("The quick brown fox", 15))
    print(count_words("the cat sat on the mat the cat"))
    print(is_palindrome("A man a plan a canal Panama"))
    print(camel_to_snake("getUserByIdAndName"))
