# Python Toolkit Cheat Sheet for Coding Interviews

Half of senior coding interviews come down to: *did you reach for the right data structure?* Knowing Python's built-in toolkit cold is the cheapest way to look like you know what you're doing.

This is your one-page reference. Read it once. Skim it before any coding round.

## The Seven Tools You Must Know

| Tool | Use when the problem mentions... | Why |
|---|---|---|
| `set` | "unique", "duplicates", "have I seen this?" | **O(1)** membership |
| `dict` | "lookup by value", "key → value" | **O(1)** key access |
| `Counter` | "most common", "frequency", "count occurrences" | Counts + `most_common()` |
| `defaultdict(list)` | "group by", "bucket by" | Auto-creates empty list |
| `deque` | "queue", "BFS", "sliding from both ends" | **O(1)** appends/pops on both ends |
| `heapq` | "top K", "Kth largest/smallest", "priority" | **O(log N)** priority queue |
| `bisect` | "search in sorted", "insertion point" | **O(log N)** binary search |

That's the whole list. Most interview problems use one or two of these.

---

## Quick Syntax Reference

### `set` — Membership
```python
s = set()
s.add(x)              # O(1)
s.remove(x)           # O(1) — raises KeyError if missing
s.discard(x)          # O(1) — safe (no error if missing)
x in s                # O(1)
```
**Use when:** you need to know "have I seen this before?" without caring about position or count.

### `dict` — Key/Value Lookup
```python
d = {}
d[key] = value        # O(1) write
d[key]                # O(1) read — KeyError if missing
d.get(key, default)   # O(1) safe read
key in d              # O(1)
for k, v in d.items():
    ...
```
**Use when:** you need to map one thing to another. The most common interview data structure.

### `collections.Counter` — Frequency Counting
```python
from collections import Counter
c = Counter("hello")          # Counter({'l': 2, 'h': 1, 'e': 1, 'o': 1})
c = Counter([1, 1, 2, 3])     # works on any iterable
c.most_common(2)              # [('l', 2), ('h', 1)] — top 2
c['x']                        # returns 0 if missing (NO KeyError)
```
**Use when:** you need to count how many times things appear. Replaces manual `if k in d: d[k] += 1 else: d[k] = 1`.

### `collections.defaultdict` — Auto-init Missing Keys
```python
from collections import defaultdict

# For grouping:
groups = defaultdict(list)
groups['anagram'].append('eat')   # auto-creates [] then appends

# For counting (alternative to Counter):
counts = defaultdict(int)
counts['x'] += 1                  # auto-creates 0 then adds
```
**Use when:** you'd otherwise write `if key not in d: d[key] = []`. The auto-init makes that boilerplate disappear.

### `collections.deque` — Double-Ended Queue
```python
from collections import deque
q = deque()
q.append(x)         # add right — O(1)
q.appendleft(x)     # add left  — O(1)
q.pop()             # remove right — O(1)
q.popleft()         # remove left  — O(1)
```
**Use when:** you need a FIFO queue. **Never use `list.pop(0)`** — it's O(N). The classic deque use case is BFS.

### `heapq` — Priority Queue (Min-Heap)
```python
import heapq
h = []
heapq.heappush(h, 5)     # O(log N)
heapq.heappop(h)         # returns smallest — O(log N)
heapq.heapify(lst)       # turn list into heap — O(N)
h[0]                     # peek smallest — O(1)
```
**Use when:** "top K", "Kth largest/smallest", "merge sorted lists", "scheduling by priority". For a **max-heap**, negate the values: `heappush(h, -value)`.

### `bisect` — Binary Search on Sorted List
```python
import bisect
sorted_list = [1, 3, 5, 7]
bisect.bisect_left(sorted_list, 4)    # 2 — where to insert 4
bisect.insort(sorted_list, 4)         # inserts 4 in place
```
**Use when:** you need binary search but don't want to write it yourself.

---

## How to Decide Which One (The Recognition Game)

When you read a problem, scan for these phrases and grab the matching tool:

| Problem phrase | Tool |
|---|---|
| "unique" / "duplicate" / "distinct" | `set` |
| "find a pair that..." / "complement" | `dict` or `set` (lookup table) |
| "most common" / "frequency" / "count" | `Counter` |
| "group anagrams" / "bucket by" | `defaultdict(list)` |
| "BFS" / "shortest path (unweighted)" / "level order" | `deque` |
| "queue" / "process in order received" | `deque` |
| "top K" / "K largest/smallest" | `heapq` |
| "median in a stream" | two `heapq`s (one min, one max) |
| "search in sorted" / "insert into sorted" | `bisect` |
| "anagram" / "permutation" | `sorted()` as key, or `Counter` |

---

## What to Memorize vs Look Up

**Memorize the names and use cases.** You should be able to say "I'd use `defaultdict(list)` here" without thinking. The interviewer can fill in syntax if you forget exact method names.

**Don't memorize exact syntax** for `heapq` and `bisect`. It's enough to say:

> "I'd use Python's `heapq` for the priority queue — push is O(log N), pop is O(log N)."

That's a passing answer. They won't quiz you on `heappush` vs `heappushpop`.

---

## The Mental Decision Tree

When facing a new problem, ask in order:

1. **Do I need to check "have I seen this"?** → `set`
2. **Do I need to look up by key?** → `dict`
3. **Am I counting things?** → `Counter`
4. **Am I grouping/bucketing things?** → `defaultdict(list)`
5. **Am I doing BFS or need O(1) queue ops?** → `deque`
6. **Do I need top K or priority ordering?** → `heapq`
7. **Is my data sorted and I need binary search?** → `bisect`

Walk down the list. The first match is usually the right tool.

---

## Bonus: String Methods Worth Knowing

```python
s.lower()              # case-insensitive comparisons
s.split(',')           # split into list
','.join(['a', 'b'])   # join list into string
s.isalnum()            # letter or digit?
s.isdigit()            # digit only?
s.startswith('prefix') # boolean
s.replace('a', 'b')    # all occurrences
s.strip()              # remove leading/trailing whitespace
```

## Bonus: List Operations and Their Costs

```python
lst.append(x)          # O(1) amortized
lst.pop()              # O(1)
lst.pop(0)             # O(N) — NEVER for queues; use deque
x in lst               # O(N) — use set for O(1)
lst.index(x)           # O(N) — only returns first occurrence
lst.count(x)           # O(N)
sorted(lst)            # O(N log N) — returns new list
lst.sort()             # O(N log N) — in-place
lst[a:b]               # O(b - a) — slice creates new list
```

**The trap:** `if x in lst` and `lst.pop(0)` are O(N). If you use them inside a loop, your O(N) algorithm silently becomes O(N²). When in doubt, swap `list` for `set` (membership) or `deque` (queue).

---

## Read This Before Every Coding Round

1. Scan the recognition table (5 min)
2. Re-skim the decision tree (1 min)
3. Walk into the room knowing you have a tool for every common pattern

That's the entire prep for "did you reach for the right data structure?"
