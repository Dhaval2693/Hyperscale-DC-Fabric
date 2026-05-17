# Session 3: Two Pointers Practice
#
# Patterns from the article:
#   Pattern 1: Opposite Ends (sorted array / palindrome)
#   Pattern 2: Same Direction (fast/slow)
#
# For each problem:
#   1. Identify which pattern fits
#   2. Write the solution
#   3. State time and space complexity


# --- Problem 1: Reverse a List In-Place ---
# Reverse a list of characters in place (modify, return nothing).
#
# Example:
#   s = ['h', 'e', 'l', 'l', 'o']
#   reverse_list(s)
#   s is now ['o', 'l', 'l', 'e', 'h']

def reverse_list(s):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 2: Valid Palindrome ---
# Return True if the string is a palindrome.
# Ignore non-alphanumeric characters and case.
#
# Example:
#   is_palindrome("A man, a plan, a canal: Panama") -> True
#   is_palindrome("race a car")                     -> False

def is_palindrome(s):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 3: Two Sum Sorted ---
# Given a SORTED array, return indices of two numbers that add up to target.
# Return (-1, -1) if no pair exists.
#
# Example:
#   two_sum_sorted([1, 3, 4, 5, 7, 11], 9) -> (1, 4)   (3 + 7 = 9)

def two_sum_sorted(nums, target):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 4: Remove Duplicates from Sorted Array ---
# Given a SORTED array, remove duplicates in-place. Return the new length.
# Modify the array so the first k elements are the unique values.
#
# Example:
#   nums = [1, 1, 2, 2, 3]
#   k = remove_duplicates(nums)
#   k is 3, nums starts with [1, 2, 3, _, _]

def remove_duplicates(nums):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 5: Move Zeros to End ---
# Move all zeros to the end while keeping the order of non-zero elements.
# Modify in-place.
#
# Example:
#   nums = [0, 1, 0, 3, 12]
#   move_zeros(nums)
#   nums is now [1, 3, 12, 0, 0]

def move_zeros(nums):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Challenge: Three Sum ---
# Return all unique triplets [a, b, c] where a + b + c == 0.
# No duplicate triplets in the result.
#
# Example:
#   three_sum([-1, 0, 1, 2, -1, -4])
#   -> [[-1, -1, 2], [-1, 0, 1]]
#
# Hint: Sort first. For each i, two-pointer search the rest for a pair
#       that sums to -nums[i]. Skip duplicates carefully at all three levels.

def three_sum(nums):
    # your code here
    pass


# --- Test your solutions ---
if __name__ == "__main__":
    s = ['h', 'e', 'l', 'l', 'o']
    reverse_list(s)
    print("Problem 1:", s)                                              # ['o', 'l', 'l', 'e', 'h']

    print("Problem 2:", is_palindrome("A man, a plan, a canal: Panama"))  # True
    print("Problem 2:", is_palindrome("race a car"))                    # False

    print("Problem 3:", two_sum_sorted([1, 3, 4, 5, 7, 11], 9))         # (1, 4)

    nums = [1, 1, 2, 2, 3]
    k = remove_duplicates(nums)
    print("Problem 4:", k, nums[:k])                                    # 3 [1, 2, 3]

    nums = [0, 1, 0, 3, 12]
    move_zeros(nums)
    print("Problem 5:", nums)                                           # [1, 3, 12, 0, 0]

    print("Challenge:", three_sum([-1, 0, 1, 2, -1, -4]))               # [[-1, -1, 2], [-1, 0, 1]]
