from typing import Dict, Tuple, List

class DSUParity:
    __slots__ = ("p","sz","xr")
    def __init__(self, n: int):
        self.p = list(range(n+1))
        self.sz = [1]*(n+1)
        self.xr = [0]*(n+1)

    def find(self, x: int):
        xr = 0
        while self.p[x] != x:
            xr ^= self.xr[x]
            x = self.p[x]
        return x, xr

    def unite(self, a: int, b: int, w: int) -> bool:
        ra, xa = self.find(a)
        rb, xb = self.find(b)
        if ra == rb:
            return (xa ^ xb) == w
        if self.sz[ra] < self.sz[rb]:
            ra, rb = rb, ra
            xa, xb = xb, xa
        self.p[rb] = ra
        self.xr[rb] = xa ^ xb ^ w
        self.sz[ra] += self.sz[rb]
        return True

def check_subset_sparse(active, ids):
    # active: dict[eid] = (a,b,w) , w in {0,1}
    parent = {}
    xr = {}      # xor-to-parent
    size = {}

    def make(x):
        parent[x] = x
        xr[x] = 0
        size[x] = 1

    def find(x):
        if x not in parent:
            make(x)
            return x, 0
        if parent[x] == x:
            return x, 0
        r, px = find(parent[x])
        xr[x] ^= px
        parent[x] = r
        return parent[x], xr[x]

    def union(a, b, w):
        ra, xa = find(a)
        rb, xb = find(b)
        if ra == rb:
            return (xa ^ xb) == w  # check consistency
        # union by size
        if size[ra] < size[rb]:
            ra, rb = rb, ra
            xa, xb = xb, xa
        parent[rb] = ra
        xr[rb] = xa ^ xb ^ w
        size[ra] += size[rb]
        return True

    for eid in ids:
        a, b, w = active[eid]
        if not union(a, b, w):
            return False
    return True
