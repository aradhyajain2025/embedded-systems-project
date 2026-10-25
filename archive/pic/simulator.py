"""Sensor behaviour model (documented assumptions, used because no hardware).
PIR: binary, high when motion in view. Ultrasonic: distance to nearest object (cm),
~250 cm to the far wall when empty, noise +-3 cm. Sound: digital, high on loud event.
"""
import numpy as np
from ids_pipeline import make_frame, SAMPLE_HZ


def _seg(rng, kind, n):
    """Return arrays pir, dist, sound of length n for a behaviour kind."""
    pir = np.zeros(n, int); snd = np.zeros(n, int)
    dist = 250 + rng.normal(0, 3, n)
    if kind == "normal":
        pir[rng.random(n) < 0.03] = 1                    # rare PIR false trigger
        snd[rng.random(n) < 0.04] = 1                    # ambient noise blips
        if rng.random() < 0.25:                          # occasional passer-by
            a = rng.integers(0, max(1, n - 6)); pir[a:a + 3] = 1
    elif kind == "intrusion":                            # sustained motion, close, noisy
        pir[:] = (rng.random(n) < 0.85)
        dist = rng.uniform(40, 160, n)
        snd[:] = (rng.random(n) < 0.45)
    elif kind == "loiter":                               # motion + steady close object
        pir[:] = (rng.random(n) < 0.7)
        dist = 90 + rng.normal(0, 4, n)
    elif kind == "noise_only":                           # loud bursts, nothing else
        snd[:] = (rng.random(n) < 0.6)
    elif kind == "tamper":                               # sensor blocked, no PIR
        dist = 8 + rng.normal(0, 1.5, n)
    return pir, np.clip(dist, 2, 400).astype(int), snd


def generate(plan, seed=0, corrupt_rate=0.0):
    """plan = [(kind, n_windows), ...]; returns (frame_lines, labels_per_window)."""
    rng = np.random.default_rng(seed)
    lines, labels, seq = [], [], 0
    for kind, nwin in plan:
        for _ in range(nwin):
            pir, dist, snd = _seg(rng, kind, 20)
            for p, d, s in zip(pir, dist, snd):
                ln = make_frame(seq, int(seq * 1000 / SAMPLE_HZ), int(p), int(d), int(s))
                if rng.random() < corrupt_rate:          # simulate UART bit error
                    i = rng.integers(0, len(ln) - 3)
                    ln = ln[:i] + chr(ord(ln[i]) ^ 0x04) + ln[i + 1:]
                lines.append(ln); seq += 1
            labels.append(kind)
    return lines, labels
