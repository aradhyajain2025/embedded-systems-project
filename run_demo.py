"""End-to-end demo: generated firmware frames -> parser -> windows -> features -> Isolation Forest.
Usage: python run_demo.py

Training uses NORMAL frames only. The test stream mixes NORMAL with INTRUDER and BLOCKING
(covered ultrasonic sensor) segments, with 2% UART corruption. All data is simulated, so
the results validate the pipeline, not real-world accuracy.
"""
import random
from collections import Counter
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ids_pipeline import *
from generator import generate_frames, NORMAL, INTRUDER, BLOCKING

TRAIN_FRAMES = 3000            # 150 windows of normal behaviour
CORRUPT_RATE = 0.02            # fraction of frames with one character flipped
CLASSES = ["normal", "intruder", "blocking"]
MODES = {"normal": NORMAL, "intruder": INTRUDER, "blocking": BLOCKING}
# (class, windows). Each segment is a whole number of windows.
PLAN = [("normal", 30), ("intruder", 6), ("normal", 25), ("blocking", 6),
        ("normal", 25), ("intruder", 6), ("normal", 25), ("blocking", 6), ("normal", 25)]


def corrupt(frame):
    """Replace one payload character, as line noise would. XOR always catches a single flip."""
    i = random.randrange(frame.index("*"))
    return frame[:i] + random.choice([c for c in "0123456789,:PDS" if c != frame[i]]) + frame[i + 1:]


def build_stream(plan, corrupt_rate):
    """Return (lines, labels) with one label per frame."""
    lines, labels = [], []
    for cls, n_windows in plan:
        for f in generate_frames(n_windows * WINDOW, MODES[cls]):
            lines.append(corrupt(f) if random.random() < corrupt_rate else f)
            labels.append(cls)
    return lines, labels


def make_labelled_windows(lines, labels):
    """Window by counting WINDOW valid frames. Keep only windows whose frames share one label."""
    recs, rec_labels, bad = [], [], 0
    for ln, lab in zip(lines, labels):
        r = parse_frame(ln)
        if r is None:
            bad += 1
        else:
            recs.append(r)
            rec_labels.append(lab)
    X, y, mixed = [], [], 0
    for i in range(0, len(recs) - WINDOW + 1, WINDOW):
        labs = set(rec_labels[i:i + WINDOW])
        if len(labs) > 1:
            mixed += 1
            continue
        X.append(window_features(recs[i:i + WINDOW]))
        y.append(labs.pop())
    return np.array(X), np.array(y), bad, mixed


def train_model(seed):
    random.seed(seed)
    recs, _ = parse_stream(generate_frames(TRAIN_FRAMES, NORMAL))
    return train(make_windows(recs)), len(recs)


def run(train_seed, test_seed):
    model, n_train = train_model(train_seed)
    random.seed(test_seed)
    lines, labels = build_stream(PLAN, CORRUPT_RATE)
    X, y, bad, mixed = make_labelled_windows(lines, labels)
    s, flag = score(model, X)
    return model, n_train, lines, bad, mixed, y, s, flag


# ---- single detailed run ----
model, n_train, lines, bad, mixed, y, s, flag = run(train_seed=1, test_seed=7)
print(f"Training: {n_train} normal frames -> {n_train // WINDOW} windows")
print(f"Test stream: {len(lines)} frames sent, {bad} rejected by checksum ({100*bad/len(lines):.1f}%), "
      f"{mixed} windows dropped for mixing classes")
print("\nPer-class detection (flagged as anomaly):")
for k in CLASSES:
    m = y == k
    print(f"  {k:9s} {flag[m].mean()*100:5.1f}%  ({flag[m].sum()}/{m.sum()} windows)")
attack = y != "normal"
print(f"\nDetection rate (attacks): {flag[attack].mean()*100:.1f}%")
print(f"False alarm rate (normal): {flag[~attack].mean()*100:.1f}%")

# ---- repeat over seeds: one run is one random draw ----
N_SEEDS = 20
rates = {k: [] for k in CLASSES}
for seed in range(100, 100 + N_SEEDS):
    *_, y_i, _, flag_i = run(train_seed=seed, test_seed=seed + 1000)
    for k in CLASSES:
        rates[k].append(flag_i[y_i == k].mean() * 100)
print(f"\nOver {N_SEEDS} different train/test seeds (mean, min to max):")
for k in CLASSES:
    r = rates[k]
    print(f"  {k:9s} {np.mean(r):5.1f}%  ({min(r):.0f} to {max(r):.0f})")
print("False alarms are partly set by the model's contamination=0.02 threshold choice.")

# ---- plot ----
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(s, lw=1.2, color="#1f4e79", label="anomaly score")
cls_col = {"intruder": "#c0392b", "blocking": "#16a085"}
i = 0
while i < len(y):
    if y[i] != "normal":
        j = i
        while j + 1 < len(y) and y[j + 1] == y[i]:
            j += 1
        ax.axvspan(i - .5, j + .5, color=cls_col[y[i]], alpha=.18, label=f"{y[i]} (ground truth)")
        i = j
    i += 1
ax.axhline(-model.offset_, ls="--", color="k", lw=1, label="decision threshold")
h, l = ax.get_legend_handles_labels()
u = dict(zip(l, h))
ax.legend(u.values(), u.keys(), fontsize=8, loc="upper right")
ax.set_xlabel(f"window index ({WINDOW / SAMPLE_HZ:.0f} s each)")
ax.set_ylabel("anomaly score (higher = more anomalous)")
ax.set_title("Isolation Forest anomaly score over time (simulated sensor stream)")
plt.tight_layout()
plt.savefig("anomaly_scores.png", dpi=150)
print("\nSaved anomaly_scores.png")

# ---- live-style verdicts around the first attack ----
first = int(np.argmax(y != "normal"))
print("\nSample live output:")
for idx in range(max(0, first - 3), min(len(y), first + 9)):
    print(f"  win {idx:3d} score={s[idx]:.3f} {'ALERT' if flag[idx] else 'ok   '}  (truth: {y[idx]})")
