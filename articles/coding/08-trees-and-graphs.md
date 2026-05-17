# Trees and Graphs

A **tree** is a special graph: connected, no cycles, one root, each node has at most one parent. A **graph** is the general structure: any set of nodes (vertices) connected by edges, possibly with cycles.

For network engineers, this topic is especially valuable. Routing tables are trees, network topologies are graphs, OSPF's SPF computation IS Dijkstra's algorithm. The same algorithms that show up in coding interviews are running inside the network devices you operate.

## Tree Representation

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

## Graph Representation: Adjacency List

Most common in interviews. A `dict` mapping each node to its neighbors.

```python
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'D'],
    'D': ['B', 'C'],
}
```

For **weighted** graphs (Dijkstra), store `(neighbor, weight)` tuples:
```python
graph = {
    'A': [('B', 5), ('C', 10)],
    ...
}
```

## Pattern 1: BFS (Breadth-First Search)

Visits nodes level by level. The right tool for **shortest path in unweighted graphs**.

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        # process node
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

Time: **O(V + E)**, Space: **O(V)**.

## Pattern 2: DFS (Depth-First Search)

Goes deep before backtracking. The right tool for **cycle detection**, **topological sort**, and **exploring all paths**.

```python
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    # process start
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
```

Time: **O(V + E)**, Space: **O(V)** for visited + call stack.

## Tree Traversal: Pre / In / Post Order

Three DFS variants on binary trees. The names refer to **when** you process the root relative to its children.

```python
def preorder(node):     # Root → Left → Right
    if not node: return
    process(node)
    preorder(node.left)
    preorder(node.right)

def inorder(node):      # Left → Root → Right
    if not node: return
    inorder(node.left)
    process(node)
    inorder(node.right)

def postorder(node):    # Left → Right → Root
    if not node: return
    postorder(node.left)
    postorder(node.right)
    process(node)
```

| Traversal | Order | Use case |
|---|---|---|
| Preorder | Root → L → R | Copy / serialize a tree |
| Inorder | L → Root → R | Visit BST in sorted order |
| Postorder | L → R → Root | Delete nodes (free children first) |

## Pattern 3: Cycle Detection (Directed Graphs)

Use DFS with a "currently in this recursion path" set, distinct from the global visited set.

```python
def has_cycle(graph):
    visited = set()
    rec_stack = set()

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:    # back edge = cycle
                return True
        rec_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    return False
```

## Pattern 4: Dijkstra (Weighted Shortest Path)

Finds shortest path by total cost in a graph with non-negative weights. **This is exactly what OSPF does internally.**

```python
import heapq

def dijkstra(graph, start):
    distances = {start: 0}
    pq = [(0, start)]    # (distance, node)
    while pq:
        dist, node = heapq.heappop(pq)
        if dist > distances.get(node, float('inf')):
            continue
        for neighbor, weight in graph[node]:
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    return distances
```

Time: **O((V + E) log V)** with a binary heap.

## Networking Connections

| Algorithm | Networking equivalent |
|---|---|
| BFS shortest path | Minimum-hop routing |
| Dijkstra | OSPF SPF tree |
| Bellman-Ford | RIP (distance vector) |
| Detect cycle | Detect routing loop |
| Topological sort | Dependency-ordered deployment |
| Connected components | Network partition detection |

When asked "design a system that uses a graph" in a network engineering interview, this connection is your anchor — talk about routing, topology, or partition detection.

## How to Talk About It

For BFS:
> "Shortest path in an unweighted graph means BFS with a deque queue. Mark visited when enqueueing. O(V + E) time."

For DFS:
> "I'll do DFS to explore. For cycle detection, I'll track a 'currently in recursion stack' set — a back edge to a node in that set means a cycle."

For Dijkstra:
> "Weighted shortest path → Dijkstra with a min-heap priority queue. O((V + E) log V). This is essentially OSPF's SPF computation."

## Common Gotchas

1. **Marking visited at the wrong time in BFS.** Mark when enqueueing, not when dequeueing.
2. **Forgetting `visited` for graphs.** Trees don't have cycles → no visited set needed. Graphs do → always use one.
3. **Confusing tree traversal orders.** Remember: pre = root first, in = root middle, post = root last.
4. **Dijkstra with negative weights.** Doesn't work. Use Bellman-Ford instead (rare in interviews).
5. **Recursion depth on huge graphs.** For graphs with >1000 nodes, iterative DFS with an explicit stack avoids stack overflow.
