# Time and Space Complexity: The Interview Reference

Complexity analysis is the language of algorithm conversations. When you propose a solution in an interview, the next question is always "what's the time and space complexity?" Knowing how to derive and state complexity — and how to reason about it — is as important as knowing the algorithm itself.

This article is a practical reference: the common data structures, their complexities, and how to analyze the algorithms built on them.

## The Big-O Hierarchy

From fastest to slowest growth:

```
O(1)        Constant      — array index access, hash map lookup
O(log n)    Logarithmic   — binary search, balanced BST operations
O(n)        Linear        — single loop over n elements
O(n log n)  Linearithmic  — efficient sorting (merge sort, heap sort)
O(n²)       Quadratic     — nested loops, bubble sort
O(2ⁿ)       Exponential   — backtracking, all subsets
O(n!)       Factorial     — permutations
```

**The practical test:** If n = 10,000:
- O(n) = 10,000 operations → fast
- O(n log n) = ~130,000 → fast
- O(n²) = 100,000,000 → slow (seconds)
- O(2ⁿ) = ∞ → infeasible

## Data Structure Complexities

### Arrays / Lists

| Operation | Average | Worst |
|---|---|---|
| Access by index | O(1) | O(1) |
| Search (unsorted) | O(n) | O(n) |
| Search (sorted, binary) | O(log n) | O(log n) |
| Insert at end | O(1) amortized | O(n) (resize) |
| Insert at index | O(n) | O(n) |
| Delete at index | O(n) | O(n) |

### Hash Map / Dictionary

| Operation | Average | Worst |
|---|---|---|
| Lookup | O(1) | O(n) (hash collision) |
| Insert | O(1) | O(n) |
| Delete | O(1) | O(n) |

In practice, hash maps are O(1) for all operations. The O(n) worst case requires pathological hash collisions — not a real concern with Python's dict.

### Set

Same as hash map — O(1) for add, remove, contains.

### Deque (collections.deque)

| Operation | Complexity |
|---|---|
| Append/Appendleft | O(1) |
| Pop/Popleft | O(1) |
| Access by index | O(n) |

Use deque for BFS queues — not a list (list.pop(0) is O(n)).

### Heap (heapq)

| Operation | Complexity |
|---|---|
| heappush | O(log n) |
| heappop | O(log n) |
| heapify (build from list) | O(n) |
| Peek minimum | O(1) |

Python's heapq is a min-heap. For max-heap, negate values.

### Sorted Containers (bisect module)

| Operation | Complexity |
|---|---|
| bisect_left / bisect_right (search) | O(log n) |
| insort (insert into sorted list) | O(n) — due to shifting |

Use bisect for sorted search. Do not use it for frequent insertions — use a heap or sort at the end.

## Analyzing Algorithm Complexity

### Single Loop → O(n)

```python
def find_max(nums):         # O(n) — one pass through all elements
    max_val = float('-inf')
    for num in nums:
        max_val = max(max_val, num)
    return max_val
```

### Nested Loops → O(n²)

```python
def bubble_sort(nums):      # O(n²) — outer × inner = n × n
    for i in range(len(nums)):
        for j in range(len(nums) - i - 1):
            if nums[j] > nums[j+1]:
                nums[j], nums[j+1] = nums[j+1], nums[j]
```

**Exception:** Nested loops are NOT always O(n²). If the inner loop runs a fixed number of times regardless of n, the total is still O(n).

### Loop + Binary Search → O(n log n)

```python
def count_pairs_with_target(nums, target):   # O(n log n)
    nums.sort()                               # O(n log n)
    count = 0
    for i, num in enumerate(nums):            # O(n) iterations
        # Binary search is O(log n) per call
        import bisect
        complement = target - num
        idx = bisect.bisect_left(nums, complement, i+1)
        if idx < len(nums) and nums[idx] == complement:
            count += 1
    return count
```

### Recursion: Use the Recurrence

For recursive algorithms, write the recurrence and solve it.

**Binary search:**
```
T(n) = T(n/2) + O(1)   → O(log n)
```

**Merge sort:**
```
T(n) = 2T(n/2) + O(n)  → O(n log n)   [Master Theorem: a=2, b=2, f(n)=n → case 2]
```

**Fibonacci (naive):**
```
T(n) = T(n-1) + T(n-2) → O(2ⁿ)       [exponential — use DP instead]
```

## Space Complexity

Space complexity counts the additional memory your algorithm uses, not counting the input.

**O(1) space:** Uses only a fixed number of variables regardless of input size.
```python
def sum_array(nums):    # O(1) space — just the accumulator
    total = 0
    for n in nums:
        total += n
    return total
```

**O(n) space:** Uses a data structure proportional to input size.
```python
def reverse(nums):      # O(n) space — the reversed list
    return nums[::-1]

def bfs(graph, start):  # O(n) space — visited set and queue
    visited = set()
    queue = deque([start])
    ...
```

**O(log n) space:** Recursive algorithms use O(depth) space for the call stack.
```python
def binary_search_recursive(nums, target, left, right):  # O(log n) call stack
    if left > right:
        return -1
    mid = (left + right) // 2
    if nums[mid] == target:
        return mid
    elif nums[mid] < target:
        return binary_search_recursive(nums, target, mid+1, right)
    else:
        return binary_search_recursive(nums, target, left, mid-1)
```

**O(n) call stack for DFS:** Recursive DFS on a graph with n nodes has O(n) call stack depth in the worst case (a linear chain graph). For large inputs, this can cause stack overflow — prefer iterative DFS with an explicit stack.

## Amortized Complexity

Some operations are occasionally expensive but cheap on average. Python's list append is the canonical example.

`list.append()` is usually O(1). When the list doubles in size, it copies all elements — O(n). But doublings happen rarely enough that the amortized cost per append, averaged over n appends, is O(1).

**When to mention amortized:** Whenever you use dynamic arrays (Python lists, Java ArrayList), hash maps, or any structure with occasional resize operations. "List append is O(1) amortized" — not just "O(1)" — is the precise answer.

## The Interview Framework

When you present a solution, state complexity proactively:

> "This runs in O(n log n) time — the sort dominates — and O(n) space for the auxiliary array."

If asked to optimize:

> "The current solution is O(n²) because of the nested loops. I can reduce to O(n) using a hash map — trade space for time. That makes it O(n) time and O(n) space."

**Always note:** Does your space complexity include the input? For in-place algorithms, the answer should be O(1) extra space (the input doesn't count). Clarify this in interviews — different interviewers count it differently.

**Common traps:**
- `in` on a list is O(n) — use a set for O(1)
- `list.pop(0)` is O(n) — use `deque.popleft()` for O(1)
- Python's `sorted()` is O(n log n) — do not call it inside a loop without thinking
- String concatenation in a loop is O(n²) — use `''.join()` instead
