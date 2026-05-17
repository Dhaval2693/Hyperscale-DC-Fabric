# Solutions: 04-sliding-window-practice.py


# --- Problem 1: Max Sum of K-Size Subarray ---
def max_sum_window(nums, k):
    if len(nums) < k:
        return None
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum

# Pattern used: 1 (Fixed-Size Window)
# Time:  O(N)
# Space: O(1)
#
# Initialize the first window (O(K)). Slide by adding the new right element
# and subtracting the leaving left element (O(1) per slide). Total: O(N).


# --- Problem 2: Subarray Averages ---
def subarray_averages(nums, k):
    if len(nums) < k:
        return []
    window_sum = sum(nums[:k])
    result = [window_sum / k]
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        result.append(window_sum / k)
    return result

# Pattern used: 1 (Fixed-Size Window)
# Time:  O(N)
# Space: O(N) for the output (or O(1) extra if output isn't counted)


# --- Problem 3: Longest Substring Without Repeating Characters ---
def longest_unique(s):
    seen = {}      # char → index of last occurrence
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        if char in seen and seen[char] >= left:
            left = seen[char] + 1
        seen[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len

# Pattern used: 2 (Variable-Size Window)
# Time:  O(N)
# Space: O(K) where K = alphabet size
#
# Invariant: window [left, right] always contains unique chars.
# When right hits a duplicate, left jumps past the previous occurrence.
#
# The `seen[char] >= left` check matters — a previous occurrence that's
# already outside the window (before left) doesn't count as a duplicate.


# --- Problem 4: Longest Substring With At Most K Distinct ---
def longest_at_most_k_distinct(s, k):
    if k == 0:
        return 0
    counts = {}     # char → count in current window
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        counts[char] = counts.get(char, 0) + 1
        # Shrink while window has more than k distinct chars
        while len(counts) > k:
            counts[s[left]] -= 1
            if counts[s[left]] == 0:
                del counts[s[left]]
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len

# Pattern used: 2 (Variable-Size Window)
# Time:  O(N) — each char enters and exits the window at most once
# Space: O(K) for the counts dict
#
# The window's invariant: at most K distinct characters.
# When violated, shrink from left until restored.
# Removing a count of 0 from the dict is important — otherwise len(counts)
# would over-count distinct characters.


# --- Problem 5: Minimum Subarray Sum >= Target ---
def min_subarray_sum(nums, target):
    left = 0
    window_sum = 0
    min_len = float('inf')
    for right in range(len(nums)):
        window_sum += nums[right]
        # Shrink while we can still meet target
        while window_sum >= target:
            min_len = min(min_len, right - left + 1)
            window_sum -= nums[left]
            left += 1
    return 0 if min_len == float('inf') else min_len

# Pattern used: 2 (Variable-Size Window)
# Time:  O(N)
# Space: O(1)
#
# Different invariant flavor: the window expands until it meets the condition,
# then shrinks while STILL meeting it — recording the size at every step.


# --- Challenge: Permutation in String ---
def check_permutation(s1, s2):
    if len(s1) > len(s2):
        return False

    from collections import Counter
    s1_counts = Counter(s1)
    window_counts = Counter(s2[:len(s1)])

    if window_counts == s1_counts:
        return True

    for i in range(len(s1), len(s2)):
        # Slide: add new right, remove old left
        window_counts[s2[i]] += 1
        window_counts[s2[i - len(s1)]] -= 1
        if window_counts[s2[i - len(s1)]] == 0:
            del window_counts[s2[i - len(s1)]]
        if window_counts == s1_counts:
            return True

    return False

# Pattern used: 1 (Fixed-Size Window) with frequency tracking
# Time:  O(N) where N = len(s2)
# Space: O(K) for the Counter, K = alphabet size
#
# Two permutations of the same letters have identical frequency maps.
# Slide a window of length len(s1) through s2, comparing window's frequency
# map to s1's. If equal at any point, found a permutation.


if __name__ == "__main__":
    print("Problem 1:", max_sum_window([2, 1, 5, 1, 3, 2], 3))
    print("Problem 2:", subarray_averages([1, 3, 2, 6, -1, 4, 1, 8, 2], 5))
    print("Problem 3:", longest_unique("abcabcbb"))
    print("Problem 3:", longest_unique("pwwkew"))
    print("Problem 4:", longest_at_most_k_distinct("eceba", 2))
    print("Problem 5:", min_subarray_sum([2, 3, 1, 2, 4, 3], 7))
    print("Challenge:", check_permutation("ab", "eidbaooo"))
    print("Challenge:", check_permutation("ab", "eidboaoo"))
