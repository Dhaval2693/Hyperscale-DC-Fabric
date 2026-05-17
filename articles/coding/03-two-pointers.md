# Two Pointers

You already met this pattern, sort of. In the arrays/hashmaps challenge, `all_pairs_with_sum` was clean with a hash map but got tangled with duplicate handling. If the array were sorted, two pointers would handle it without a hash map at all — and with O(1) space instead of O(N).

That's the trade two pointers offers: when the data is sorted (or you can sort it cheaply), you often replace a hash map with two index variables walking through the array. Less space, sometimes cleaner code.

This article covers the two main sub-patterns.

## Pattern 1: Opposite Ends (Sorted Arrays)

Place one pointer at the start, one at the end. Move them toward each other based on what you find.

**Example: Two Sum on a sorted array.**

```python
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        current = nums[left] + nums[right]
        if current == target:
            return [left, right]
        elif current < target:
            left += 1   # need bigger → move left up
        else:
            right -= 1  # need smaller → move right down
    return []
```

Time: **O(N)**, Space: **O(1)**. No hash map needed.

**Why it works:** if the sum is too small, the left value is the smallest in play; moving it up only helps. If too big, the right value is the largest in play; moving it down only helps. You never skip a valid pair, because you only eliminate values that can't be in any future pair.

## Pattern 2: Same Direction (Fast/Slow Pointers)

Two pointers move in the same direction at different speeds, or one waits while the other scouts ahead. Used for in-place array modification.

**Example: Remove duplicates from a sorted array, in-place.**

```python
def remove_duplicates(nums):
    if not nums:
        return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1   # new length
```

Time: **O(N)**, Space: **O(1)**.

The slow pointer marks "end of unique elements so far." Fast scans ahead for the next new value to write at slow+1.

## Recognizing Two Pointers in Interviews

Trigger phrases:

| If the problem says... | Use... |
|---|---|
| "Sorted array" + "find pair/triplet" | Opposite ends |
| "Palindrome" or "reverse" | Opposite ends |
| "In-place" or "without extra space" | Fast/slow |
| "Remove / partition / move" | Fast/slow |
| "Cycle in linked list" | Fast/slow (Floyd's algorithm) |

When you see "sorted" in a problem, your first instinct should be: *"Can I skip the hash map and use two pointers?"*

## Common Gotchas

1. **Off-by-one in the loop condition.** Use `while left < right` when you don't want the same index used twice (most cases).

2. **Forgetting to sort first.** Two pointers needs sorted input. The sort is O(N log N), so total complexity often becomes O(N log N), not O(N).

3. **Modifying the array while iterating.** Fast/slow is safe because you only write to positions the fast pointer has already passed. Other patterns may need a temp array.

## How to Talk About It

> "The array is sorted, so I'll use two pointers — one at each end. If the sum is too small, move left up; too big, move right down. This is O(N) time and O(1) space — better than the hash map version which uses O(N) space."

The phrase "two pointers" is recognized vocabulary. Saying it tells the interviewer you've seen this pattern before.

## The Bridge to Sliding Window

When the gap between your two pointers (the "window") expands or contracts based on a condition, you've moved from two pointers into **sliding window** territory. That's the next article.
