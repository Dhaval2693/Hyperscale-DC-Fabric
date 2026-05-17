# Stacks and Queues

Stacks and queues are simple but solve a surprisingly large class of interview problems. Both store a sequence, but they differ in how items are added and removed.

- **Stack** — LIFO (last in, first out). Like a stack of plates.
- **Queue** — FIFO (first in, first out). Like a line at a store.

**In Python:**
- Stack: just use a list. `list.append()` and `list.pop()` are both O(1).
- Queue: use `collections.deque`. **Never use `list.pop(0)`** — it's O(N).

## Pattern 1: Basic Stack (Matching/Parsing)

The classic: balanced parentheses.

```python
def valid_parentheses(s):
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
```

Time: **O(N)**, Space: **O(N)**.

Open brackets push. Close brackets pop and verify match. Empty stack at the end means everything paired.

## Pattern 2: Monotonic Stack

A stack where values inside stay sorted (always increasing or always decreasing). Used for "next greater / next smaller element" problems.

```python
def next_greater_element(nums):
    """For each element, find the next greater element to its right."""
    result = [-1] * len(nums)
    stack = []   # stores indices

    for i, num in enumerate(nums):
        while stack and nums[stack[-1]] < num:
            idx = stack.pop()
            result[idx] = num
        stack.append(i)
    return result
```

Time: **O(N)** — each element is pushed and popped at most once across the entire run.

The stack always holds indices whose values are in decreasing order. A new larger value triggers pops (resolving "next greater" for those popped indices) before being pushed itself.

## Pattern 3: BFS with a Queue

The canonical use of queues. Walk a graph or tree level by level.

```python
from collections import deque

def bfs_shortest_path(graph, start, target):
    visited = {start}
    queue = deque([(start, [start])])    # (node, path_so_far)

    while queue:
        node, path = queue.popleft()
        for neighbor in graph[node]:
            if neighbor == target:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []
```

Time: **O(V + E)**. Space: **O(V)**.

**Critical rule:** mark a node visited when you **add** it to the queue, not when you process it. Otherwise the same node gets enqueued multiple times.

## Recognizing Them in Interviews

| Problem says... | Use |
|---|---|
| "Match opening/closing brackets" | Stack |
| "Parse nested structures" (JSON-like) | Stack |
| "Next greater / smaller element" | Monotonic stack |
| "Daily temperatures" / "stock span" | Monotonic stack |
| "BFS" / "shortest path (unweighted)" | Queue (`deque`) |
| "Level-order traversal" of tree | Queue (`deque`) |
| "Implement undo/redo" | Stack |

## How to Talk About It

For parsing:
> "Nested structure means stack. Each opener pushes; each closer pops and verifies the match. O(N) time and O(N) space."

For monotonic stack:
> "Each element is pushed and popped at most once, so even with a nested-looking while loop, total work is amortized O(N)."

For BFS:
> "Unweighted shortest path → BFS with a deque queue. Mark visited at enqueue time to avoid duplicates."

## Common Gotchas

1. **Using `list` as a queue.** `list.pop(0)` is O(N). Always `deque.popleft()` for queues.
2. **Marking visited at the wrong time in BFS.** Mark at enqueue, not dequeue.
3. **Empty stack on a close bracket.** Check `if not stack` before peeking `stack[-1]`.
4. **Monotonic stack direction confusion.** "Next greater" wants a decreasing stack (pop when current is bigger). "Next smaller" wants the opposite.
