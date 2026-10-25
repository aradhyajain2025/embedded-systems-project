"""Live mode: score frames as they arrive.
Usage: python live_serial.py COM6 [baud]   frames from a (virtual) COM port, needs pyserial
       python live_serial.py frames.txt    frames from a log file, one per line
       Get-Clipboard | python live_serial.py -    frames copied from the MPLAB UART window (PowerShell)
Scored frames always come from the firmware. generator.py is used only to make the normal training data.
"""
import os, random, sys
import numpy as np
from frames import parse_frame
from ids_pipeline import WINDOW, make_windows, parse_stream, score, train, window_features
from generator import generate_frames, NORMAL

TRAIN_FRAMES = 3000    # 150 windows of normal behaviour


def frame_source(src, baud):
    if src == "-":
        yield from sys.stdin
    elif os.path.isfile(src):
        with open(src, encoding="utf-8-sig") as f:
            yield from f
    elif src.upper().startswith("COM") or src.startswith("/dev/"):
        try:
            import serial
        except ImportError:
            sys.exit("pyserial is not installed: python -m pip install pyserial")
        try:
            with serial.Serial(src, baud, timeout=2) as ser:
                while True:
                    yield ser.readline().decode(errors="ignore")   # "" on timeout, skipped by the caller
        except serial.SerialException as e:
            sys.exit(f"Cannot use {src}: {e}")
    else:
        sys.exit(f"'{src}' is not a file, a COM port or '-'")


if len(sys.argv) < 2:
    sys.exit(__doc__)
src = sys.argv[1]
baud = int(sys.argv[2]) if len(sys.argv) > 2 else 9600

random.seed(1)         # same training data every run, so demo results repeat
recs, _ = parse_stream(generate_frames(TRAIN_FRAMES, NORMAL))
X_train = make_windows(recs)
model = train(X_train)
print(f"Trained on {len(recs)} normal frames -> {len(X_train)} windows")

buf, bad, n_win = [], 0, 0
try:
    for line in frame_source(src, baud):
        line = line.lstrip("﻿").strip()   # a BOM from PowerShell or Notepad would fail the first frame
        if not line:
            continue                           # blank line or serial timeout, not a rejected frame
        r = parse_frame(line)
        if r is None:
            bad += 1
            continue
        buf.append(r)
        if len(buf) == WINDOW:
            n_win += 1
            s, f = score(model, np.array([window_features(buf)]))
            print(f"window {n_win:3d}  score={s[0]:.3f} {'ALERT' if f[0] else 'ok'} (rejected so far: {bad})")
            buf = []
except KeyboardInterrupt:
    pass
print(f"Done: {n_win} windows scored, {bad} frames rejected, {len(buf)} frames left over (less than one window)")
