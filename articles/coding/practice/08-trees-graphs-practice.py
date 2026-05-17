# Session 8: Trees and Graphs Practice
#
# Patterns from the article:
#   Pattern 1: BFS (shortest path, level order)
#   Pattern 2: DFS (cycle detection, path finding)
#   Pattern 3: Tree traversals (pre/in/post)
#   Pattern 4: Dijkstra (weighted shortest path)


# --- Setup: TreeNode class for tree problems ---
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# --- Problem 1: Inorder Traversal ---
# Return the inorder traversal of a binary tree as a list of values.
#
# Example tree:
#      1
#       \
#        2
#       /
#      3
# inorder -> [1, 3, 2]

def inorder_traversal(root):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 2: Maximum Depth of Binary Tree ---
# Return the depth (number of nodes on the longest path from root to a leaf).
#
# Example:
#      3
#     / \
#    9  20
#       / \
#      15  7
# max_depth -> 3

def max_depth(root):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 3: Level Order Traversal (BFS) ---
# Return values grouped by level (list of lists).
#
# Example (same tree as Problem 2):
# level_order -> [[3], [9, 20], [15, 7]]

def level_order(root):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 4: Number of Islands ---
# Given a 2D grid of '1' (land) and '0' (water), count the number of islands.
# An island is a group of '1's connected horizontally/vertically.
#
# Example:
#   grid = [
#       ["1","1","0","0"],
#       ["1","1","0","0"],
#       ["0","0","1","0"],
#       ["0","0","0","1"]
#   ]
#   num_islands(grid) -> 3

def num_islands(grid):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Problem 5: Detect Cycle in Directed Graph ---
# Given a directed graph as adjacency list, return True if it has any cycle.
#
# Example:
#   graph = {0: [1], 1: [2], 2: [0]}    -> True
#   graph = {0: [1], 1: [2], 2: []}     -> False

def has_cycle(graph):
    # your code here
    pass

# Pattern used:
# Time:
# Space:


# --- Challenge: Dijkstra's Shortest Path ---
# Given a weighted graph (adj list of (neighbor, weight) tuples),
# return shortest distance from start to every reachable node.
#
# Example:
#   graph = {
#       'A': [('B', 1), ('C', 4)],
#       'B': [('C', 2), ('D', 5)],
#       'C': [('D', 1)],
#       'D': []
#   }
#   dijkstra(graph, 'A') -> {'A': 0, 'B': 1, 'C': 3, 'D': 4}

def dijkstra(graph, start):
    # your code here
    pass


# --- Test your solutions ---
if __name__ == "__main__":
    # Tree for problems 1-3:
    #      3
    #     / \
    #    9  20
    #       / \
    #      15  7
    root = TreeNode(3,
        TreeNode(9),
        TreeNode(20, TreeNode(15), TreeNode(7)))

    # Tree for problem 1:
    #   1
    #    \
    #     2
    #    /
    #   3
    root2 = TreeNode(1, None, TreeNode(2, TreeNode(3)))

    print("Problem 1:", inorder_traversal(root2))                  # [1, 3, 2]
    print("Problem 2:", max_depth(root))                           # 3
    print("Problem 3:", level_order(root))                         # [[3], [9, 20], [15, 7]]

    grid = [
        ["1","1","0","0"],
        ["1","1","0","0"],
        ["0","0","1","0"],
        ["0","0","0","1"]
    ]
    print("Problem 4:", num_islands(grid))                         # 3

    print("Problem 5:", has_cycle({0: [1], 1: [2], 2: [0]}))       # True
    print("Problem 5:", has_cycle({0: [1], 1: [2], 2: []}))        # False

    weighted = {
        'A': [('B', 1), ('C', 4)],
        'B': [('C', 2), ('D', 5)],
        'C': [('D', 1)],
        'D': []
    }
    print("Challenge:", dijkstra(weighted, 'A'))                   # {'A':0, 'B':1, 'C':3, 'D':4}
