import sys

# Increase recursion depth just in case
sys.setrecursionlimit(200000)

def solve():
    # Fast I/O
    try:
        input_data = sys.stdin.read().split()
    except Exception:
        return

    if not input_data:
        return

    iterator = iter(input_data)
    try:
        N = int(next(iterator))
        Q_ops = int(next(iterator))
    except StopIteration:
        return

    # Data structures for parsing
    active_start = {} # id -> (u, v, w, start_time)
    edges = [] # (u, v, w, id, start, end)
    queries = [] # (time, type)
    
    current_time = 0
    
    # Parse operations
    # We iterate until we consume all expected operations or run out of input
    # The number of operations is Q_ops.
    
    for _ in range(Q_ops):
        try:
            op_type = next(iterator)
        except StopIteration:
            break
            
        if op_type == 'A':
            try:
                eid = int(next(iterator))
                etype = next(iterator)
                u = int(next(iterator))
                v = int(next(iterator))
            except StopIteration:
                break
            w = 0 if etype == 'S' else 1
            active_start[eid] = (u, v, w, current_time)
        elif op_type == 'R':
            try:
                eid = int(next(iterator))
            except StopIteration:
                break
            if eid in active_start:
                u, v, w, start = active_start.pop(eid)
                # Lifetime is [start, current_time - 1]
                if start <= current_time - 1:
                    edges.append((u, v, w, eid, start, current_time - 1))
        elif op_type == 'Q' or op_type == 'C':
            queries.append((current_time, op_type))
        
        current_time += 1
        
    # Close open intervals
    final_time = Q_ops - 1
    for eid, (u, v, w, start) in active_start.items():
        if start <= final_time:
            edges.append((u, v, w, eid, start, final_time))
            
    # Build Segment Tree
    # Range [0, Q_ops - 1]
    if Q_ops > 0:
        tree_size = 4 * Q_ops
        tree = [[] for _ in range(tree_size)]
        
        def add_to_tree(node, l, r, ql, qr, edge):
            if ql > r or qr < l:
                return
            if ql <= l and r <= qr:
                tree[node].append(edge)
                return
            mid = (l + r) // 2
            add_to_tree(2 * node, l, mid, ql, qr, edge)
            add_to_tree(2 * node + 1, mid + 1, r, ql, qr, edge)
            
        for edge in edges:
            # edge: (u, v, w, eid, start, end)
            add_to_tree(1, 0, Q_ops - 1, edge[4], edge[5], edge)
    else:
        # No operations? Just return
        return

    # DSU State
    parent = list(range(N + 1))
    rank = [0] * (N + 1)
    parity = [0] * (N + 1) # parity[u] = parity(u, parent[u])
    
    # History for rollback
    # (child, parent, old_rank_parent)
    history = []
    
    # Current solution stack (list of edge IDs)
    current_solution = []
    
    def find(i):
        p = 0
        while i != parent[i]:
            p ^= parity[i]
            i = parent[i]
        return i, p

    def union(u, v, w):
        root_u, par_u = find(u)
        root_v, par_v = find(v)
        
        if root_u != root_v:
            # Merge
            if rank[root_u] < rank[root_v]:
                root_u, root_v = root_v, root_u
            
            # Attach root_v to root_u
            # Path: v -> ... -> root_v -> root_u -> ... -> u
            # Weight: par_v ^ w_new ^ par_u = w
            # w_new = par_u ^ par_v ^ w
            w_new = par_u ^ par_v ^ w
            
            parent[root_v] = root_u
            parity[root_v] = w_new
            
            old_rank_u = rank[root_u]
            if rank[root_u] == rank[root_v]:
                rank[root_u] += 1
                
            history.append((root_v, root_u, old_rank_u))
            return True # Merged (Tree edge)
        else:
            # Same component
            if (par_u ^ par_v) == w:
                return False # Consistent (Extra edge)
            else:
                return None # Inconsistent

    def rollback(steps):
        for _ in range(steps):
            child, par, old_rank = history.pop()
            parent[child] = child
            parity[child] = 0
            rank[par] = old_rank

    query_idx = 0
    num_queries = len(queries)
    
    MAX_WITNESS = 5000

    def dfs(node, l, r):
        nonlocal query_idx
        
        ops_count = 0
        level_solution_count = 0
        
        # Process edges at this node
        for u, v, w, eid, _, _ in tree[node]:
            res = union(u, v, w)
            if res is not None:
                # Consistent (either tree or extra)
                current_solution.append(eid)
                level_solution_count += 1
                if res is True:
                    ops_count += 1
            
        if l == r:
            # Leaf: check for query
            while query_idx < num_queries and queries[query_idx][0] == l:
                _, q_type = queries[query_idx]
                
                k_raw = len(current_solution)
                k = min(k_raw, MAX_WITNESS)
                
                if q_type == 'Q':
                    sys.stdout.write(f"{k}\n")
                else:
                    # Output K and the IDs
                    # We take the first k IDs from current_solution
                    # This is deterministic
                    if k == 0:
                        sys.stdout.write("0\n")
                    else:
                        # Optimization: construct string efficiently
                        # Using slice is fine for k=5000
                        out_ids = current_solution[:k]
                        sys.stdout.write(f"{k} {' '.join(map(str, out_ids))}\n")
                
                query_idx += 1
        else:
            mid = (l + r) // 2
            dfs(2 * node, l, mid)
            dfs(2 * node + 1, mid + 1, r)
            
        # Rollback
        rollback(ops_count)
        for _ in range(level_solution_count):
            current_solution.pop()

    dfs(1, 0, Q_ops - 1)

if __name__ == '__main__':
    solve()
