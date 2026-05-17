# Session 7: Recursion Practice
#
# Patterns from the article:
#   Pattern 1: Divide and Conquer
#   Pattern 2: Backtracking
#
# Plus: simple recursive functions and memoization.


# --- Problem 1: Factorial ---
# Compute n! recursively.
#
# Example:
#   factorial(5) -> 120

def factorial(n):
    # your code here
    pass

# Time:
# Space:


# --- Problem 2: Sum of Digits ---
# Compute the sum of digits of a non-negative integer recursively.
#
# Example:
#   sum_digits(1234) -> 10   (1+2+3+4)

def sum_digits(n):
    # your code here
    pass

# Time:
# Space:


# --- Problem 3: Fibonacci with Memoization ---
# Compute the nth Fibonacci number in O(N) time using memoization.
#
# Example:
#   fib(0) -> 0
#   fib(1) -> 1
#   fib(10) -> 55

def fib(n, memo=None):
    # your code here
    pass

# Time:
# Space:


# --- Problem 4: Power of Two ---
# Return True if n is a power of two (1, 2, 4, 8, ...). Use recursion.
#
# Example:
#   is_power_of_two(16) -> True
#   is_power_of_two(18) -> False
#   is_power_of_two(1)  -> True

def is_power_of_two(n):
    # your code here
    pass

# Time:
# Space:


# --- Problem 5: Generate All Subsets (Backtracking) ---
# Given a list of distinct integers, return all possible subsets.
#
# Example:
#   subsets([1, 2, 3])
#   -> [[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]
#   (order doesn't matter)

def subsets(nums):
    # your code here
    pass

# Time:
# Space:


# --- Challenge: Generate All Permutations ---
# Given a list of distinct integers, return all possible permutations.
#
# Example:
#   permutations([1, 2, 3])
#   -> [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]
#   (order doesn't matter)

def permutations(nums):
    # your code here
    pass


# --- Test your solutions ---
if __name__ == "__main__":
    print("Problem 1:", factorial(5))                    # 120
    print("Problem 2:", sum_digits(1234))                # 10
    print("Problem 3:", fib(10))                         # 55
    print("Problem 4:", is_power_of_two(16))             # True
    print("Problem 4:", is_power_of_two(18))             # False
    print("Problem 5:", subsets([1, 2, 3]))
    print("Challenge:", permutations([1, 2, 3]))
