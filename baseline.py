# baseline.py
import sys

def main():
    data = sys.stdin.buffer.read()
    n = len(data)
    i = 0

    def skip():
        nonlocal i
        while i < n and data[i] <= 32:
            i += 1

    def read_int():
        nonlocal i
        skip()
        s = 0
        while i < n and data[i] > 32:
            s = s * 10 + (data[i] - 48)
            i += 1
        return s

    def read_tok():
        nonlocal i
        skip()
        j = i
        while j < n and data[j] > 32:
            j += 1
        tok = data[i:j]
        i = j
        return tok

    _N = read_int()
    Q = read_int()

    active = {}  # id -> 1
    out = bytearray()

    for _ in range(Q):
        op = read_tok()
        if op == b"A":
            eid = read_int()
            _typ = read_tok()
            _a = read_int()
            _b = read_int()
            active[eid] = 1
        elif op == b"R":
            eid = read_int()
            active.pop(eid, None)
        else:
            # Q or C
            if active:
                eid = next(iter(active))  # 任取一条存活边
                if op == b"C":
                    out += b"1 " + str(eid).encode() + b"\n"
                else:
                    out += b"1\n"
            else:
                out += b"0\n"

    sys.stdout.buffer.write(out)

if __name__ == "__main__":
    main()
