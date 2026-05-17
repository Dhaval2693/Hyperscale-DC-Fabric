# Recursion

Recursion is when a function calls itself with a smaller version of the same problem. It's the natural way to solve anything with self-similar structure: tree traversal, divide-and-conquer, backtracking.

In an interview, recursion appears in three contexts:
1. **Tree / graph traversal** (next article)
2. **Divide and conquer** (merge sort, quick sort, binary search)
3. **Backtracking** (generate permutations, subsets, combinations)

## The Two Parts of Every Recursion

Every recursive function has exactly two parts:

1. **Base case** — when to STOP recursing
2. **Recursive case** — call yourself with a smaller subproblem

Without a base case, the recursion never stops → stack overflow. **Always write the base case first.**

## The Simplest Example: Factorial

```python
def factorial(n):
    if n <= 1:                       # base case
        return 1
    return n * factorial(n - 1)      # recursive case
```

`factorial(5)` calls `factorial(4)` calls `factorial(3)` ... until `factorial(1)` returns 1 and the chain unwinds.

Time: **O(N)**. Space: **O(N)** for the call stack.

## When Recursion Goes Wrong: Naive Fibonacci

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

This is **O(2ᴺ)** — exponential. `fib(40)` takes seconds; `fib(50)` takes minutes. Why? `fib(38)` is recomputed many times by different branches of the recursion tree.

**The fix: memoization.** Cache results so each subproblem is solved once.

```python
def fib(n, memo=None):
    if memo is None:
        memo = {}
    if n <= 1:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fib(n - 1, memo) + fib(n - 2, memo)
    return memo[n]
```

Now it's **O(N)** time. This is the bridge to **dynamic programming** — DP is just recursion + memoization made explicit.

## Pattern 1: Divide and Conquer

Break the problem in half, solve each half, combine results.

```python
def merge_sort(nums):
    if len(nums) <= 1:                # base case
        return nums
    mid = len(nums) // 2
    left = merge_sort(nums[:mid])     # solve left half
    right = merge_sort(nums[mid:])    # solve right half
    return merge(left, right)         # combine
```

Time: **O(N log N)** — log N levels of recursion, O(N) merging per level.

## Pattern 2: Backtracking (Generate All Possibilities)

Recursively try each option, then "undo" it (backtrack) to try the next.

```python
def subsets(nums):
    result = []
    def backtrack(start, current):
        result.append(current[:])              # record this subset
        for i in range(start, len(nums)):
            current.append(nums[i])            # try including nums[i]
            backtrack(i + 1, current)
            current.pop()                      # undo, try next
    backtrack(0, [])
    return result
```

The `current.pop()` is the "backtrack" — restore state before trying the next option.

## How to Think About Recursion

**Trust the recursion.** Don't trace every call in your head. Trust that `factorial(n - 1)` correctly returns `(n-1)!`, and just write what `factorial(n)` should do given that.

This mental shift — "assume the smaller version works, just handle one step" — is the hardest and most important thing about recursion. Senior engineers think this way naturally.

## How to Talk About It

> "I'll solve this recursively. Base case: [size 0 or 1]. Recursive case: I break the problem into a smaller subproblem of size N-1 (or split it in half for divide-and-conquer)."

For memoization:
> "Naive recursion has overlapping subproblems — it's O(2ᴺ). I'll memoize so each subproblem is computed once, bringing it to O(N)."

For backtracking:
> "I'll explore each choice recursively, backtracking after each call to try the next option. The work is proportional to the number of valid configurations."

## Common Gotchas

1. **Missing base case** → stack overflow.
2. **Mutable default argument.** `def f(x, memo={})` shares `{}` across calls. Use `memo=None` and init inside.
3. **Recursion depth limit.** Python's default is ~1000. For deeper recursion, use iteration with an explicit stack.
4. **Returning vs printing.** Recursion combines return values. Printing inside a recursive function doesn't help the caller.

## When NOT to Use Recursion

For very deep structures (deep linked lists, very tall trees), use iteration with an explicit stack:

```python
def tree_sum_iterative(root):
    if not root:
        return 0
    stack = [root]
    total = 0
    while stack:
        node = stack.pop()
        total += node.val
        if node.left: stack.append(node.left)
        if node.right: stack.append(node.right)
    return total
```

Same algorithm, no recursion limit. Heap-allocated explicit stack instead of the call stack.
