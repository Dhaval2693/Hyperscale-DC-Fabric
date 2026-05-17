# Sliding Window

Sliding window is a special case of two pointers where both pointers move in the same direction, and you maintain some state about the elements *between* them (the "window").

If two pointers felt natural, sliding window is the next step: same idea, but the window expands and contracts based on a condition.

## When to Recognize It

Trigger phrases:
- "Subarray" or "substring"
- "Window of size K"
- "Maximum / minimum / longest / shortest of contiguous elements"
- "At most / at least K of something"

If the problem asks about a **contiguous chunk** of an array or string and wants something optimal, sliding window is usually the answer.

## Pattern 1: Fixed-Size Window

The window has a constant size K. You slide it one step at a time — add the new element on the right, remove the oldest on the left.

**Example: Maximum sum of subarray of size K.**

```python
def max_sum_window(nums, k):
    if len(nums) < k:
        return None

    # Sum of the first window
    window_sum = sum(nums[:k])
    max_sum = window_sum

    # Slide: add right, remove left
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)

    return max_sum
```

Time: **O(N)**, Space: **O(1)**.

**The trick:** instead of recomputing the sum from scratch for every window (O(K) per window → O(N×K) total), you do one add and one subtract per slide (O(1) per step). One initialization (O(K)) plus N-K slides (O(1) each) = **O(N) total**.

## Pattern 2: Variable-Size Window

The window grows and shrinks based on a condition. Expand the right pointer until the condition breaks, then shrink from the left until it's restored.

**Example: Longest substring without repeating characters.**

```python
def longest_unique_substring(s):
    seen = {}      # char → index of last occurrence
    left = 0
    max_len = 0

    for right, char in enumerate(s):
        if char in seen and seen[char] >= left:
            # Move left past the previous occurrence
            left = seen[char] + 1
        seen[char] = right
        max_len = max(max_len, right - left + 1)

    return max_len
```

Time: **O(N)**, Space: **O(K)** where K = alphabet size.

The invariant: the window `[left, right]` always contains only unique characters. When right hits a duplicate, left jumps past the old occurrence to restore the invariant.

## Recognizing the Two Sub-Patterns

| Problem says... | Use... |
|---|---|
| "Window of size K" / "Every K elements" | **Fixed-size** |
| "Longest / shortest where [condition] holds" | **Variable-size** |
| "At most K distinct" | **Variable-size** |
| "Average / sum of every K elements" | **Fixed-size** |

## How to Talk About It

State the **invariant** out loud. "The window `[left, right]` always contains [property]. When the property breaks, I shrink from left until it's restored."

Senior engineers state the invariant explicitly. Juniors just describe the code line by line.

## Why It's Still O(N) Despite the Nested Loop

Variable-size windows often have a `while` inside a `for`. It looks like O(N²), but it's actually O(N) because of **amortized analysis**:

- Right pointer advances N times total (the outer `for`)
- Left pointer advances at most N times total across the entire run (the inner `while`)
- Each element enters the window once and leaves at most once
- Total work: 2N = **O(N)**

This is a classic interview point — explaining why a nested-loop sliding window is still O(N) shows you understand amortized analysis.

## Common Gotchas

1. **Off-by-one on window size.** Window `[left, right]` (inclusive on both ends) has size `right - left + 1`. Easy to drop the +1.

2. **Forgetting to update state when shrinking.** When you move `left` past an element, that element has left the window — update any frequency counter or sum accordingly.

3. **Initializing wrong for fixed window.** Sum the first K, set as max, *then* start the loop from index K (not 0).

## The Bridge to Binary Search

Sliding window and two pointers both walk linearly through the data. Binary search instead **jumps** — eliminating half the search space at each step. That's the next topic.
