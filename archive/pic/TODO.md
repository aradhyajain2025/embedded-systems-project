# TODO (living list, Claude updates this as work happens)

Last updated: Fri 23 Oct 2026, 00:35
Deadlines: demo **today, Fri 23 Oct, 8 am**. Review 3 due **Sat 31 Oct**.

Legend: `[x]` done, `[ ]` open, `[~]` in progress, `[?]` waiting on someone. Tick boxes yourself any time, tell me and I will sync the rest.

## Waiting on others
- [?] Teammate: a clean screenshot or screen recording of the MPLAB UART 1 Output window running
- [x] Platform justification reworded in CLAUDE.md to match the firmware (no CCP or interrupt on change claimed). Use the same wording on the slides.

## Firmware facts (read from main.c, frame.c, sensors.c)
- Timer2 interrupt every 1 ms (PR2=249, 1:4 prescaler, 4 MHz), `sample_due` set every 200 ms, so 5 frames per second. 20 frames = 4 s.
- Hardware USART, 9600 baud (SPBRG=25, BRGH=1, about 0.16% error). TRISC6 and TRISC7 set to 1 is correct for the PIC16F877A USART.
- `frame_build` writes `P:x,D:y,S:z*CS\n`, XOR over the payload before `*`, uppercase hex. Clamps D>400 to 0 and D=1 to 2 so it always matches the PC parser.
- Real sensor path (not run in simulation): PIR and sound are polled on RB0 and RB1. Ultrasonic uses Timer1 as a 1 us counter, busy-waiting on the echo pin, cm = microseconds / 58, and returns 0 on timeout or if the echo is under 116 us (closer than 2 cm).
- NOT used: CCP capture, interrupt on change. Do not claim them in the viva unless the code changes.
- fake_sensors.c is identical to fake_sensors_generated.c (unchanged paste).

## Before the demo (priority order)
- [ ] Open anomaly_scores.png and check it reads clearly (labels, threshold line, colours)
- [x] Demo runbook written: see RUNBOOK.md
- [ ] Dry run of the whole demo on your laptop, timed, twice (second run is the real time)
- [ ] Test the live copy once (`Get-Clipboard | python live_serial.py -` after Ctrl+A, Ctrl+C in the UART window), time how long 300 frames take, then test the fallback `python live_serial.py frames_log.txt`
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
- [x] live_serial.py: sources are COM port, log file, or `-` (stdin, for a clipboard copy from MPLAB); the `sim` mode was removed so scored frames always come from the firmware; seeded training so runs repeat
- [x] export_c_array.py and fake_sensors_generated.c (400 frame table for the firmware)
- [x] Teammate's log (frames_log.txt): 516 lines, 0 rejected, intruder windows alert
- [x] maker.py self-test only runs when run directly
- [x] Firmware source received and read (main.c, frame.c, frame.h, sensors.c, sensors.h, fake_sensors.c, fake_sensors.h); sample rate 5 per second confirmed from the timer setup
