"""
collections module — Counter, defaultdict, OrderedDict, namedtuple, deque
"""

from collections import Counter, defaultdict, OrderedDict, namedtuple, deque

# ── Counter ───────────────────────────────────────────────────────────────
text = "the quick brown fox jumps over the lazy dog"
word_freq = Counter(text.split())
print("Top 3 words:", word_freq.most_common(3))

char_freq = Counter(text.replace(" ", ""))
print("Top 5 chars:", char_freq.most_common(5))

# ── defaultdict ───────────────────────────────────────────────────────────
words_by_letter: defaultdict = defaultdict(list)
for word in text.split():
    words_by_letter[word[0]].append(word)
print("\nWords by first letter:")
for letter in sorted(words_by_letter)[:4]:
    print(f"  {letter}: {words_by_letter[letter]}")

# ── OrderedDict — LRU cache pattern ──────────────────────────────────────
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._cache: OrderedDict = OrderedDict()

    def get(self, key):
        if key not in self._cache:
            return -1
        self._cache.move_to_end(key)
        return self._cache[key]

    def put(self, key, value) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)

cache = LRUCache(3)
for k, v in [(1, "a"), (2, "b"), (3, "c")]:
    cache.put(k, v)
cache.get(1)       # access key 1 → moves to end
cache.put(4, "d")  # evicts key 2 (least recently used)
print("\nLRU cache after operations:", dict(cache._cache))

# ── namedtuple ───────────────────────────────────────────────────────────
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(f"\nPoint: {p}, distance from origin: {(p.x**2 + p.y**2)**0.5:.2f}")

# ── deque — sliding window ────────────────────────────────────────────────
readings = [1, 3, 5, 2, 4, 6, 8, 7]
window_size = 3
window: deque = deque(maxlen=window_size)
averages = []
for r in readings:
    window.append(r)
    if len(window) == window_size:
        averages.append(sum(window) / window_size)
print("\nSliding window averages:", averages)
