#!/usr/bin/env python3
"""PC side for the ESP32 intrusion detector.
Frame format from the firmware:  P:1,D:45,S:0*7D   (XOR checksum of the payload)

  python ids_live.py record   --port COM5 --label normal --seconds 600 --out normal_train.csv
  python ids_live.py train    normal_train.csv --model model.joblib
  python ids_live.py evaluate --model model.joblib normal_test.csv walk.csv loiter.csv cover.csv
  python ids_live.py live     --port COM5 --model model.joblib

Needs: pip install pyserial numpy scikit-learn joblib
"""
import argparse, csv, sys, time
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

WINDOW = 20          # frames per window = 4 s at 5 frames per second
FIRST_FRAME_TIMEOUT = 60   # s to wait for the first frame (firmware warm-up is 30 s)
FEATURES = ["pir_ratio", "pir_transitions", "sound_ratio", "sound_transitions",
            "pir_sound_overlap", "dist_mean", "dist_std", "dist_min", "dist_range",
            "no_echo_ratio"]


def checksum(payload):
    r = 0
    for ch in payload:
        r ^= ord(ch)
    return f"{r:02X}"


def parse_frame(line):
    """Return (p, d, s) or None for comments, malformed lines and bad checksums."""
    line = line.strip()
    if not line or line.startswith("#") or line.count("*") != 1:
        return None
    payload, given = line.split("*")
    if len(given) != 2 or given.upper() != checksum(payload):
        return None
    try:
        kv = dict(item.split(":") for item in payload.split(","))
        if set(kv) != {"P", "D", "S"}:
            return None
        p, d, s = int(kv["P"]), int(kv["D"]), int(kv["S"])
    except ValueError:
        return None
    if p not in (0, 1) or s not in (0, 1) or not 0 <= d <= 400:
        return None
    return p, d, s


def window_features(w):
    a = np.array(w, dtype=float)
    pir, dist, snd = a[:, 0], a[:, 1], a[:, 2]
    valid = dist[dist > 0]                    # D=0 is "no echo", not a distance: keep it out of the distance stats
    if len(valid) == 0:                       # whole window had no echo: no_echo_ratio carries it
        d_stats = [0.0, 0.0, 0.0, 0.0]
    else:
        d_stats = [valid.mean(), valid.std(), valid.min(), valid.max() - valid.min()]
    return [pir.mean(), np.abs(np.diff(pir)).sum(),
            snd.mean(), np.abs(np.diff(snd)).sum(),
            float(((pir > 0) & (snd > 0)).mean()),
            *d_stats,
            float((dist == 0).mean())]


def make_windows(frames):
    return np.array([window_features(frames[i:i + WINDOW])
                     for i in range(0, len(frames) - WINDOW + 1, WINDOW)])


def read_csv(path):
    frames, label = [], None
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            label = row["label"]
            frames.append((int(row["P"]), int(row["D"]), int(row["S"])))
    return frames, label


def line_source(args):
    """Yield text lines from a serial port, or from a file with --replay."""
    if args.replay:
        with open(args.replay) as f:
            yield from f
        return
    import serial
    ser = serial.Serial()                     # set DTR and RTS low before opening: asserted lines usually reset the ESP32
    ser.port, ser.baudrate, ser.timeout = args.port, args.baud, 2
    ser.dtr = False
    ser.rts = False
    ser.open()
    with ser:
        while True:
            yield ser.readline().decode(errors="ignore")


def cmd_record(args):
    n = bad = pre = 0
    t0 = None                                 # clock starts at the first valid frame, so the 30 s warm-up is not counted
    started = time.time()
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["t", "label", "P", "D", "S"])
        try:
            for line in line_source(args):
                if t0 is None and time.time() - started > FIRST_FRAME_TIMEOUT:
                    print(f"\nNo valid frame within {FIRST_FRAME_TIMEOUT} s. Check port, baud and wiring.")
                    break
                if t0 is not None and args.seconds and time.time() - t0 > args.seconds:
                    break
                fr = parse_frame(line)
                if fr is None:
                    if line.strip() and not line.startswith("#"):
                        if t0 is None:
                            pre += 1          # boot log before the first frame, not a corrupted frame
                        else:
                            bad += 1
                    continue
                if t0 is None:
                    t0 = time.time()
                w.writerow([round(time.time() - t0, 3), args.label, *fr]); f.flush(); n += 1
                if n % 25 == 0:
                    print(f"\r{n} frames, {bad} rejected", end="", flush=True)
        except KeyboardInterrupt:
            pass
    print(f"\nSaved {n} frames to {args.out} ({bad} rejected, {n // WINDOW} windows)"
          + (f", ignored {pre} non-frame lines before the first frame" if pre else ""))


def cmd_train(args):
    X = np.vstack([make_windows(read_csv(p)[0]) for p in args.csv])
    if len(X) < 100:
        print(f"Warning: only {len(X)} windows. Aim for 150 or more (about 10 minutes).")
    model = IsolationForest(n_estimators=200, contamination=0.02, random_state=42).fit(X)
    joblib.dump(model, args.model)
    print(f"Trained on {len(X)} normal windows, saved {args.model}")


def cmd_evaluate(args):
    model = joblib.load(args.model)
    print(f"{'label':14s}{'windows':>8s}{'flagged':>9s}")
    for p in args.csv:
        frames, label = read_csv(p)
        X = make_windows(frames)
        if not len(X):
            print(f"{p}: fewer than {WINDOW} frames"); continue
        flag = model.predict(X) == -1
        print(f"{label:14s}{len(X):8d}{flag.mean() * 100:8.1f}%")
    print("For the 'normal' row, flagged % is the false alarm rate. For the others it is the detection rate.")


def cmd_live(args):
    model = joblib.load(args.model)
    buf, bad, seen = [], 0, False
    for line in line_source(args):
        fr = parse_frame(line)
        if fr is None:
            bad += seen and line.strip() != "" and not line.startswith("#")   # boot log before the first frame is not counted
            continue
        seen = True
        buf.append(fr)
        if len(buf) == WINDOW:
            x = np.array([window_features(buf)])
            score = -model.score_samples(x)[0]
            alert = model.predict(x)[0] == -1
            print(f"score={score:.3f}  {'ALERT' if alert else 'ok   '}  (rejected frames so far: {bad})", flush=True)
            buf = []


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("record", "live"):
        sp = sub.add_parser(name)
        sp.add_argument("--port"); sp.add_argument("--baud", type=int, default=115200)
        sp.add_argument("--replay", help="read frames from a text file instead of a serial port")
    sub.choices["record"].add_argument("--label", required=True)
    sub.choices["record"].add_argument("--seconds", type=int, default=0)
    sub.choices["record"].add_argument("--out", required=True)
    sub.choices["live"].add_argument("--model", default="model.joblib")
    sp = sub.add_parser("train"); sp.add_argument("csv", nargs="+"); sp.add_argument("--model", default="model.joblib")
    sp = sub.add_parser("evaluate"); sp.add_argument("csv", nargs="+"); sp.add_argument("--model", default="model.joblib")
    args = ap.parse_args()
    if args.cmd in ("record", "live") and not (args.port or args.replay):
        ap.error("give --port COMx or --replay file")
    {"record": cmd_record, "train": cmd_train, "evaluate": cmd_evaluate, "live": cmd_live}[args.cmd](args)
