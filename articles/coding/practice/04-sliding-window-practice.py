# Session 4: Sliding Window Practice
#
# Patterns from the article:
#   Pattern 1: Fixed-Size Window
#   Pattern 2: Variable-Size Window


# --- Problem 1: Max Sum of K-Size Subarray (Fixed) ---
# Find the maximum sum of any contiguous subarray of size k.
#
# Example:
#   max_sum_window([2, 1, 5, 1, 3, 2], 3) -> 9   (5+1+3)

def max_sum_window(nums, k):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 2: Average of Every K-Size Subarray (Fixed) ---
# Return a list of averages of every contiguous subarray of size k.
#
# Example:
#   subarray_averages([1, 3, 2, 6, -1, 4, 1, 8, 2], 5)
#   -> [2.2, 2.8, 2.4, 3.6, 2.8]

def subarray_averages(nums, k):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 3: Longest Substring Without Repeating Characters (Variable) ---
# Return the length of the longest substring with all unique characters.
#
# Example:
#   longest_unique("abcabcbb") -> 3   ("abc")
#   longest_unique("bbbbb")    -> 1
#   longest_unique("pwwkew")   -> 3   ("wke")

def longest_unique(s):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 4: Longest Substring With At Most K Distinct (Variable) ---
# Return the length of the longest substring containing at most k distinct chars.
#
# Example:
#   longest_at_most_k_distinct("eceba", 2) -> 3   ("ece")
#   longest_at_most_k_distinct("aaaa", 1)  -> 4

def longest_at_most_k_distinct(s, k):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 5: Minimum Subarray Sum >= Target (Variable) ---
# Return the length of the smallest contiguous subarray whose sum >= target.
# Return 0 if no such subarray exists.
#
# Example:
#   min_subarray_sum([2, 3, 1, 2, 4, 3], 7) -> 2   ([4, 3])
#   min_subarray_sum([1, 1, 1, 1], 10)      -> 0

def min_subarray_sum(nums, target):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Challenge: Permutation in String ---
# Return True if any permutation of s1 is a substring of s2.
#
# Example:
#   check_permutation("ab", "eidbaooo") -> True    ("ba" is a permutation of "ab" and a substring)
#   check_permutation("ab", "eidboaoo") -> False
#
# Hint: Fixed window of size len(s1). Track character frequencies in the window
#       and compare to the frequency map of s1.

def check_permutation(s1, s2):
    # your code here
    pass


# --- Test your solutions ---
if __name__ == "__main__":
    print("Problem 1:", max_sum_window([2, 1, 5, 1, 3, 2], 3))                          # 9
    print("Problem 2:", subarray_averages([1, 3, 2, 6, -1, 4, 1, 8, 2], 5))             # [2.2, 2.8, 2.4, 3.6, 2.8]
    print("Problem 3:", longest_unique("abcabcbb"))                                     # 3
    print("Problem 3:", longest_unique("pwwkew"))                                       # 3
    print("Problem 4:", longest_at_most_k_distinct("eceba", 2))                         # 3
    print("Problem 5:", min_subarray_sum([2, 3, 1, 2, 4, 3], 7))                        # 2
    print("Challenge:", check_permutation("ab", "eidbaooo"))                            # True
    print("Challenge:", check_permutation("ab", "eidboaoo"))                            # False
