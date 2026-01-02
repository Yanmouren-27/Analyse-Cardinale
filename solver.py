import sys

# Increase recursion depth just in case
sys.setrecursionlimit(300000)

def solve():
    # Fast I/O
    input_data = sys.stdin.read().split()
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
    
    for _ in range(Q_ops):
        try:
            op_type = next(iterator)
        except StopIteration:
            break
            
        if op_type == 'A':
            eid = int(next(iterator))
            etype = next(iterator)
            u = int(next(iterator))
            v = int(next(iterator))
            w = 0 if etype == 'S' else 1
            active_start[eid] = (u, v, w, current_time)
        elif op_type == 'R':
            eid = int(next(iterator))
            if eid in active_start:
                u, v, w, start = active_start.pop(eid)
                if start <= current_time - 1:
                    edges.append((u, v, w, eid, start, current_time - 1))
        elif op_type == 'Q' or op_type == 'C':
            queries.append((current_time, op_type))
        
        current_time += 1
        
    final_time = Q_ops - 1
    for eid, (u, v, w, start) in active_start.items():
        if start <= final_time:
            edges.append((u, v, w, eid, start, final_time))
            
    if Q_ops == 0:
        return

    # Build Segment Tree
    tree_size = 4 * Q_ops
    tree = [[] for _ in range(tree_size)]
    
    def add_to_tree(node, l, r, ql, qr, edge):
        if ql > r or qr < l:
            return
        if ql <= l and r <= qr:
            tree[node].append(edge)
            return
        mid = (l + r) // 2
        if ql <= mid:
            add_to_tree(2 * node, l, mid, ql, qr, edge)
        if qr > mid:
            add_to_tree(2 * node + 1, mid + 1, r, ql, qr, edge)
            
    for u, v, w, eid, start, end in edges:
        add_to_tree(1, 0, Q_ops - 1, start, end, (u, v, w, eid))

    # DSU State
    parent = list(range(N + 1))
    rank = [0] * (N + 1)
    parity = [0] * (N + 1)
    
    history = []
    current_solution = []
    
    # Iterative DFS Stack: [node, l, r, stage, ops_count, level_solution_count]
    stack = [[1, 0, Q_ops - 1, 0, 0, 0]]
    
    query_idx = 0
    num_queries = len(queries)
    MAX_WITNESS = 5000
    
    write = sys.stdout.write
    
    while stack:
        frame = stack[-1]
        node, l, r, stage, _, _ = frame
        
        if stage == 0:
            # Pruning
            if query_idx >= num_queries or queries[query_idx][0] > r:
                stack.pop()
                continue
                
            ops_count = 0
            level_solution_count = 0
            
            for u, v, w, eid in tree[node]:
                # Inline find(u)
                curr = u
                p_u = 0
                while curr != parent[curr]:
                    p_u ^= parity[curr]
                    curr = parent[curr]
                root_u, par_u = curr, p_u
                
                # Inline find(v)
                curr = v
                p_v = 0
                while curr != parent[curr]:
                    p_v ^= parity[curr]
                    curr = parent[curr]
                root_v, par_v = curr, p_v
                
                if root_u != root_v:
                    if rank[root_u] < rank[root_v]:
                        root_u, root_v = root_v, root_u
                    
                    w_new = par_u ^ par_v ^ w
                    parent[root_v] = root_u
                    parity[root_v] = w_new
                    
                    old_rank_u = rank[root_u]
                    if rank[root_u] == rank[root_v]:
                        rank[root_u] += 1
                        
                    history.append((root_v, root_u, old_rank_u))
                    current_solution.append(eid)
                    level_solution_count += 1
                    ops_count += 1
                else:
                    if (par_u ^ par_v) == w:
                        current_solution.append(eid)
                        level_solution_count += 1
            
            frame[4] = ops_count
            frame[5] = level_solution_count
            
            if l == r:
                while query_idx < num_queries and queries[query_idx][0] == l:
                    _, q_type = queries[query_idx]
                    k_raw = len(current_solution)
                    k = min(k_raw, MAX_WITNESS, N)
                    
                    if q_type == 'Q':
                        write(f"{k}\n")
                    else:
                        if k == 0:
                            write("0\n")
                        else:
                            write(f"{k} {' '.join(map(str, current_solution[:k]))}\n")
                    
                    query_idx += 1
                frame[3] = 3
            else:
                frame[3] = 1
                mid = (l + r) // 2
                stack.append([2 * node, l, mid, 0, 0, 0])
                
        elif stage == 1:
            frame[3] = 2
            mid = (l + r) // 2
            stack.append([2 * node + 1, mid + 1, r, 0, 0, 0])
            
        elif stage == 2:
            frame[3] = 3
            
        elif stage == 3:
            ops_count = frame[4]
            level_solution_count = frame[5]
            
            for _ in range(ops_count):
                child, par, old_rank = history.pop()
                parent[child] = child
                parity[child] = 0
                rank[par] = old_rank
                
            if level_solution_count > 0:
                del current_solution[-level_solution_count:]
                
            stack.pop()

if __name__ == '__main__':
    solve()
