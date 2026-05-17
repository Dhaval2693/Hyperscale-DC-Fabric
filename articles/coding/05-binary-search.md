# Binary Search

If a problem mentions "sorted" and asks you to find something, binary search is almost always the answer. It cuts O(N) search down to **O(log N)** by halving the search space at each step.

You already met `log N` in the complexity article. Binary search is the canonical example — and it's one of the few algorithms interviewers expect you to write correctly from memory.

## The Core Template

```python
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

Time: **O(log N)**, Space: **O(1)**.

**Why log N:** each step eliminates half the remaining elements. An input of 1 million takes only ~20 comparisons (2²⁰ ≈ 1M). This is exceptionally efficient.

**Memorize this template.** The four lines inside the loop — `mid`, equal check, `left = mid + 1`, `right = mid - 1` — should be muscle memory.

## Pattern 1: Find a Target (Classic)

The template above. Use when the array is sorted and you need to find a specific value.

## Pattern 2: Find a Boundary (First/Last Occurrence)

For sorted arrays with **duplicates**, find the leftmost or rightmost occurrence of a value.

```python
def first_occurrence(nums, target):
    left, right = 0, len(nums) - 1
    result = -1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            result = mid         # record this match...
            right = mid - 1      # ...but keep searching left
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result
```

The key change: when you find the target, don't return — keep narrowing toward the boundary, remembering the last match.

## Pattern 3: Binary Search on the Answer (Advanced)

This one is mind-bending: you binary search on the **answer space**, not on the input array. Used when the problem has a monotonic property: *"if X works, then anything bigger than X also works."*

**Example:** "Find the minimum truck capacity that can deliver all packages in D days."

The answer is somewhere between `max(packages)` (smallest possible capacity) and `sum(packages)` (one giant delivery). Binary search on the capacity, and at each midpoint, check feasibility.

```python
def min_capacity(packages, days):
    def can_deliver(cap):
        d, current = 1, 0
        for p in packages:
            if current + p > cap:
                d += 1
                current = p
            else:
                current += p
        return d <= days

    left, right = max(packages), sum(packages)
    while left < right:
        mid = (left + right) // 2
        if can_deliver(mid):
            right = mid        # try smaller
        else:
            left = mid + 1     # need bigger
    return left
```

When you spot this kind of problem ("minimum X such that...") it's the trigger. Binary search on the X.

## When to Use What

| Problem signal | Pattern |
|---|---|
| "Find target in sorted array" | Pattern 1 |
| "Find first / last position of..." | Pattern 2 |
| "Minimum / maximum X such that..." | Pattern 3 |
| "Search in rotated sorted array" | Pattern 1 with rotation handling |
| "Square root / nth root" | Pattern 3 |

## Common Bugs

1. **Off-by-one in the while condition.** `while left <= right` for standard search (Pattern 1). `while left < right` for some boundary searches. Pick the template and stick to it — don't improvise.

2. **Forgetting to update `result` in boundary search.** Pattern 2 requires recording the last match before continuing — otherwise you return -1 when the target exists.

3. **`(left + right) // 2` overflow.** Not an issue in Python (arbitrary precision integers), but in C++/Java use `left + (right - left) // 2` to avoid integer overflow.

4. **Infinite loop in Pattern 3.** When using `while left < right`, make sure `left = mid + 1` (not just `mid`) at some point — otherwise the loop never terminates when `left + 1 == right`.

## How to Talk About It

> "The array is sorted, so I can binary search. Each comparison eliminates half the remaining range. That gives O(log N) time and O(1) space."

For boundary search:
> "I'll binary search and, when I find the target, keep searching left to find the first occurrence — recording the last match each time."

For answer-space search:
> "The problem has a monotonic property — if X works, so does anything bigger. I can binary search on X itself, checking feasibility at each midpoint."

## Why This Matters

Binary search is rarely a standalone interview problem at senior level. It usually appears **inside** a bigger problem — sorted routing table lookup, finding the time a metric crossed a threshold, binary search on a feasibility predicate. Knowing the template cold means you can drop it into any larger algorithm without thinking.
