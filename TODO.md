# TODO (living list, Claude updates this as work happens)

Last updated: Thu 22 Oct 2026
Deadlines: demo **Fri 23 Oct, 8 am**. Review 3 due **Sat 31 Oct**.

Legend: `[x]` done, `[ ]` open, `[~]` in progress, `[?]` waiting on someone. Tick boxes yourself any time, tell me and I will sync the rest.

## Waiting on others
- [?] Teammate: final fake_sensors.c that built, plus a clean screenshot or screen recording of the MPLAB UART 1 Output window running
- [?] Teammate: sample period of the firmware timer (we assume 5 frames per second, so 20 frames = 4 s)

## Before the demo (priority order)
- [ ] Open anomaly_scores.png and check it reads clearly (labels, threshold line, colours)
- [ ] Write the demo runbook: exact commands in the order you will run them, one screen each
  - `python run_demo.py` (metrics + plot, takes a few seconds)
  - `python live_serial.py frames_log.txt` (firmware frames through the model)
  - fallback if MPLAB fails: `python live_serial.py sim` plus the saved screenshot
- [ ] Dry run of the whole demo on your laptop, timed
- [ ] Viva prep: answer the five questions in your own words first, then I will tighten them
  - why ML vs a threshold
  - why Isolation Forest
  - why the ML is on the PC side
  - why simulated data
  - where is the embedded part
- [ ] Decide what you say about limits (see "Say these yourself" below)
- [ ] Slides: confirm what exists and what is missing

## Say these yourself in the presentation
- All data is simulated and scripted. Results validate the pipeline, not real-world accuracy.
- The model trains on the same generator that makes the test data, so a clean result is partly circular.
- Sensor values come from a hardcoded table in the firmware. Real sensor read functions exist behind `USE_FAKE_SENSORS` but were not exercised.
- Blocking (covered ultrasonic sensor) is defined as D=0 on 90% of frames. A one-line rule on no_echo_ratio would probably do as well. The model's value is the intruder class.
- Quote the 20-seed numbers (intruder about 85%, blocking about 91%, false alarms about 1.3%), not the single seed 7 run.

## After the demo, for Review 3
- [ ] Add the 20-seed results table and the plot to the report
- [ ] Write the limitations section from the list above
- [ ] Optional: try widening the training glitch rates to lift blocking detection, re-run 20 seeds, report honestly either way
- [ ] Optional: make live_serial.py follow a growing file, for a live feel
- [ ] Optional: virtual COM port (needs a file bridge, and UART file output did not work)

## Housekeeping
- [ ] Delete simulator.py (replaced by generator.py, nothing imports it now)
- [ ] Add .gitignore for __pycache__
- [ ] roundtrip.py and testparser.py: check they still pass after the maker.py import guard
- [ ] Confirm the frame format wording in CLAUDE.md still matches (it still lists ids_pipeline as assuming `$S`)

## Done
- [x] Fix generator.py glitch bug (separate output variable) and NORMAL distance drift
- [x] Reconcile ids_pipeline.py with frames.py (real `P:x,D:y,S:z*CS` format)
- [x] D=0 treated as no echo: distance features ignore it, new no_echo_ratio feature (10 features)
- [x] BLOCKING mode in generator.py (kept as the third class)
- [x] Rebuild run_demo.py: NORMAL, INTRUDER, BLOCKING, 2% UART corruption, 20-seed summary
- [x] live_serial.py: sources are COM port, log file, or `sim`; seeded training so runs repeat
- [x] export_c_array.py and fake_sensors_generated.c (400 frame table for the firmware)
- [x] Teammate's log (frames_log.txt): 516 lines, 0 rejected, intruder windows alert
- [x] maker.py self-test only runs when run directly
