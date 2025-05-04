
from itertools import combinations
import math

from star import Star


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
    
    def find(self, a):
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a
    
    def union(self, a, b):
        ra = self.find(a)
        rb = self.find(b)
        if ra != rb:
            self.parent[rb] = ra
            return True
        return False

def euclidean(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def min_connecting_distance(points : list[Star]):
    n = len(points)
    edges = []

    # Step 1: Compute all pairwise distances
    for i, j in combinations(range(n), 2):
        dist = euclidean(points[i].position, points[j].position)
        edges.append((dist, i, j))

    # Step 2: Sort by distance
    edges.sort()

    # Step 3: Kruskal's algorithm
    uf = UnionFind(n)
    max_edge = 0
    edge_count = 0

    for dist, i, j in edges:
        if uf.union(i, j):
            max_edge = max(max_edge, dist)
            edge_count += 1
            if edge_count == n - 1:  # MST is complete
                break

    return max_edge