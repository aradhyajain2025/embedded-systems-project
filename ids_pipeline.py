"""PC-side pipeline: frame parsing -> windowing -> features -> Isolation Forest.

FRAME FORMAT (from frames.py): P:<0|1>,D:<0|2..400>,S:<0|1>*<CS>
CS = XOR of every payload character (everything before '*'), 2 uppercase hex digits.
Frames carry no seq or timestamp, so windows are built by counting WINDOW valid frames.
D=0 means the ultrasonic sensor got no echo. It is NOT a distance, so the distance
features ignore it and no_echo_ratio reports how much of the window it covers.
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from frames import parse_frame

SAMPLE_HZ = 5          # frames per second (generator rate; confirm against the firmware)
WINDOW = 20            # frames per window (= 4 s at SAMPLE_HZ)
FEATURE_NAMES = ["pir_ratio", "pir_transitions", "dist_mean", "dist_std",
                 "dist_min", "dist_range", "sound_ratio", "sound_transitions",
                 "pir_sound_overlap", "no_echo_ratio"]


def parse_stream(lines):
    """Parse many lines; returns (records, n_rejected). A record is (pir, dist_cm, sound)."""
    recs, bad = [], 0
    for ln in lines:
        r = parse_frame(ln.strip())
        if r is None:
            bad += 1
        else:
            recs.append(r)
    return recs, bad


def window_features(w):
    pir = np.array([r[0] for r in w])
    d_all = np.array([r[1] for r in w], dtype=float)
    snd = np.array([r[2] for r in w])
    d = d_all[d_all > 0]                      # drop no-echo frames from distance stats
    if len(d) == 0:                           # whole window had no echo: flagged via no_echo_ratio
        d_stats = [0.0, 0.0, 0.0, 0.0]
    else:
        d_stats = [d.mean(), d.std(), d.min(), d.max() - d.min()]
    return [pir.mean(), np.abs(np.diff(pir)).sum(),
            *d_stats,
            snd.mean(), np.abs(np.diff(snd)).sum(),
            float((pir & snd).mean()),
            float((d_all == 0).mean())]


def make_windows(recs, size=WINDOW):
    X = []
    for i in range(0, len(recs) - size + 1, size):
        X.append(window_features(recs[i:i + size]))
    return np.array(X)


def train(X_normal, contamination=0.02, seed=42):
    return IsolationForest(n_estimators=200, contamination=contamination,
                           random_state=seed).fit(X_normal)


def score(model, X):
    """Higher = more anomalous. Returns (score, is_anomaly)."""
    s = -model.score_samples(X)
    return s, model.predict(X) == -1
