# Solutions: 08-trees-graphs-practice.py

from collections import deque
import heapq


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# --- Problem 1: Inorder Traversal ---
def inorder_traversal(root):
    result = []
    def helper(node):
        if not node:
            return
        helper(node.left)
        result.append(node.val)
        helper(node.right)
    helper(root)
    return result

# Pattern used: 3 (Tree Traversal - Inorder)
# Time:  O(N) — visit every node once
# Space: O(H) where H = tree height (O(N) worst case, O(log N) balanced)
#
# Inorder = Left, Root, Right. For a BST, this visits values in sorted order.


# --- Problem 2: Maximum Depth of Binary Tree ---
def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

# Pattern used: 2 (DFS via recursion)
# Time:  O(N)
# Space: O(H)
#
# Trust the recursion: the max depth at this node is 1 + max(left depth, right depth).


# --- Problem 3: Level Order Traversal (BFS) ---
def level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result

# Pattern used: 1 (BFS)
# Time:  O(N)
# Space: O(N) — queue holds up to one level (which can be N/2 leaves)
#
# Trick: capture level_size BEFORE the inner loop. Process exactly that many
# nodes (one level), then move to the next. Otherwise levels blur together.


# --- Problem 4: Number of Islands ---
def num_islands(grid):
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if (r < 0 or r >= rows or c < 0 or c >= cols
                or grid[r][c] != "1"):
            return
        grid[r][c] = "0"   # mark visited by sinking the land
        dfs(r+1, c)
        dfs(r-1, c)
        dfs(r, c+1)
        dfs(r, c-1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                dfs(r, c)   # sink the entire island
    return count

# Pattern used: 2 (DFS on grid)
# Time:  O(rows × cols)
# Space: O(rows × cols) worst case for recursion stack
#
# Classic island-counting: scan the grid; each unvisited '1' is a new island.
# DFS from that cell "sinks" all connected land (marks it '0') so we don't
# count it again.


# --- Problem 5: Detect Cycle in Directed Graph ---
def has_cycle(graph):
    visited = set()
    rec_stack = set()

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:    # back edge → cycle
                return True
        rec_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    return False

# Pattern used: 2 (DFS) with recursion-stack tracking
# Time:  O(V + E)
# Space: O(V)
#
# Two sets matter:
#   - visited: ever processed (global)
#   - rec_stack: currently in this DFS path
# If we hit a node already in rec_stack, that's a back edge → cycle.


# --- Challenge: Dijkstra's Shortest Path ---
def dijkstra(graph, start):
    distances = {start: 0}
    pq = [(0, start)]    # (distance, node)

    while pq:
        dist, node = heapq.heappop(pq)
        if dist > distances.get(node, float('inf')):
            continue     # stale entry — already found shorter path
        for neighbor, weight in graph.get(node, []):
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    return distances

# Pattern used: 4 (Dijkstra) — BFS with priority queue
# Time:  O((V + E) log V)
# Space: O(V)
#
# Greedy: always expand the closest unfinalized node next.
# The min-heap (heapq) ensures we always pop the shortest known distance.
# Stale heap entries (already-better paths found) are skipped with the `if`.
#
# This is the EXACT algorithm OSPF uses internally to build its SPF tree.


if __name__ == "__main__":
    root = TreeNode(3,
        TreeNode(9),
        TreeNode(20, TreeNode(15), TreeNode(7)))
    root2 = TreeNode(1, None, TreeNode(2, TreeNode(3)))

    print("Problem 1:", inorder_traversal(root2))
    print("Problem 2:", max_depth(root))
    print("Problem 3:", level_order(root))

    grid = [
        ["1","1","0","0"],
        ["1","1","0","0"],
        ["0","0","1","0"],
        ["0","0","0","1"]
    ]
    print("Problem 4:", num_islands(grid))

    print("Problem 5:", has_cycle({0: [1], 1: [2], 2: [0]}))
    print("Problem 5:", has_cycle({0: [1], 1: [2], 2: []}))

    weighted = {
        'A': [('B', 1), ('C', 4)],
        'B': [('C', 2), ('D', 5)],
        'C': [('D', 1)],
        'D': []
    }
    print("Challenge:", dijkstra(weighted, 'A'))
