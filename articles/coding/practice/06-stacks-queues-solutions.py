# Solutions: 06-stacks-queues-practice.py


# --- Problem 1: Valid Parentheses ---
def valid_parens(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return len(stack) == 0

# Pattern used: 1 (Basic Stack)
# Time:  O(N)
# Space: O(N)
#
# Open → push. Close → check + pop. Stack empty at end means matched.


# --- Problem 2: Daily Temperatures ---
def daily_temperatures(temps):
    result = [0] * len(temps)
    stack = []   # stores indices with decreasing temperatures

    for i, temp in enumerate(temps):
        while stack and temps[stack[-1]] < temp:
            idx = stack.pop()
            result[idx] = i - idx
        stack.append(i)
    return result

# Pattern used: 2 (Monotonic Stack)
# Time:  O(N)
# Space: O(N) for the stack
#
# Each index is pushed and popped at most once → O(N) amortized.
# Stack always holds indices with not-yet-resolved "next warmer day."


# --- Problem 3: Implement Queue Using Two Stacks ---
class MyQueue:
    def __init__(self):
        self.in_stack = []
        self.out_stack = []

    def enqueue(self, x):
        self.in_stack.append(x)

    def dequeue(self):
        if not self.out_stack:
            while self.in_stack:
                self.out_stack.append(self.in_stack.pop())
        return self.out_stack.pop()

# Pattern used: Two stacks
# Time (amortized): O(1) per operation
# Space: O(N)
#
# enqueue → push to in_stack.
# dequeue → if out_stack empty, transfer all from in_stack (reverses order),
#           then pop from out_stack. Each element is moved at most twice.


# --- Problem 4: Min Stack ---
class MinStack:
    def __init__(self):
        self.stack = []        # (value, current_min)

    def push(self, x):
        cur_min = min(x, self.stack[-1][1]) if self.stack else x
        self.stack.append((x, cur_min))

    def pop(self):
        self.stack.pop()

    def top(self):
        return self.stack[-1][0]

    def get_min(self):
        return self.stack[-1][1]

# Pattern used: Augmented stack
# Time:  O(1) for all operations
# Space: O(N)
#
# Store min at each level alongside the value.
# When popping, the previous element's stored min is automatically correct.


# --- Problem 5: BFS — Shortest Path in Grid ---
from collections import deque

def shortest_path(grid):
    if not grid or grid[0][0] == 1:
        return -1
    rows, cols = len(grid), len(grid[0])
    if grid[rows-1][cols-1] == 1:
        return -1

    visited = {(0, 0)}
    queue = deque([(0, 0, 0)])   # (row, col, steps)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        r, c, steps = queue.popleft()
        if (r, c) == (rows-1, cols-1):
            return steps
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and grid[nr][nc] == 0 and (nr, nc) not in visited):
                visited.add((nr, nc))
                queue.append((nr, nc, steps + 1))
    return -1

# Pattern used: 3 (BFS with deque)
# Time:  O(rows × cols)
# Space: O(rows × cols)
#
# BFS guarantees the first time we reach the target is via the shortest path.
# Mark visited at ENQUEUE time, not dequeue — otherwise duplicates.


# --- Challenge: Largest Rectangle in Histogram ---
def largest_rectangle(heights):
    stack = []   # indices in increasing height order
    max_area = 0
    heights = heights + [0]   # sentinel: forces all remaining to flush

    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            top = stack.pop()
            # Width: from the index after the previous stack-top, to i-1
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, heights[top] * width)
        stack.append(i)
    return max_area

# Pattern used: 2 (Monotonic Stack — increasing)
# Time:  O(N) — each index pushed and popped once
# Space: O(N) for the stack
#
# For each bar, when we pop it from the stack, we know:
#   - the right boundary is the current i (first smaller to the right)
#   - the left boundary is the new top of stack (last smaller to the left)
# So width = i - new_top - 1, area = height × width.
#
# This problem is one of the harder monotonic-stack applications — worth
# understanding the pattern but don't worry if you can't derive it cold.


if __name__ == "__main__":
    print("Problem 1:", valid_parens("()[]{}"))
    print("Problem 1:", valid_parens("(]"))
    print("Problem 2:", daily_temperatures([73,74,75,71,69,72,76,73]))

    q = MyQueue()
    q.enqueue(1); q.enqueue(2); q.enqueue(3)
    print("Problem 3:", q.dequeue(), q.dequeue(), q.dequeue())

    ms = MinStack()
    ms.push(3); ms.push(5); ms.push(2); ms.push(1)
    print("Problem 4:", ms.get_min())
    ms.pop()
    print("Problem 4:", ms.get_min())

    grid = [[0,0,0],[1,1,0],[0,0,0]]
    print("Problem 5:", shortest_path(grid))

    print("Challenge:", largest_rectangle([2,1,5,6,2,3]))
