# Time and Space Complexity

Before writing a single algorithm, you need a way to measure it. Not by running it and timing it — that depends on your hardware, your input, and a dozen other variables. You need a way to reason about how an algorithm behaves as the problem scales. That is what complexity analysis gives you.

There are two dimensions to measure: time and space.

**Time complexity** describes how the number of operations grows as the input size grows. **Space complexity** describes how much memory the algorithm consumes as the input grows. Both are expressed using Big O notation, which captures the dominant growth behavior and discards constants and lower-order terms.

## Big O Notation

When we say an algorithm is O(N), we mean: as the input size N grows, the number of operations grows linearly. Double the input, roughly double the work. When we say O(N²), we mean: double the input, quadruple the work. The notation captures the shape of the growth curve, not the exact count.

Constants are dropped because they don't change the fundamental behavior. An algorithm that does 3N operations is still O(N) — the constant 3 doesn't change the fact that the work scales linearly. At large enough N, what matters is whether the algorithm is linear or quadratic or logarithmic, not the constant multiplier.

Lower-order terms are also dropped. An algorithm with N² + N operations is O(N²) — when N is large, the N term is irrelevant compared to N².

## The Common Complexities

**O(1) — Constant**

The operation takes the same time regardless of input size. Looking up a value in a dictionary by key is O(1). Accessing a list by index is O(1). The input could have a million elements, and these operations still take the same number of steps.

```python
nums = [2, 7, 11, 15]
print(nums[0])        # O(1) — direct access
```

**O(log N) — Logarithmic**

The work roughly halves with each step. Binary search is the canonical example — each comparison eliminates half the remaining elements. An input of a million elements requires only about 20 comparisons. This is exceptionally efficient and comes up frequently with sorted data or tree structures.

**O(N) — Linear**

The work grows proportionally with input size. A single loop over the input is O(N). Your Two Sum brute-force's outer loop alone would be O(N). Linear is generally good — you're doing roughly one unit of work per element.

```python
def find_max(nums):
    max_val = nums[0]
    for num in nums:       # visits every element once
        if num > max_val:
            max_val = num
    return max_val         # O(N) time, O(1) space
```

**O(N log N) — Linearithmic**

This is the complexity of efficient sorting algorithms — merge sort, heapsort, Python's built-in `sorted()`. It is worse than linear but far better than quadratic. Most interview problems that use sorting land here.

**O(N²) — Quadratic**

Two nested loops, each iterating over the input. Your Two Sum solution was O(N²). This becomes impractical quickly — an input of 10,000 elements means 100 million operations. Interviewers expect you to recognize this and ask whether you can do better.

```python
def two_sum_brute(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):   # nested loop = O(N²)
            if nums[i] + nums[j] == target:
                return [i, j]
```

**O(2^N) — Exponential**

Every additional input element doubles the work. Appears in brute-force recursion and combinatorial problems. Almost always a sign that a better approach exists — usually dynamic programming.

## Space Complexity

Space complexity measures how much additional memory your algorithm uses, beyond the input itself. The input is given — you don't count it. You count what your algorithm creates on top of it.

When your Two Sum solution ran, it used a few variables — `i`, `j`, and the return value. Those take the same amount of memory regardless of how large `nums` is. That is O(1) space — constant. Your function creates no new data structures that grow with the input.

The hashmap solution is different:

```python
def two_sum(nums, target):
    seen = {}                           # this grows with input
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
```

`seen` can grow up to N entries — one per element. That is O(N) space. You traded space for time: O(N²) time + O(1) space became O(N) time + O(N) space. In most interview contexts, this trade is worth it.

## How to Analyze Your Own Code

When you look at a function, ask these questions in order:

1. Are there loops? How many levels deep? One loop = O(N). Loop inside a loop = O(N²).
2. Are there recursive calls? How many times does the function call itself, and how does that scale with input?
3. Are there data structures being created? Arrays, dictionaries, sets that grow with N contribute to space complexity.
4. Are you calling any library functions? `sorted()` is O(N log N). `in` on a list is O(N). `in` on a set or dictionary is O(1).

The last point is a common source of hidden complexity. Searching for a value in a Python list with `if x in my_list` is O(N) — Python has to check every element. The same check on a Python set or dictionary is O(1) — it computes a hash and looks directly. This distinction is why hash maps appear in so many optimized solutions.

## What Interviewers Actually Expect

When you submit a solution, the interviewer will ask: "What is the time and space complexity of this?" They are not asking you to count lines. They want to know whether you understand how your solution scales and whether you considered alternatives.

The expected pattern in interviews is: start with the naive solution, state its complexity, then improve it. Saying "this is O(N²), but I think we can do O(N) with a hash map" demonstrates exactly the thinking they are looking for. The brute force solution is a starting point, not a failure — as long as you recognize it and know the direction to improve.

In the next article, we will use this framework to look at arrays and hash maps — the two data structures that appear in more interview problems than anything else.
