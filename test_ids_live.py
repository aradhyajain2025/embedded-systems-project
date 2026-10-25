"""Checks for ids_live.py. Run: python test_ids_live.py   (also works with pytest)."""
import ids_live as L


def frame(p, d, s):
    payload = f"P:{p},D:{d},S:{s}"
    return f"{payload}*{L.checksum(payload)}"


def test_checksum_example():
    assert L.checksum("P:1,D:45,S:0") == "7D"
    assert L.parse_frame("P:1,D:45,S:0*7D") == (1, 45, 0)


def test_roundtrip_all_values():
    for p in (0, 1):
        for s in (0, 1):
            for d in range(0, 401):
                assert L.parse_frame(frame(p, d, s)) == (p, d, s)


def test_rejects_bad_frames():
    bad = ["P:1,D:45,S:0*7E",          # wrong checksum
           "P:2,D:45,S:0", "P:1,D:401,S:0", "P:1,D:-5,S:0", "P:1,D:45,S:2",
           "P:1,D:45", "P:1,D:45,S:0*7", "P:1,D:45,S:0*7D*7D", "garbage", "", "   "]
    for line in bad:
        assert L.parse_frame(line) is None, line
    for d in (401, -5):
        payload = f"P:1,D:{d},S:0"
        assert L.parse_frame(f"{payload}*{L.checksum(payload)}") is None


def test_corrupted_character_is_caught():
    good = frame(1, 45, 0)
    for i in range(good.index("*")):
        changed = good[:i] + ("9" if good[i] != "9" else "8") + good[i + 1:]
        assert L.parse_frame(changed) is None, changed


def test_comments_and_line_endings():
    assert L.parse_frame("# warming up sensors") is None
    assert L.parse_frame("P:1,D:45,S:0*7D\r\n") == (1, 45, 0)
    assert L.parse_frame("  P:1,D:45,S:0*7d  ") == (1, 45, 0)     # lower case hex is accepted


def test_feature_count_and_order():
    f = L.window_features([(0, 250, 0)] * 20)
    assert len(f) == len(L.FEATURES) == 10
    assert L.FEATURES[5] == "dist_mean" and L.FEATURES[9] == "no_echo_ratio"


def test_no_echo_frame_does_not_distort_distance_stats():
    clean = L.window_features([(0, 250, 0)] * 20)
    one_glitch = L.window_features([(0, 250, 0)] * 9 + [(0, 0, 0)] + [(0, 250, 0)] * 10)
    assert one_glitch[5:9] == clean[5:9]
    assert abs(one_glitch[9] - 0.05) < 1e-9


def test_fully_covered_window():
    f = L.window_features([(0, 0, 0)] * 20)
    assert f[5:9] == [0.0, 0.0, 0.0, 0.0] and f[9] == 1.0


def test_pir_and_sound_features():
    w = [(1, 100, 1)] * 10 + [(0, 100, 0)] * 10
    f = L.window_features(w)
    assert f[0] == 0.5 and f[1] == 1 and f[2] == 0.5 and f[3] == 1 and f[4] == 0.5


def test_windows_do_not_overlap_and_drop_the_remainder():
    assert len(L.make_windows([(0, 250, 0)] * 59)) == 2
    assert len(L.make_windows([(0, 250, 0)] * 19)) == 0


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print("ok   ", name)
        except AssertionError as e:
            failed += 1
            print("FAIL ", name, e)
    print(f"{len(tests) - failed} of {len(tests)} passed")
    raise SystemExit(1 if failed else 0)
