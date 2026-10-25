# Project: Context-aware intrusion detection (ESA course project)

## Situation
- Course: Embedded System Architecture (VIT Vellore, Semester 3). Two-person team.
- Platform: ESP32-S3 dev board (ESP32-S3-N16R8), Arduino framework, real hardware. The earlier PIC16F877A simulation build is dropped and archived in `archive/pic/`. Do not edit or quote it, except to remove stale mentions.
- Teammate owns the firmware (`esp32_ids.ino`, `FIRMWARE_GUIDE.md`). I (Aradhya) own the PC side in Python.
- Deliverable: hardware plus the necessary software shown working. No slides, no report. Due Thu 29 Oct 2026.
- Phases: A (no board) and B (board, no sensors) are done. Phase C (sensors wired, recordings) happens when the sensors arrive, and the demo is the next day.

## System
Sensors: PIR (GPIO 4), digital sound DO (GPIO 5), HC-SR04 ultrasonic (TRIG GPIO 6, ECHO GPIO 7 through a divider).
Pipeline: firmware frames over USB serial at 115200 baud -> parse + checksum -> windows of 20 frames (4 s, non overlapping) -> 10 features -> Isolation Forest (unsupervised, trained on normal behaviour only, `n_estimators=200`, `contamination=0.02`, `random_state=42`) -> score + alert.
Why ML at all: labelled intrusion data is impractical to collect, so unsupervised anomaly detection is used. The ESP32 paper in our literature set (Datta & Majeed 2026) used a hand weighted index instead.
Why the ML is on the PC: the ESP32 does sampling and framing, the PC does the windowing and the model.

## Frame contract
`P:1,D:45,S:0*7D`. `P` PIR level 0 or 1. `D` distance in cm, 1 to 400, 0 means no echo. `S` is 1 if a sound event happened since the previous frame, or the sound pin is still active. Checksum = XOR of every payload character before `*`, two uppercase hex digits. One frame per line, 5 per second. Lines starting with `#` are comments and ignored.
Features (in order): pir_ratio, pir_transitions, sound_ratio, sound_transitions, pir_sound_overlap, dist_mean, dist_std, dist_min, dist_range, no_echo_ratio. Distance stats use D>0 frames only.

## Files
- `ids_live.py`: the PC side. Commands: `check`, `record`, `train`, `evaluate`, `live`. Each of check, record and live reads `--port COMx` or `--replay file.txt`.
- `test_ids_live.py`: checks for the parser and features. Run `python test_ids_live.py`.
- `make_replays.py`: makes SIMULATED frame files in `replays/` to rehearse the pipeline. Never report results from these.
- `esp32_ids.ino`, `FIRMWARE_GUIDE.md`: the firmware and the teammate's guide. Do not edit the guide unless I ask.
- `PHASE_C_AND_DEMO.md`: the checklist for the sensor day and the demo.
- `SHOPPING_LIST.md`: hardware list.
- `archive/`: old versions (`pic/`, `esp32/`). Copy to `archive/` before changing any file, ask before deleting.

## Rules for working with me
- Tight answers, no filler. Tag technical claims [Certain] / [Likely] / [Guessing].
- No dashes or hyphens as clause punctuation in prose.
- For concepts, ask what I think first. For debugging, point at the region before fixing, unless I say "just tell me".
- Be honest about weaknesses. Label every result with its source: simulated, replayed (simulated frames through the file path) or hardware. Never quote replay numbers as hardware results.
- Do not tune thresholds or settings on the test recordings without telling me. Test recordings must be separate sessions from the training recording.
- Do not claim anything the firmware does not do. Honest claims: hardware timer interrupt for the 200 ms period, pin change interrupt for sound, UART frames with XOR checksum at 115200 baud, ultrasonic distance from the echo pulse width. Not claimed: interrupt driven echo capture (`pulseIn` blocks up to 30 ms), RMT, DMA, RTOS, Wi-Fi.
- Viva questions to be ready for: why ML vs a threshold, why Isolation Forest, why PC side, where is the embedded part, why windows, how was blocking handled.

## Open decisions
- Blocking (covered sensor): decide after the real cover test whether to report weak detection as a limitation or add a rule on `no_echo_ratio` beside the model.
