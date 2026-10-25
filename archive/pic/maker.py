from frames import checksum
import frames

def make_frame(p, d, s):
    if p not in (0, 1) or s not in (0, 1):
        raise ValueError(f"bad P or S: {p}, {s}")
    if not (d == 0 or 2 <= d <= 400):
        raise ValueError(f"bad D: {d}")
    payload = f"P:{p},D:{d},S:{s}"
    return f"{payload}*{checksum(payload)}"

if __name__ == "__main__":
    count = 0
    fails = 0
    for p in (0, 1):
        for s in (0, 1):
            for d in [0] + list(range(2, 401)):
                frame = make_frame(p, d, s)
                parsed = frames.parse_frame(frame)
                if parsed != (p, d, s):
                    fails += 1
                    print(p, d, s, frame)
                count += 1
    print(count, "tested,", fails, "failed")

