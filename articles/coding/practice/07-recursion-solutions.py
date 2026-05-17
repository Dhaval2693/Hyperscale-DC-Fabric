# Solutions: 07-recursion-practice.py


# --- Problem 1: Factorial ---
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Time:  O(N) — N recursive calls
# Space: O(N) — N frames on the call stack


# --- Problem 2: Sum of Digits ---
def sum_digits(n):
    if n < 10:
        return n
    return n % 10 + sum_digits(n // 10)

# Time:  O(log N) — N divided by 10 each step
# Space: O(log N) — recursion depth
#
# Base case: single digit. Recursive case: extract last digit, recurse on the rest.


# --- Problem 3: Fibonacci with Memoization ---
def fib(n, memo=None):
    if memo is None:
        memo = {}
    if n <= 1:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fib(n - 1, memo) + fib(n - 2, memo)
    return memo[n]

# Time:  O(N) — each fib(k) computed once thanks to memo
# Space: O(N) — memo + call stack
#
# Without memo: O(2ᴺ). The memo turns exponential into linear.
# The `if memo is None: memo = {}` avoids the mutable default arg trap.


# --- Problem 4: Power of Two ---
def is_power_of_two(n):
    if n == 1:
        return True
    if n < 2 or n % 2 != 0:
        return False
    return is_power_of_two(n // 2)

# Time:  O(log N)
# Space: O(log N) call stack
#
# Base case: n == 1 (2⁰). Halve repeatedly; if anything is ever odd along the way,
# it's not a power of two.


# --- Problem 5: Generate All Subsets ---
def subsets(nums):
    result = []
    def backtrack(start, current):
        result.append(current[:])               # record snapshot
        for i in range(start, len(nums)):
            current.append(nums[i])             # choose
            backtrack(i + 1, current)           # recurse
            current.pop()                       # un-choose (backtrack)
    backtrack(0, [])
    return result

# Pattern used: Backtracking
# Time:  O(N × 2ᴺ) — 2ᴺ subsets, each costs O(N) to copy
# Space: O(N) recursion depth + O(N × 2ᴺ) for the output
#
# The pattern: choose → recurse → un-choose. This generates every combination
# of "include or exclude" for each element.
#
# `current[:]` makes a snapshot — without the copy, every result entry would
# point to the same list (which keeps mutating).


# --- Challenge: Generate All Permutations ---
def permutations(nums):
    result = []
    def backtrack(current, remaining):
        if not remaining:
            result.append(current[:])
            return
        for i in range(len(remaining)):
            current.append(remaining[i])
            backtrack(current, remaining[:i] + remaining[i+1:])
            current.pop()
    backtrack([], nums)
    return result

# Pattern used: Backtracking
# Time:  O(N × N!) — N! permutations × O(N) to copy each
# Space: O(N) recursion + O(N × N!) for output
#
# Same backtracking shape as subsets, but at each step we pick from REMAINING
# items (not by start index). After picking, we recurse with that item removed.


if __name__ == "__main__":
    print("Problem 1:", factorial(5))
    print("Problem 2:", sum_digits(1234))
    print("Problem 3:", fib(10))
    print("Problem 4:", is_power_of_two(16))
    print("Problem 4:", is_power_of_two(18))
    print("Problem 5:", subsets([1, 2, 3]))
    print("Challenge:", permutations([1, 2, 3]))
