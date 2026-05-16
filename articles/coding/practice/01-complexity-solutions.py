# Solutions: 01-complexity-practice.py
#
# Read this AFTER you've attempted the practice problems yourself.
# Each solution explains the answer AND the reasoning — the reasoning
# is the part that matters in interviews.


# --- Problem 1 ---
def sum_list(nums):
    total = 0
    for num in nums:
        total += num
    return total

# Time:  O(N)
# Space: O(1)
#
# Why:
#   - Time: One loop that visits each of the N elements exactly once.
#           Each iteration does constant work (one addition).
#   - Space: Only `total` is allocated. Its size never grows with N.
#           The input itself doesn't count toward space complexity.
#
# Common mistake: Saying O(N) space because "there's a list of N elements."
# The input is given — you don't count it. You count what YOU allocate.


# --- Problem 2 ---
def has_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

# Time:  O(N)
# Space: O(N)
#
# Why:
#   - Time: One pass through the list. `in` on a set is O(1), and
#           `set.add()` is O(1), so each iteration is constant work.
#           Total = N iterations × O(1) work = O(N).
#   - Space: The set can grow up to N elements (worst case: no duplicates
#           found until the very end, or never found at all).
#
# Common mistake: Saying O(N²) time because "we check membership."
# Membership in a SET is O(1), not O(N). Membership in a LIST is O(N).
# This distinction is the entire reason hash-based structures exist.


# --- Problem 3 ---
def print_pairs(nums):
    for i in range(len(nums)):
        for j in range(len(nums)):
            print(nums[i], nums[j])

# Time:  O(N²)
# Space: O(1)
#
# Why:
#   - Time: Outer loop runs N times. For each outer iteration, the inner
#           loop runs N times. Total iterations = N × N = N².
#   - Space: No data structures are allocated. `print()` writes to stdout
#           but doesn't allocate memory that grows with N.
#
# Interview note: When you see nested loops over the same input, your
# first instinct should be "this is O(N²) — can I do better with a
# hash map or a sort?"


# --- Problem 4 ---
def first_and_last(nums):
    return nums[0], nums[-1]

# Time:  O(1)
# Space: O(1)
#
# Why:
#   - Time: Two index lookups. Python list indexing is O(1) regardless
#           of list size — it's direct memory access.
#   - Space: Returns a tuple of two references. Constant size.
#
# Common mistake: Saying O(N) because "we have a list of N elements."
# What matters is the WORK YOU DO, not the input size. You do constant
# work here, regardless of how big nums is.


# --- Challenge ---
def two_sum(nums, target):
    seen = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []  # no solution found

# Time:  O(N)
# Space: O(N)
#
# Why:
#   - Time: One pass through the list. For each element, a dict lookup
#           (`in seen`) is O(1) and a dict insert (`seen[num] = i`) is O(1).
#           Total = N × O(1) = O(N).
#   - Space: `seen` can grow to N entries in the worst case.
#
# The key insight: instead of looking for the complement by scanning the
# rest of the list (O(N) per element → O(N²) total), we store every value
# we've already seen and look up the complement in O(1).
#
# This is the foundational tradeoff: space for time. We added O(N) space
# to cut the time from O(N²) to O(N). For any reasonable N, this is worth it.


# --- Test the challenge solution ---
if __name__ == "__main__":
    print(two_sum([2, 7, 11, 15], 9))   # [0, 1]
    print(two_sum([3, 2, 4], 6))         # [1, 2]
    print(two_sum([1, 2, 3], 100))       # [] — no solution
