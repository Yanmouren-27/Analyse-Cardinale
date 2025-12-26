import os, csv, subprocess, sys, random
from typing import Dict, Tuple, List, Optional
from ref_check import check_subset_sparse

DATA_DIR = "data"
OUT_DIR = "outputs"
REPORT_DIR = "reports"
SOLVER = "solver.py"
TIME_LIMIT = 8.0  # seconds per run
P = 2  # exponent (>1): slow early, fast late

# Evaluator auditing:
# - It will run the solver multiple times (RUNS).
# - Each run deterministically turns some 'Q' in the input into 'C' (checked query).
# - For 'Q': solver must output a single integer K (claim).
# - For 'C': solver must output a witness subset line: "K id1 id2 ... idK".
# - All runs must produce identical K for every query index; otherwise the whole case scores 0.
# - For each 'C', the witness subset must be satisfiable under current active constraints.
RUNS = 4
CHECK_PROB = 0.05
MAX_WITNESS = 5000  # hard cap to prevent pathological output on checked queries

def clamp(x: float, lo: float, hi: float) -> float:
    if x < lo: return lo
    if x > hi: return hi
    return x

def score_query(k: int, k0: int, m: int, P: int = 4) -> float:
    # full-set priority
    if k == m:
        return 200.0
    if m == 0:
        return 0.0
    if k <= k0:
        return clamp(100.0 * (k / max(1.0, float(k0))), 0.0, 200.0)
    if m <= k0:
        return 100.0
    z = (k - k0) / float(m - k0)
    z = clamp(z, 0.0, 1.0)
    sc = 100.0 + 100.0 * (z ** P)
    return clamp(sc, 0.0, 200.0)

def run_solver(input_text: str, timeout_s: float) -> tuple[Optional[str], Optional[str]]:
    try:
        p = subprocess.run(
            [sys.executable, SOLVER],
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"
    if p.returncode != 0:
        return None, "RUNTIME_ERROR"
    return p.stdout, None

def make_masked_input(raw_lines: List[str], seed: int) -> tuple[str, List[str]]:
    rnd = random.Random(seed)
    masked = [raw_lines[0]]
    ops = []
    for ln in raw_lines[1:]:
        if ln == "Q":
            ln2 = "C" if rnd.random() < CHECK_PROB else "Q"
            masked.append(ln2)
            ops.append(ln2)
        else:
            masked.append(ln)
            ops.append(ln)
    return "\n".join(masked) + "\n", ops

def parse_outputs(out_text: str, qcnt: int) -> Optional[List[str]]:
    lines = [ln.strip() for ln in out_text.splitlines() if ln.strip() != ""]
    if len(lines) != qcnt:
        return None
    return lines

def evaluate_case(case_name: str, in_path: str, case_seed: int) -> float:
    raw_lines = [ln.strip() for ln in open(in_path, "r", encoding="utf-8").read().splitlines() if ln.strip() != ""]
    N, Q = map(int, raw_lines[0].split())
    file_ops = raw_lines[1:]

    q_positions = [i for i, ln in enumerate(file_ops) if ln == "Q"]
    qcnt = len(q_positions)
    if qcnt == 0:
        return 0.0

    all_claims: List[List[int]] = []
    all_witness: List[Dict[int, List[int]]] = []

    for r in range(RUNS):
        masked_input, masked_ops = make_masked_input(
            raw_lines,
            seed=case_seed * 10007 + r * 9176 + 12345
        )

        # Save masked input for debugging/repro
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(f"{OUT_DIR}/{case_name}.run{r}.masked.in", "w", encoding="utf-8") as f:
            f.write(masked_input)

        out_text, err = run_solver(masked_input, timeout_s=TIME_LIMIT)
        if err:
            with open(f"{OUT_DIR}/{case_name}.run{r}.err.txt", "w", encoding="utf-8") as f:
                f.write(err)
            return 0.0

        # Save solver raw output
        with open(f"{OUT_DIR}/{case_name}.run{r}.out", "w", encoding="utf-8") as f:
            f.write(out_text)

        lines = parse_outputs(out_text, qcnt)
        if lines is None:
            return 0.0

        claims: List[int] = []
        witness: Dict[int, List[int]] = {}

        for qi, t in enumerate(q_positions):
            parts = lines[qi].split()
            if len(parts) == 0 or not parts[0].lstrip("-").isdigit():
                return 0.0
            k = int(parts[0])
            if k < 0 or k > N:
                return 0.0
            claims.append(k)

            if masked_ops[t] == "C":
                if k > MAX_WITNESS:
                    return 0.0
                if len(parts) != 1 + k:
                    return 0.0
                ids = []
                seen = set()
                for x in parts[1:]:
                    if not x.isdigit():
                        return 0.0
                    eid = int(x)
                    if eid in seen:
                        return 0.0
                    seen.add(eid)
                    ids.append(eid)
                witness[qi] = ids
            else:
                if len(parts) != 1:
                    return 0.0

        all_claims.append(claims)
        all_witness.append(witness)

    # Claims must match across runs
    for qi in range(qcnt):
        v = all_claims[0][qi]
        for r in range(1, RUNS):
            if all_claims[r][qi] != v:
                return 0.0
    claims = all_claims[0]

    active: Dict[int, Tuple[int, int, int]] = {}
    total = 0.0
    qi = 0

    for t, ln in enumerate(file_ops):
        if ln[0] == 'A':
            _, sid, typ, a, b = ln.split()
            eid = int(sid); a = int(a); b = int(b)
            w = 0 if typ == 'S' else 1
            active[eid] = (a, b, w)
        elif ln[0] == 'R':
            _, sid = ln.split()
            eid = int(sid)
            active.pop(eid, None)
        else:
            m = len(active)
            k0 = 0 if m == 0 else 1  # baseline size
            k = claims[qi]
            if k > m:
                return 0.0

            # Validate all audited witnesses (size equals k because witness line is "K ids")
            for r in range(RUNS):
                ids = all_witness[r].get(qi)
                if ids is None:
                    continue
                if len(ids) != k:
                    return 0.0
                for eid in ids:
                    if eid not in active:
                        return 0.0
                if not check_subset_sparse(active, ids):
                    return 0.0

            total += score_query(k, k0, m, P=P)
            qi += 1

    return total / max(1, qcnt)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

    names = [fn[:-3] for fn in os.listdir(DATA_DIR) if fn.startswith("case_") and fn.endswith(".in")]
    names.sort()

    rows = []
    for name in names:
        in_path = f"{DATA_DIR}/{name}.in"
        case_seed = int(name.split("_")[1]) * 9109
        sc = evaluate_case(name, in_path, case_seed)
        rows.append((name, sc))

    with open(f"{REPORT_DIR}/scores.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "score"])
        for name, s in rows:
            w.writerow([name, f"{s:.7f}"])

    avg = (sum(s for _, s in rows) / max(1, len(rows))) if rows else 0.0
    with open(f"{REPORT_DIR}/summary.txt", "w", newline="", encoding="utf-8") as f:
        f.write(f"average_score,{avg:.7f}\n")

    print("Final Average Score:", f"{avg:.7f}")

if __name__ == "__main__":
    main()
