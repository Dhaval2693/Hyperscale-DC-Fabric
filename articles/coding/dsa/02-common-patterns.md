# Common Coding Patterns for Technical Interviews

Technical interviews for senior engineering roles at companies like LinkedIn often include a coding component. The problems are rarely network-specific — they test general problem-solving ability using standard data structures and algorithms. This article covers the patterns that appear most frequently, with clean Python implementations you can practice from.

## Pattern 1: Sliding Window

**What it solves:** Problems involving a contiguous subarray or substring that optimizes some condition.

**Network analogy:** Finding the time window with maximum packet rate. Detecting burst traffic patterns in a series of per-second byte counts.

```python
def max_traffic_in_window(byte_counts: list[int], window_size: int) -> int:
    """
    Find the maximum total bytes in any window_size-second window.
    byte_counts[i] = bytes received in second i.
    """
    if len(byte_counts) < window_size:
        return sum(byte_counts)

    # Initialize the first window
    window_sum = sum(byte_counts[:window_size])
    max_sum = window_sum

    # Slide the window: add next element, remove first element
    for i in range(window_size, len(byte_counts)):
        window_sum += byte_counts[i]
        window_sum -= byte_counts[i - window_size]
        max_sum = max(max_sum, window_sum)

    return max_sum

# Find longest substring without repeating characters
# (more classic interview version)
def length_of_longest_substring(s: str) -> int:
    char_index = {}
    left = 0
    max_len = 0

    for right, char in enumerate(s):
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1
        char_index[char] = right
        max_len = max(max_len, right - left + 1)

    return max_len
```

**Time complexity:** O(n). **Space complexity:** O(k) where k is window size or alphabet size.

## Pattern 2: Two Pointers

**What it solves:** Finding pairs or partitioning arrays in linear time. Works on sorted arrays or strings.

**Network analogy:** Finding two prefixes in a sorted list that together cover a target range. Partitioning hosts by subnet.

```python
def two_sum_sorted(numbers: list[int], target: int) -> tuple[int, int]:
    """
    Find two indices (1-indexed) where numbers[i] + numbers[j] == target.
    Input is sorted. Returns (-1, -1) if no solution.
    """
    left, right = 0, len(numbers) - 1

    while left < right:
        current_sum = numbers[left] + numbers[right]
        if current_sum == target:
            return (left + 1, right + 1)  # 1-indexed
        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return (-1, -1)

def three_sum(nums: list[int]) -> list[list[int]]:
    """Find all unique triplets that sum to zero."""
    nums.sort()
    result = []

    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue  # Skip duplicates
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left+1]:
                    left += 1  # Skip duplicates
                while left < right and nums[right] == nums[right-1]:
                    right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return result
```

## Pattern 3: Hash Map / Frequency Count

**What it solves:** Problems requiring fast lookup, counting occurrences, grouping elements.

**Network analogy:** Counting occurrences of each error type in a log. Finding the most common source IP in traffic data.

```python
from collections import Counter, defaultdict

def most_common_source_ips(log_entries: list[str], top_n: int = 10) -> list[tuple[str, int]]:
    """
    Find the top N source IPs by request count from a log list.
    Each entry is like "192.168.1.1 GET /api/v1/health 200"
    """
    source_ips = [entry.split()[0] for entry in log_entries if entry]
    counter = Counter(source_ips)
    return counter.most_common(top_n)

def group_anagrams(strs: list[str]) -> list[list[str]]:
    """Group strings that are anagrams of each other."""
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))  # Sorted characters as canonical key
        groups[key].append(s)
    return list(groups.values())

def subarray_sum_equals_k(nums: list[int], k: int) -> int:
    """Count subarrays that sum to k. Classic prefix sum + hash map."""
    count = 0
    prefix_sum = 0
    seen = defaultdict(int)
    seen[0] = 1  # Empty subarray has sum 0

    for num in nums:
        prefix_sum += num
        count += seen[prefix_sum - k]  # If (prefix_sum - k) was seen before, valid subarray exists
        seen[prefix_sum] += 1

    return count
```

## Pattern 4: Binary Search

**What it solves:** Searching a sorted array in O(log n). Also applicable to "search in answer space" problems.

**Network analogy:** Finding a prefix in a sorted routing table. Binary search on a time range to find when a metric exceeded a threshold.

```python
import bisect

def find_prefix(routing_table: list[str], target: str) -> int:
    """Binary search in a sorted list of IP prefixes."""
    idx = bisect.bisect_left(routing_table, target)
    if idx < len(routing_table) and routing_table[idx] == target:
        return idx
    return -1

def min_days_to_achieve_target(required: list[int], supply: list[int]) -> int:
    """
    Minimum number of days to supply all required amounts.
    Each day produces supply[day] units. Find minimum days.
    """
    def can_meet_by_day(days: int) -> bool:
        total = sum(supply[:days])
        return total >= sum(required)

    left, right = 1, len(supply)
    while left < right:
        mid = (left + right) // 2
        if can_meet_by_day(mid):
            right = mid
        else:
            left = mid + 1
    return left

# Standard binary search template
def binary_search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1  # Not found
```

## Pattern 5: Stack-Based Problems

**What it solves:** Problems with nested structures, "next greater element," and monotonic sequences.

**Network analogy:** Parsing nested configuration blocks. Finding the next higher-metric route in a list.

```python
def valid_parentheses(s: str) -> bool:
    """Check if bracket string is valid."""
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for char in s:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    return len(stack) == 0

def next_greater_element(nums: list[int]) -> list[int]:
    """
    For each element, find the next greater element to its right.
    Returns -1 if none exists.
    Uses monotonic stack (decreasing).
    """
    result = [-1] * len(nums)
    stack = []  # Indices

    for i, num in enumerate(nums):
        # Pop elements smaller than current — current is their "next greater"
        while stack and nums[stack[-1]] < num:
            idx = stack.pop()
            result[idx] = num
        stack.append(i)

    return result
```

## Pattern 6: Dynamic Programming

**What it solves:** Optimization problems with overlapping subproblems. "What is the maximum/minimum/number-of-ways?"

```python
def longest_common_subsequence(s1: str, s2: str) -> int:
    """Classic DP. Useful for diff-like operations (config diff)."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return dp[m][n]

def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    """0/1 knapsack — maximize value within weight limit."""
    n = len(weights)
    dp = [0] * (capacity + 1)

    for i in range(n):
        for w in range(capacity, weights[i] - 1, -1):  # Traverse backwards
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])

    return dp[capacity]
```

## Interview Approach — The Framework

Regardless of the specific problem, use this framework in the interview:

1. **Clarify (2 min):** Input format? Edge cases? Constraints on size? Return type?
2. **Example (1 min):** Walk through a small example by hand.
3. **Approach (2 min):** Describe your approach before coding. Name the pattern. State time/space complexity.
4. **Code (10-15 min):** Write clean, readable code. Name variables well.
5. **Test (3 min):** Walk through your example, test edge cases (empty input, single element, already sorted).
6. **Optimize (if time):** Can you do better? Usually: can you reduce from O(n²) to O(n log n) or O(n)?

**The thing senior engineers do differently:** They explain the tradeoff, not just the solution. "I'll use a hash map for O(1) lookup at the cost of O(n) space, versus a sorted array with O(log n) lookup and O(1) space — given the problem size, the hash map is worth it."
