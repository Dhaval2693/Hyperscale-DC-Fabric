# Session 6: Stacks and Queues Practice
#
# Patterns from the article:
#   Pattern 1: Basic Stack (matching/parsing)
#   Pattern 2: Monotonic Stack (next greater/smaller)
#   Pattern 3: Queue / BFS


# --- Problem 1: Valid Parentheses ---
# Return True if the string has balanced brackets: (), [], {}.
#
# Example:
#   valid_parens("()[]{}")   -> True
#   valid_parens("(]")       -> False
#   valid_parens("([)]")     -> False
#   valid_parens("{[]}")     -> True

def valid_parens(s):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 2: Daily Temperatures (Monotonic Stack) ---
# Given a list of daily temperatures, return a list where result[i] is
# the number of days you have to wait until a warmer temperature.
# If there is no future day, put 0.
#
# Example:
#   daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])
#   -> [1, 1, 4, 2, 1, 1, 0, 0]

def daily_temperatures(temps):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 3: Implement Queue Using Two Stacks ---
# Implement enqueue() and dequeue() using only stack operations.
# Both should be O(1) amortized.

class MyQueue:
    def __init__(self):
        # your code here
        pass

    def enqueue(self, x):
        # your code here
        pass

    def dequeue(self):
        # your code here
        pass

# Pattern used:
# Time (amortized):
# Space:


# --- Problem 4: Min Stack ---
# Design a stack that supports push, pop, top, and getMin all in O(1).

class MinStack:
    def __init__(self):
        # your code here
        pass

    def push(self, x):
        pass

    def pop(self):
        pass

    def top(self):
        pass

    def get_min(self):
        pass

# Pattern used:
# Time:
# Space:


# --- Problem 5: BFS — Number of Steps to Target in Grid ---
# Given a 2D grid where 0 = open, 1 = wall, find minimum steps from
# (0,0) to (rows-1, cols-1). Return -1 if unreachable.
# Can move up/down/left/right.
#
# Example:
#   grid = [[0,0,0],
#           [1,1,0],
#           [0,0,0]]
#   shortest_path(grid) -> 4

def shortest_path(grid):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Challenge: Largest Rectangle in Histogram ---
# Given heights of bars in a histogram, return the area of the largest
# rectangle that can be formed within the histogram.
#
# Example:
#   largest_rectangle([2, 1, 5, 6, 2, 3]) -> 10   (5 and 6 form 5×2)
#
# Hint: Monotonic stack. For each bar, find how far left and right
#       it can extend (until a smaller bar). Width × height = area.

def largest_rectangle(heights):
    # your code here
    pass


# --- Test your solutions ---
if __name__ == "__main__":
    print("Problem 1:", valid_parens("()[]{}"))                          # True
    print("Problem 1:", valid_parens("(]"))                              # False
    print("Problem 2:", daily_temperatures([73,74,75,71,69,72,76,73]))   # [1,1,4,2,1,1,0,0]

    q = MyQueue()
    q.enqueue(1); q.enqueue(2); q.enqueue(3)
    print("Problem 3:", q.dequeue(), q.dequeue(), q.dequeue())           # 1 2 3

    ms = MinStack()
    ms.push(3); ms.push(5); ms.push(2); ms.push(1)
    print("Problem 4:", ms.get_min())                                    # 1
    ms.pop()
    print("Problem 4:", ms.get_min())                                    # 2

    grid = [[0,0,0],[1,1,0],[0,0,0]]
    print("Problem 5:", shortest_path(grid))                             # 4

    print("Challenge:", largest_rectangle([2,1,5,6,2,3]))                # 10
