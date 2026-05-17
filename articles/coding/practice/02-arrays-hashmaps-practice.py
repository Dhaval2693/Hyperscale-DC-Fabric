# Session 2: Arrays and Hash Maps Practice
#
# Each problem below maps to one of the four patterns from the article:
#   Pattern 1: Lookup Table
#   Pattern 2: Frequency Counting
#   Pattern 3: Deduplication
#   Pattern 4: Grouping
#
# For each problem:
#   1. Identify which pattern fits
#   2. Write the solution
#   3. State time and space complexity


# --- Problem 1: Deduplication ---
# Return True if the list contains any duplicate values.
#
# Example:
#   has_duplicate([1, 2, 3, 1])   -> True
#   has_duplicate([1, 2, 3, 4])   -> False

def has_duplicate(nums):
    # your code here
    duplicates = set()
    for num in nums:
        if num in duplicates:
            return True
        duplicates.add(num)
    return False

# Pattern used:
# Time: O(N)
# Space: O(N)


# --- Problem 2: Frequency Counting ---
# Given a list of strings (error types from a log), return the most common one.
#
# Example:
#   most_common(["timeout", "auth", "timeout", "auth", "timeout"])
#   -> "timeout"

def most_common(items):
    # your code here
    common = {}
    for item in items:
        if item in common:
            common[item] += 1
        else:
            common[item] = 1
    
    best_item = None
    best_count = 0
    for item, count in common.items():
        if count > best_count:
            best_count = count
            best_item = item
    return best_item
     
        

# Pattern used:
# Time: O(N)
# Space: O(K)


# --- Problem 3: Lookup Table ---
# Given a list of numbers, return True if any TWO numbers in the list
# add up to the target. This is Two Sum, but you only need a yes/no answer.
#
# Example:
#   has_pair_with_sum([1, 2, 3, 9], 8)    -> False
#   has_pair_with_sum([1, 2, 4, 4], 8)    -> True   (4 + 4)
#   has_pair_with_sum([10, 15, 3, 7], 17) -> True   (10 + 7)

def has_pair_with_sum(nums, target):
    # your code here
    seen = set()
    for num in nums:
        complement = target - num
        if complement in seen:
            return True
        seen.add(num)
    return False

# Pattern used:
# Time: O(N)
# Space: O(N)


# --- Problem 4: Frequency Counting (variant) ---
# Return the FIRST character in a string that appears exactly once.
# Return None if every character repeats.
#
# Example:
#   first_unique("leetcode")  -> "l"
#   first_unique("aabbcc")    -> None
#   first_unique("loveleet")  -> "v"

def first_unique(s):
    # your code here
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in s:
        if counts[ch] == 1:
            return ch 
    return None


# Pattern used:
# Time: O(N)
# Space: O(K)


# --- Problem 5: Grouping ---
# Given a list of words, group the anagrams together.
# Two words are anagrams if they contain the same letters in any order.
#
# Example:
#   group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
#   -> [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
#
# Order of groups and order within groups does not matter.

def group_anagrams(words):
    # your code here
    anagrams = {}
    for word in words:
        key = "".join(sorted(word))
        if key not in anagrams:
            anagrams[key] = []
        anagrams[key].append(word)
    return list(anagrams.values())


# Pattern used:
# Time:
# Space:


# --- Challenge: Bridge to Two Pointers ---
#
# Return ALL pairs of indices (i, j) where nums[i] + nums[j] == target and i < j.
# There may be multiple valid pairs. Return them as a list of tuples.
#
# Example:
#   all_pairs_with_sum([1, 5, 3, 7, 2, 4], 6)
#   -> [(0, 1), (4, 5)]
#   (Because: nums[0]+nums[1] = 1+5 = 6 ✓, and nums[4]+nums[5] = 2+4 = 6 ✓)
#
# Hint 1: A hash map gets you O(N) for the FIRST pair. To find ALL pairs efficiently
#         (especially with duplicate values), you may need a slightly different setup.
# Hint 2: This problem becomes much cleaner if the array is sorted — which is exactly
#         what the next concept (two pointers) is built for.

def all_pairs_with_sum(nums, target):
    # your code here
    all_pairs = []
    for index, num in enumerate(nums):
        complement = target - num
        if complement in nums[:index] + nums[index+1:]:
            complement_index = nums.index(complement)
            if index < complement_index:
                all_pairs.append((index, complement_index))
    return all_pairs



# --- Test your solutions ---
if __name__ == "__main__":
    print("Problem 1:", has_duplicate([1, 2, 3, 1]))                      # True
    print("Problem 1:", has_duplicate([1, 2, 3, 4]))                      # False
    print("Problem 2:", most_common(["timeout", "auth", "timeout"]))      # timeout
    print("Problem 3:", has_pair_with_sum([10, 15, 3, 7], 17))            # True
    print("Problem 4:", first_unique("leetcode"))                         # l
    print("Problem 5:", group_anagrams(["eat", "tea", "tan", "ate"]))     # [[eat,tea,ate],[tan]]
    print("Challenge:", all_pairs_with_sum([1, 5, 3, 7, 2, 4], 6))  # [(0,1), (4,5)]
