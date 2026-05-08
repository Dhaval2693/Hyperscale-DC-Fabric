# Graph Algorithms for Network Engineers

Networks are graphs. Routers and switches are nodes; links are edges. Many network problems that seem domain-specific are, at their core, graph problems: finding the shortest path, detecting cycles, determining reachability, finding bottlenecks. Understanding graph algorithms is directly useful for network engineering and also prepares you for the graph-heavy section of any technical coding interview.

This article covers the graph algorithms most relevant to network engineers — BFS, DFS, Dijkstra, and cycle detection — with Python implementations and network-specific examples.

## Representing a Network as a Graph

```python
from collections import defaultdict

class NetworkGraph:
    """Adjacency list representation of a network topology."""

    def __init__(self):
        # {node: [(neighbor, weight), ...]}
        self.edges = defaultdict(list)

    def add_link(self, a: str, b: str, cost: int = 1, bidirectional: bool = True):
        self.edges[a].append((b, cost))
        if bidirectional:
            self.edges[b].append((a, cost))

    def nodes(self) -> set:
        all_nodes = set(self.edges.keys())
        for neighbors in self.edges.values():
            all_nodes.update(n for n, _ in neighbors)
        return all_nodes

# Build a simple spine-leaf topology
net = NetworkGraph()
net.add_link("spine-1", "leaf-1", cost=1)
net.add_link("spine-1", "leaf-2", cost=1)
net.add_link("spine-2", "leaf-1", cost=1)
net.add_link("spine-2", "leaf-2", cost=1)
```

## BFS — Breadth-First Search

**What it does:** Finds the shortest path in terms of hop count (number of edges) between a source and all other nodes.

**Network use case:** Finding the minimum-hop path between two devices. Verifying that all nodes are reachable from the core. Finding all devices within N hops of a given device.

```python
from collections import deque

def bfs_shortest_path(graph: NetworkGraph, start: str, target: str) -> list[str]:
    """
    Find the shortest path (minimum hops) from start to target.
    Returns the path as a list of nodes, or empty list if unreachable.
    """
    if start == target:
        return [start]

    visited = {start}
    # Queue stores (current_node, path_to_current_node)
    queue = deque([(start, [start])])

    while queue:
        node, path = queue.popleft()
        for neighbor, _ in graph.edges[node]:
            if neighbor == target:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return []  # target not reachable

def bfs_reachable(graph: NetworkGraph, start: str) -> set[str]:
    """Return all nodes reachable from start."""
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor, _ in graph.edges[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return visited

# Check if all leaves are reachable from spine-1
reachable = bfs_reachable(net, "spine-1")
all_nodes = net.nodes()
unreachable = all_nodes - reachable
if unreachable:
    print(f"Partition detected: {unreachable} not reachable from spine-1")
```

**Time complexity:** O(V + E) where V = nodes, E = edges.

**Interview note:** BFS is always the right algorithm when "shortest path" means "fewest hops" — no weights. If edges have weights, use Dijkstra.

## DFS — Depth-First Search

**What it does:** Explores as far as possible along each branch before backtracking. Useful for cycle detection and connectivity checks.

**Network use case:** Detecting routing loops (cycles in the graph). Finding all devices in a network segment. Topological sorting for dependency ordering (deploy A before B, B before C).

```python
def dfs_detect_cycle(graph: NetworkGraph) -> bool:
    """
    Detect if the network topology has any cycles.
    Uses DFS with a recursion stack to distinguish back edges (cycles) from cross edges.
    """
    visited = set()
    rec_stack = set()  # Nodes currently in the DFS call stack

    def dfs(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)

        for neighbor, _ in graph.edges[node]:
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True  # Back edge = cycle

        rec_stack.remove(node)
        return False

    for node in graph.nodes():
        if node not in visited:
            if dfs(node):
                return True
    return False

# Topological sort — ordering for dependency-based deployment
def topological_sort(graph: NetworkGraph) -> list[str]:
    """
    Returns nodes in topological order (deploy order: no node appears before its dependencies).
    Only valid for DAGs (directed acyclic graphs).
    """
    visited = set()
    result = []

    def dfs(node: str):
        visited.add(node)
        for neighbor, _ in graph.edges[node]:
            if neighbor not in visited:
                dfs(neighbor)
        result.append(node)

    for node in graph.nodes():
        if node not in visited:
            dfs(node)

    return list(reversed(result))
```

**Time complexity:** O(V + E).

## Dijkstra's Algorithm — Shortest Weighted Path

**What it does:** Finds the shortest path by total cost (sum of edge weights) from a source to all other nodes. This is how OSPF computes its SPF (Shortest Path First) tree.

**Network use case:** Computing the minimum-cost path in an OSPF network. Simulating routing table computation. Finding the lowest-latency path when latency is the edge weight.

```python
import heapq

def dijkstra(graph: NetworkGraph, start: str) -> dict[str, tuple[int, list[str]]]:
    """
    Dijkstra's algorithm — shortest weighted path from start to all other nodes.
    Returns {node: (total_cost, path)} for all reachable nodes.
    """
    # Priority queue: (cost, node, path)
    pq = [(0, start, [start])]
    # Best known distance to each node
    best = {start: 0}

    while pq:
        cost, node, path = heapq.heappop(pq)

        # Skip if we've already found a better path
        if cost > best.get(node, float('inf')):
            continue

        for neighbor, edge_cost in graph.edges[node]:
            new_cost = cost + edge_cost
            if new_cost < best.get(neighbor, float('inf')):
                best[neighbor] = new_cost
                heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

    # Reconstruct — rebuild paths (simplified: just return costs for large graphs)
    return best

# Network with weighted links (OSPF cost based on bandwidth)
weighted_net = NetworkGraph()
weighted_net.add_link("spine-1", "leaf-1", cost=10)   # 10G link
weighted_net.add_link("spine-1", "leaf-2", cost=100)  # 1G link (higher cost)
weighted_net.add_link("spine-2", "leaf-1", cost=10)
weighted_net.add_link("spine-2", "leaf-2", cost=10)

costs = dijkstra(weighted_net, "spine-1")
print(f"Cost to leaf-2 via spine-1: {costs['leaf-2']}")
# Expected: 10 via spine-2 → leaf-2, not 100 via spine-1 → leaf-2
```

**Time complexity:** O((V + E) log V) with a binary heap.

**Interview note:** Dijkstra assumes non-negative edge weights. For negative weights (rare in networking), use Bellman-Ford.

## Finding Network Partitions

**The problem:** After a link failure, which parts of the network are disconnected?

```python
def find_partitions(graph: NetworkGraph) -> list[set[str]]:
    """
    Find all connected components in the network.
    Each component is a set of nodes that can reach each other.
    Multiple components = network partition.
    """
    all_nodes = graph.nodes()
    visited = set()
    partitions = []

    for node in all_nodes:
        if node not in visited:
            component = bfs_reachable(graph, node)
            partitions.append(component)
            visited.update(component)

    return partitions

# Simulate a spine failure
net_after_failure = NetworkGraph()
# spine-1 failed — only spine-2 links remain
net_after_failure.add_link("spine-2", "leaf-1")
net_after_failure.add_link("spine-2", "leaf-2")
# leaf-3 is only connected via spine-1 (which failed)
net_after_failure.add_link("leaf-3", "spine-1-dead-link-only")

parts = find_partitions(net_after_failure)
if len(parts) > 1:
    print(f"Network is partitioned into {len(parts)} segments:")
    for i, part in enumerate(parts):
        print(f"  Partition {i+1}: {part}")
```

## Interview Tips for Graph Problems

**BFS vs DFS:** If the problem says "shortest path" or "minimum hops" — BFS. If it says "all paths," "detect cycle," or "ordering" — DFS.

**Mark visited before enqueuing, not after dequeuing.** A common bug: marking a node visited when you pop it (not when you push it) causes the same node to be pushed to the queue multiple times, giving incorrect results and O(n²) behavior in worst case.

**Edge cases to mention in interviews:**
- Disconnected graph (multiple components)
- Self-loops
- No path between source and target
- Graph with a single node
- Weighted graph with equal weights (Dijkstra degenerates to BFS — that's correct)

**Space complexity:** BFS and DFS both use O(V) space for the visited set and queue/stack. Dijkstra uses O(V + E) for the priority queue.
