"""Make SIMULATED frame files in the ESP32 format, to rehearse the PC pipeline before the sensors arrive.

  python make_replays.py            writes replays/*.txt
  python run_replay_demo.py         (or run the commands it prints) record -> train -> evaluate

Every behaviour below is my assumption, not a measurement. Results from these files are
"simulated replay" results and must never be reported as hardware results.
Assumed hardware behaviour: PIR output stays high at least 3 s (15 frames), sound lasts
1 frame unless the noise lasts, covered HC-SR04 gives D=0 on most frames.
"""
import os
import random
from ids_live import checksum

OUT = "replays"
CORRUPT = 0.01          # fraction of frames with one character changed


def frame(p, d, s):
    payload = f"P:{p},D:{d},S:{s}"
    return f"{payload}*{checksum(payload)}"


def corrupt(line):
    i = random.randrange(line.index("*"))
    return line[:i] + random.choice([c for c in "0123456789,:PDS" if c != line[i]]) + line[i + 1:]


def generate(n, kind):
    """Return n frame lines of one behaviour: normal, walk, loiter or cover."""
    lines, hold, d = [], 0, 250.0
    for _ in range(n):
        if kind == "normal":
            if hold == 0 and random.random() < 0.004:
                hold = 15 + random.randint(0, 8)           # a passer-by or a PIR false trigger
            dist = 250 + random.randint(-3, 3)
            s = 1 if random.random() < 0.01 else 0
            glitch = 0.01
        elif kind == "walk":                               # someone walks in and moves around
            if hold == 0 and random.random() < 0.08:
                hold = 15 + random.randint(0, 25)
            d = max(40.0, min(250.0, d + random.randint(-12, 6)))
            dist = int(d)
            s = 1 if random.random() < 0.06 else 0
            glitch = 0.01
        elif kind == "loiter":                             # someone stays close and fidgets
            if hold == 0 and random.random() < 0.05:
                hold = 15 + random.randint(0, 10)
            dist = 100 + random.randint(-5, 5)
            s = 1 if random.random() < 0.03 else 0
            glitch = 0.01
        elif kind == "cover":                              # sensor blocked, room otherwise quiet
            if hold == 0 and random.random() < 0.004:
                hold = 15 + random.randint(0, 8)
            dist = 250 + random.randint(-3, 3)
            s = 1 if random.random() < 0.01 else 0
            glitch = 0.9
        else:
            raise ValueError(kind)
        p = 1 if hold > 0 else 0
        hold = max(0, hold - 1)
        dist = 0 if random.random() < glitch else max(1, min(400, dist))
        line = frame(p, dist, s)
        lines.append(corrupt(line) if random.random() < CORRUPT else line)
    return lines


# (file name, behaviour, frames). 3000 frames = 10 min = 150 windows at 5 frames per second.
FILES = [("normal_train", "normal", 3000), ("normal_test", "normal", 900),
         ("walk", "walk", 400), ("loiter", "loiter", 400), ("cover", "cover", 400)]


if __name__ == "__main__":
    random.seed(11)
    os.makedirs(OUT, exist_ok=True)
    for name, kind, n in FILES:
        path = f"{OUT}/{name}.txt"
        with open(path, "w") as f:
            f.write("# warming up sensors\n# running\n")
            f.write("\n".join(generate(n, kind)) + "\n")
        print(f"wrote {path}: {n} frames ({n // 20} windows), behaviour {kind}")
    print("\nNext:")
    for name, kind, _ in FILES:
        print(f"  python ids_live.py record --replay {OUT}/{name}.txt --label {kind if name != 'normal_test' else 'normal'} --out {OUT}/{name}.csv")
    print(f"  python ids_live.py train {OUT}/normal_train.csv --model {OUT}/model.joblib")
    print(f"  python ids_live.py evaluate --model {OUT}/model.joblib {OUT}/normal_test.csv {OUT}/walk.csv {OUT}/loiter.csv {OUT}/cover.csv")
