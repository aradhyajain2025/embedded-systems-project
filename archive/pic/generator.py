from maker import make_frame
import random

NORMAL = {
    "p_burst_chance": 0.01,   # per frame, brief motion starts
    "p_burst_len": (3, 10),   # frames the P=1 run lasts (0.6 to 2 s)
    "s_blip_chance": 0.01,    # per frame, sound blip
    "d_base": 250,            # empty room distance in cm
    "d_jitter": 3,            # random noise in cm
    "d_glitch_chance": 0.01,  # occasional D=0 (no echo)
}
INTRUDER = {
    "p_burst_chance": 0.15,   # motion starts often
    "p_burst_len": (10, 40),  # runs of 2 to 8 s
    "s_blip_chance": 0.08,
    "d_walk_step": 10,        # D drifts like a random walk
    "d_glitch_chance": 0.01,
}
BLOCKING = {
    "p_burst_chance": 0.01,   # room is quiet, same as NORMAL
    "p_burst_len": (3, 10),
    "s_blip_chance": 0.01,
    "d_base": 250,
    "d_jitter": 3,
    "d_glitch_chance": 0.9,   # ultrasonic sensor covered: D=0 (no echo) on most frames
}
def generate_frames(n, mode=NORMAL):
    p_burst_len = 0
    d = mode.get("d_base", 250)
    for i in range(n):
        if p_burst_len > 0:
            p = 1
            p_burst_len -= 1
        else:
            p = 1 if random.random() < mode.get("p_burst_chance", 0.01) else 0
            if p:
                p_burst_len = random.randint(*mode.get("p_burst_len", (3, 10))) - 1
        s = 1 if random.random() < mode.get("s_blip_chance", 0.01) else 0
        if "d_walk_step" in mode:
            d += random.randint(-mode["d_walk_step"], mode["d_walk_step"])
        else:
            # empty room: jitter around the base, no accumulation
            d = mode.get("d_base", 250) + random.randint(-mode.get("d_jitter", 3), mode.get("d_jitter", 3))
        d = max(2, min(400, d))
        # glitch only affects the transmitted value, true distance d carries on
        d_out = 0 if random.random() < mode.get("d_glitch_chance", 0.01) else d
        yield make_frame(p, d_out, s)