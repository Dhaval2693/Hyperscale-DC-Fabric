# Session 5: Binary Search Practice
#
# Patterns from the article:
#   Pattern 1: Find a Target (classic)
#   Pattern 2: Find a Boundary (first/last occurrence)
#   Pattern 3: Binary Search on the Answer


# --- Problem 1: Standard Binary Search ---
# Find the index of target in a sorted array. Return -1 if not found.
#
# Example:
#   binary_search([1, 3, 5, 7, 9, 11], 7) -> 3
#   binary_search([1, 3, 5, 7, 9, 11], 4) -> -1

def binary_search(nums, target):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 2: First Occurrence of Target ---
# Find the INDEX of the first occurrence of target in a sorted array
# (which may contain duplicates). Return -1 if not found.
#
# Example:
#   first_occurrence([1, 2, 2, 2, 3, 4], 2) -> 1
#   first_occurrence([1, 2, 2, 2, 3, 4], 5) -> -1

def first_occurrence(nums, target):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 3: Find Insert Position ---
# Given a sorted array with no duplicates, return the index where target
# would be inserted to keep it sorted. If target is found, return its index.
#
# Example:
#   search_insert([1, 3, 5, 6], 5) -> 2
#   search_insert([1, 3, 5, 6], 2) -> 1
#   search_insert([1, 3, 5, 6], 7) -> 4

def search_insert(nums, target):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 4: Find Peak Element ---
# A peak is an element strictly greater than its neighbors.
# Return the INDEX of any peak. You may assume nums[-1] = nums[N] = -inf.
# Must run in O(log N) time.
#
# Example:
#   find_peak([1, 2, 3, 1])       -> 2   (3 is a peak)
#   find_peak([1, 2, 1, 3, 5, 6, 4]) -> 1 or 5

def find_peak(nums):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 5: Search in Rotated Sorted Array ---
# A sorted array has been rotated at some pivot point.
# Find the index of target. Return -1 if not found. Must be O(log N).
#
# Example:
#   search_rotated([4, 5, 6, 7, 0, 1, 2], 0) -> 4
#   search_rotated([4, 5, 6, 7, 0, 1, 2], 3) -> -1

def search_rotated(nums, target):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Challenge: Capacity to Ship Packages Within D Days ---
# Find the minimum truck capacity such that all packages can be delivered
# within `days` days. Packages must be delivered in order (no reordering).
#
# Example:
#   min_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5)  -> 15
#   min_capacity([3, 2, 2, 4, 1, 4], 3)                -> 6
#
# Hint: Binary search on the answer (capacity). The range is
#       [max(packages), sum(packages)]. For each midpoint, check if
#       that capacity can deliver everything within `days`.

def min_capacity(packages, days):
    # your code here
    pass


# --- Test your solutions ---
if __name__ == "__main__":
    print("Problem 1:", binary_search([1, 3, 5, 7, 9, 11], 7))                # 3
    print("Problem 1:", binary_search([1, 3, 5, 7, 9, 11], 4))                # -1
    print("Problem 2:", first_occurrence([1, 2, 2, 2, 3, 4], 2))              # 1
    print("Problem 2:", first_occurrence([1, 2, 2, 2, 3, 4], 5))              # -1
    print("Problem 3:", search_insert([1, 3, 5, 6], 5))                       # 2
    print("Problem 3:", search_insert([1, 3, 5, 6], 2))                       # 1
    print("Problem 4:", find_peak([1, 2, 3, 1]))                              # 2
    print("Problem 5:", search_rotated([4, 5, 6, 7, 0, 1, 2], 0))             # 4
    print("Problem 5:", search_rotated([4, 5, 6, 7, 0, 1, 2], 3))             # -1
    print("Challenge:", min_capacity([1,2,3,4,5,6,7,8,9,10], 5))              # 15
    print("Challenge:", min_capacity([3,2,2,4,1,4], 3))                       # 6
