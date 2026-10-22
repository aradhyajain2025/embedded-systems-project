"""Live mode: score frames as they arrive.
Usage: python live_serial.py COM6 [baud]   frames from a (virtual) COM port, needs pyserial
       python live_serial.py frames.txt    frames from a log file, one per line
       python live_serial.py sim           frames from generator.py (NORMAL then INTRUDER)
"""
import os, random, sys
import numpy as np
from ids_pipeline import *
from generator import generate_frames, NORMAL, INTRUDER

TRAIN_FRAMES = 3000    # 150 windows of normal behaviour


def frame_source(src, baud):
    if src == "sim":
        yield from generate_frames(400, NORMAL)
        yield from generate_frames(200, INTRUDER)
    elif os.path.isfile(src):
        with open(src) as f:
            yield from f
    else:
        import serial
        with serial.Serial(src, baud, timeout=2) as ser:
            while True:
                yield ser.readline().decode(errors="ignore")


src = sys.argv[1]
baud = int(sys.argv[2]) if len(sys.argv) > 2 else 9600

random.seed(1)         # same training data every run, so demo results repeat
recs, _ = parse_stream(generate_frames(TRAIN_FRAMES, NORMAL))
X_train = make_windows(recs)
model = train(X_train)
print(f"Trained on {len(recs)} normal frames -> {len(X_train)} windows")

buf, bad = [], 0
for line in frame_source(src, baud):
    r = parse_frame(line.strip())
    if r is None:
        bad += 1
        continue
    buf.append(r)
    if len(buf) == WINDOW:
        s, f = score(model, np.array([window_features(buf)]))
        print(f"score={s[0]:.3f} {'ALERT' if f[0] else 'ok'} (rejected so far: {bad})")
        buf = []
