# TODO (ESP32 build). Due Thu 29 Oct 2026.

## Waiting on others
- [ ] Order and receive the sensors (see SHOPPING_LIST.md). Critical path.
- [ ] Agree the Phase C day with the roommate who holds the board. Presentation the day after.

## Done on the PC side
- [x] Phase A and B finished (about 300 frames, 0 rejected)
- [x] ids_live.py: D=0 excluded from distance stats, record clock starts at the first frame, DTR/RTS low on open, boot lines not counted as rejected
- [x] ids_live.py: `check` command, richer `live` output, `evaluate` shows counts, replay files read as UTF-8 or UTF-16, `train` skips short CSVs
- [x] test_ids_live.py (10 checks) replaces the broken PIC-era test scripts
- [x] make_replays.py for rehearsal (simulated only)
- [x] Sound latch fix in esp32_ids.ino, FIRMWARE_GUIDE.md updated to match
- [x] PIC files and old docs archived in archive/pic, CLAUDE.md rewritten for the ESP32 build

## Phase C (needs sensors), see PHASE_C_AND_DEMO.md
- [ ] Link check, sensor bring up, cover test (raw recordings of three cover cases)
- [ ] Recordings: normal_train (600 s), normal_test (300 s), walk, loiter, cover
- [ ] Train and evaluate, fill in the results table (source: hardware)
- [ ] Blocking decision: limitation or a rule on no_echo_ratio, after seeing the cover data

## Before the demo
- [ ] One full dry run of the demo with the board
- [ ] Write my own viva answers (why ML vs threshold, why Isolation Forest, why PC side, where is the embedded part, why windows, how blocking was handled)
