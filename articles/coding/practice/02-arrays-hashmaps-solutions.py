# Solutions: 02-arrays-hashmaps-practice.py
#
# Read this AFTER attempting the practice problems. The "why" matters
# more than the answer — interviewers ask you to explain, not just code.


# --- Problem 1: Deduplication ---
def has_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

# Pattern used: 3 (Deduplication)
# Time:  O(N)
# Space: O(N)
#
# Why:
#   - One pass through nums. Set membership (`in`) and insert are both O(1).
#   - The set can grow to N elements in the worst case (no duplicates).
#   - Early exit: returns True the moment a duplicate is found, so best
#     case is O(1) if the first two elements are the same.
#
# Alternative one-liner:
#   return len(set(nums)) != len(nums)
# Same complexity, but it always builds the full set — no early exit.
# Less efficient for inputs with early duplicates.
#
# Common mistake: Using a list instead of a set. `if num in my_list` is O(N),
# which makes the whole thing O(N²). The set is the entire point.


# --- Problem 2: Frequency Counting ---
from collections import Counter

def most_common(items):
    counts = Counter(items)
    return counts.most_common(1)[0][0]

# Pattern used: 2 (Frequency Counting)
# Time:  O(N)
# Space: O(K) where K = number of unique items (worst case K = N)
#
# Why:
#   - Counter(items) is O(N) — one pass to count each item.
#   - most_common(1) is O(K log K) in general, but for k=1 it's O(K).
#   - For interview purposes: O(N) total.
#
# Manual version (if you can't use Counter):
#   counts = {}
#   for item in items:
#       counts[item] = counts.get(item, 0) + 1
#   return max(counts, key=counts.get)
#
# Same complexity. Know both — sometimes interviewers ask you not to use
# library helpers to make sure you understand the underlying logic.


# --- Problem 3: Lookup Table ---
def has_pair_with_sum(nums, target):
    seen = set()
    for num in nums:
        complement = target - num
        if complement in seen:
            return True
        seen.add(num)
    return False

# Pattern used: 1 (Lookup Table)
# Time:  O(N)
# Space: O(N)
#
# Why:
#   - For each element, ask: "have I seen its complement already?"
#   - Set lookup is O(1), so the whole pass is O(N).
#   - The set can grow to N elements.
#
# Note: For has_pair_with_sum([1, 2, 4, 4], 8), the trick is that the second
# 4 finds the first 4 in the set — so this works for "pair where both values
# are equal" only if the value appears at least twice. The order of "check
# THEN add" matters: if you added first, the same element would match itself.
#
# Common mistake: Using a dict to store index too. You don't need the index
# here — only yes/no. Use the simplest structure that answers the question.


# --- Problem 4: Frequency Counting (variant) ---
def first_unique(s):
    counts = Counter(s)
    for ch in s:
        if counts[ch] == 1:
            return ch
    return None

# Pattern used: 2 (Frequency Counting)
# Time:  O(N)
# Space: O(K) where K = unique characters (bounded by alphabet size,
#        so effectively O(1) for ASCII inputs)
#
# Why:
#   - First pass: count every character → O(N).
#   - Second pass: find the first character with count 1 → O(N).
#   - Two passes of O(N) = O(N) total. Constants don't matter.
#
# Critical insight: WHY two passes?
#   You need to know the FINAL count before deciding "is this unique?"
#   A single pass can't tell you whether 'l' is unique until you've seen
#   the whole string. So count first, then decide.
#
# Common mistake: Trying to do it in one pass with a dict that tracks
# "is this still unique?" — it gets messy and isn't faster. Two clean
# passes beats one tangled pass every time.


# --- Problem 5: Grouping ---
from collections import defaultdict

def group_anagrams(words):
    groups = defaultdict(list)
    for word in words:
        key = "".join(sorted(word))  # canonical form: sorted letters
        groups[key].append(word)
    return list(groups.values())

# Pattern used: 4 (Grouping)
# Time:  O(N * M log M) where N = number of words, M = average word length
# Space: O(N * M) for the groups dict
#
# Why:
#   - For each of N words, sorting takes O(M log M).
#   - Dict insert is O(M) (hashing the key, which is M chars long).
#   - Total: O(N * M log M).
#
# The key choice: SORTED LETTERS as the canonical form.
#   "eat" → "aet"
#   "tea" → "aet"
#   "ate" → "aet"
#   All three hash to the same key → grouped together automatically.
#
# Alternative key: a tuple of letter counts (avoids sorting).
#   key = tuple(sorted(Counter(word).items()))
# Same idea, slightly different tradeoff. Sorting the word is simpler.
#
# Common mistake: Using a list as the dict key — lists aren't hashable.
# Tuples and strings are. That's why we join the sorted chars into a string.


# --- Challenge: Bridge to Two Pointers ---
def all_pairs_with_sum(nums, target):
    indices = defaultdict(list)  # value -> all indices where it appears
    pairs = []
    for i, num in enumerate(nums):
        complement = target - num
        for j in indices[complement]:
            pairs.append((j, i))
        indices[num].append(i)
    return pairs

# Time:  O(N + P) where P = number of pairs found (worst case O(N²) if
#        nearly every element pairs with every other)
# Space: O(N) for the indices dict
#
# Why this is awkward:
#   The simple `seen = {value: index}` from Problem 3 doesn't work because
#   it only stores ONE index per value. With duplicates like [3, 3, 3] and
#   target=6, you'd miss pairs.
#
#   The fix is to store ALL indices for each value (defaultdict(list)).
#   Then for each new element, walk every previous occurrence of its
#   complement and emit a pair.
#
#   This works, but notice it's no longer "clean O(N)" — finding all pairs
#   is fundamentally limited by how many pairs exist.
#
# Why this motivates the next topic:
#   If you SORT the array first, you can use TWO POINTERS (one from each
#   end, moving inward) and solve this without any hash map at all.
#   Sorting costs O(N log N), but then the two-pointer scan is O(N).
#   Total: O(N log N) time, O(1) extra space.
#
#   For "all pairs" type problems, two pointers is usually cleaner than
#   hash maps. The next article covers exactly this.


# --- Verify your work ---
if __name__ == "__main__":
    print("Problem 1:", has_duplicate([1, 2, 3, 1]))                       # True
    print("Problem 1:", has_duplicate([1, 2, 3, 4]))                       # False
    print("Problem 2:", most_common(["timeout", "auth", "timeout"]))       # timeout
    print("Problem 3:", has_pair_with_sum([10, 15, 3, 7], 17))             # True
    print("Problem 3:", has_pair_with_sum([1, 2, 4, 4], 8))                # True
    print("Problem 4:", first_unique("leetcode"))                          # l
    print("Problem 4:", first_unique("aabbcc"))                            # None
    print("Problem 5:", group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
    # → [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]  (order may vary)
    print("Challenge:", all_pairs_with_sum([1, 5, 3, 7, 2, 4], 6))         # [(0, 1), (4, 5)]
    print("Challenge:", all_pairs_with_sum([3, 3, 3], 6))                  # [(0, 1), (0, 2), (1, 2)]
