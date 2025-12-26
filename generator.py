import os, random

def gen_case(seed: int, N: int, Q: int, out_path: str):
    import random
    rnd = random.Random(seed)

    active = {}          # eid -> (typ,a,b)
    active_ids = []      # list of eids
    pos = {}             # eid -> index in active_ids
    next_id = 1
    ops = []

    val = [0]*(N+1)
    for i in range(1, N+1):
        val[i] = rnd.getrandbits(1)

    def gen_edge():
        a = rnd.randint(1, N)
        b = rnd.randint(1, N)
        while b == a:
            b = rnd.randint(1, N)
        w = val[a] ^ val[b]
        if rnd.random() < 0.08:
            w ^= 1
        typ = 'S' if w == 0 else 'D'
        return typ, a, b

    for _ in range(Q):
        r = rnd.random()
        if r < 0.22:
            ops.append("Q")
        elif r < 0.72 or not active_ids:
            eid = next_id; next_id += 1
            typ, a, b = gen_edge()
            active[eid] = (typ, a, b)

            pos[eid] = len(active_ids)
            active_ids.append(eid)

            ops.append(f"A {eid} {typ} {a} {b}")
        else:
            # O(1) random remove
            idx = rnd.randrange(len(active_ids))
            eid = active_ids[idx]

            last = active_ids[-1]
            active_ids[idx] = last
            pos[last] = idx
            active_ids.pop()

            pos.pop(eid, None)
            active.pop(eid, None)

            ops.append(f"R {eid}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"{N} {Q}\n")
        f.write("\n".join(ops))
        f.write("\n")


def main():
    os.makedirs("data", exist_ok=True)

    # N,Q are kept <= 1e5 to keep I/O and checking manageable.
    cases = []
    for _ in range(20):
        cases.append((4000, 35000))
    for _ in range(20):
        cases.append((30000, 90000))
    for _ in range(10):
        cases.append((100000, 100000))

    for idx, (N, Q) in enumerate(cases, 1):
        seed = idx * 9109
        out_path = f"data/case_{idx:04d}.in"
        gen_case(seed, N, Q, out_path)

if __name__ == "__main__":
    main()
