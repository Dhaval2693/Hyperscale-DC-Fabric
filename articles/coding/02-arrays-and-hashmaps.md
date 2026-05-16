# Arrays and Hash Maps

You already saw why hash maps matter. In the previous article, your Two Sum brute force was O(N²) — two nested loops, each scanning the array. The hash map version cut it to O(N) — one pass, with a constant-time lookup at each step. That single trick — trading space for time using a hash map — appears in more interview problems than any other technique.

This article goes deeper into why hash maps work, and shows the patterns built on top of them. By the end, you should be able to walk into an interview, recognize when a hash map is the right tool, and explain *why* without thinking.

## Why Arrays Are Limited

Arrays (Python lists) give you one superpower and one weakness.

**The superpower:** access by index is O(1). If you know the position, you get the value instantly.

```python
nums = [10, 20, 30, 40, 50]
print(nums[2])     # 30 — O(1), direct memory access
```

**The weakness:** searching for a value is O(N). The array doesn't know where any specific value lives. It has to scan element by element.

```python
nums = [10, 20, 30, 40, 50]
if 30 in nums:     # O(N) — Python checks every element
    print("found")
```

Your Two Sum brute force ran into exactly this weakness. For each element, you had to scan the rest of the array to find its complement. That scan is O(N), and you did it N times — hence O(N²).

A hash map fixes this. It gives you O(1) lookup by value, not just by index.

## How Hash Maps Work (Quick Intuition)

When you write `seen[num] = i`, Python doesn't just store the pair in a list. It computes a *hash* of `num` — a number derived from the value — and uses that hash to decide where in memory to store it. When you later ask `if complement in seen`, Python computes the hash of `complement` and jumps directly to that memory location.

No scanning. No comparison loop. Just compute-hash → jump-to-location → check.

That is why hash map operations (lookup, insert, delete) are O(1) — they bypass the search entirely.

The tradeoff: hash maps use extra memory. Your Two Sum hash map grew to hold up to N entries — O(N) space. You traded O(1) space + O(N²) time for O(N) space + O(N) time. In nearly every interview context, that trade is worth it.

## Python Hash Map Types

You will use three things from Python's standard library. Know what each is for.

**`dict`** — the basic hash map. Maps keys to values.
```python
counts = {}
counts["bgp_error"] = 5
counts["bgp_error"] += 1   # now 6
```

**`set`** — a hash map with no values, only keys. Use it when you only care about *whether* something exists.
```python
seen_ips = set()
seen_ips.add("10.0.0.1")
if "10.0.0.1" in seen_ips:   # O(1)
    print("duplicate")
```

**`collections.Counter`** — a dict subclass specialized for counting.
```python
from collections import Counter
errors = ["timeout", "auth", "timeout", "timeout", "auth"]
counts = Counter(errors)
# Counter({'timeout': 3, 'auth': 2})
print(counts.most_common(1))   # [('timeout', 3)]
```

**`collections.defaultdict`** — a dict that auto-initializes missing keys. Saves you from writing `if key not in d: d[key] = []` constantly.
```python
from collections import defaultdict
groups = defaultdict(list)
groups["spine"].append("spine-01")   # no KeyError, list auto-created
groups["spine"].append("spine-02")
# {'spine': ['spine-01', 'spine-02']}
```

## The Four Patterns You Will See in Interviews

Almost every hash map interview problem fits one of these four patterns. Recognize the pattern, you've solved the problem.

### Pattern 1: Lookup Table (Two Sum)

You scan the array once. For each element, you check if its "complement" (something derived from it) has already been seen. If yes, you've found your answer. If no, you record the current element for future lookups.

```python
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
```

**Why this matters:** The pattern generalizes. Any problem that says "find two things that together satisfy condition X" can usually be solved this way — store what you've seen, look up what you need.

### Pattern 2: Frequency Counting

Count how many times each element appears. Once you have the counts, the answer falls out.

```python
from collections import Counter

def first_unique_char(s):
    """Return index of first character that appears exactly once."""
    counts = Counter(s)
    for i, ch in enumerate(s):
        if counts[ch] == 1:
            return i
    return -1
```

Two passes: one to count, one to find. Both O(N). This is the right shape for any problem asking "first/most/least frequent thing."

### Pattern 3: Deduplication

You need to know whether you've seen something before. Use a `set`.

```python
def has_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False
```

This is O(N) instead of the naive O(N²). Any problem that says "are there any repeats" or "remove duplicates" wants a set.

### Pattern 4: Grouping

Group elements by some computed key. Use a `defaultdict`.

```python
from collections import defaultdict

def group_anagrams(words):
    """Group words that are anagrams of each other."""
    groups = defaultdict(list)
    for word in words:
        key = "".join(sorted(word))   # canonical form
        groups[key].append(word)
    return list(groups.values())
```

The trick is choosing the right key. For anagrams, it's the sorted letters. For "group IPs by subnet," it's the subnet prefix. The hash map handles the rest.

## Recognizing the Hash Map Signal in an Interview

When you read a problem, these phrases should make you think "hash map":

- "find two/three things that..." → lookup table
- "count occurrences of..." → frequency counting
- "find the most/least common..." → frequency counting
- "are there duplicates..." → deduplication
- "first non-repeating..." → frequency counting
- "group by..." → grouping with defaultdict
- "have we seen this before..." → set

If your brute-force solution is "for each element, scan the array again," that's the signal to ask whether a hash map can replace the inner scan.

## What Interviewers Actually Want to Hear

When you arrive at the hash map solution, *state the tradeoff*. Don't just say "I'll use a hash map." Say:

> "The brute force is O(N²) because of the nested scan. I can trade space for time using a hash map — store each value as I see it, then each lookup is O(1) instead of O(N). That makes the whole thing O(N) time and O(N) space."

That single sentence shows you understand both the optimization and the cost. It's what separates engineers who memorized the solution from engineers who understand it.

The practice file works through these four patterns one problem at a time. The challenge at the end starts to bridge into the next concept — two pointers — which is the second most common interview pattern after hash maps.
