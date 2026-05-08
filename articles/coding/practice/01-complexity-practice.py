# Session 1: Complexity Analysis Practice
# For each function below, determine:
# 1. Time complexity
# 2. Space complexity
# 3. Why?

# --- Problem 1 ---
def sum_list(nums):
    total = 0
    for num in nums:
        total += num
    return total

# Your answer:
# Time:
# Space:
# Why:


# --- Problem 2 ---
def has_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

# Your answer:
# Time:
# Space:
# Why:


# --- Problem 3 ---
def print_pairs(nums):
    for i in range(len(nums)):
        for j in range(len(nums)):
            print(nums[i], nums[j])

# Your answer:
# Time:
# Space:
# Why:


# --- Problem 4 ---
def first_and_last(nums):
    return nums[0], nums[-1]

# Your answer:
# Time:
# Space:
# Why:


# --- Challenge ---
# Rewrite your original two_sum to be O(N) time.
# Use the hashmap approach from the article.

def two_sum(nums, target):
    # your code here
    pass


# Test
print(two_sum([2, 7, 11, 15], 9))   # expected: [0, 1]
print(two_sum([3, 2, 4], 6))         # expected: [1, 2]
