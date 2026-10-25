
from maker import make_frame
import frames

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
bad_inputs = [(2, 45, 0), (1, 45, 2), (1, 1, 0), (1, 401, 0), (1, -5, 0)]
for args in bad_inputs:
    try:
        make_frame(*args)
        print("NOT REJECTED:", args)
    except ValueError:
        pass