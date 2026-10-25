# Demo runbook (Fri 23 Oct 2026, 8 am)

Total about 7 minutes of showing. Commands take about 9 s and 3 s on the dev laptop, so most of the time is talking.

## Before you walk in
- [ ] PowerShell open in `d:\embedded_project`, font size large (Ctrl + scroll)
- [ ] `python run_demo.py` run once, so anomaly_scores.png is fresh and the packages load fast
- [ ] anomaly_scores.png open in an image viewer, ready to switch to
- [ ] MPLAB X project open with the UART 1 Output tab, **firmware started at the beginning of step 1** so about 300 frames (60 s) are in the window by step 3. Time how long this takes in the dry run
- [ ] frames_log.txt exists in the folder (516 lines), this is the fallback if the live copy fails
- [ ] Laptop charged and plugged in, notifications off

## Steps

### 1. The system in one breath (30 s)
Say: "PIR, ultrasonic and sound go into a PIC16F877A. The firmware frames each reading and sends it over UART with an XOR checksum. On the PC we parse, window, extract features and score with an Isolation Forest trained on normal behaviour only."

### 2. Embedded part: the firmware frames (1 min)
Show: MPLAB X UART 1 Output window (frames scrolling) or the screenshot.
Point at: `P:1,D:15,S:1*79`. Payload, then `*`, then two hex digits of checksum.
Say: "Sensor values come from a table in the firmware because we have no hardware. The `USE_FAKE_SENSORS` switch swaps in the real read functions, which we did not run in simulation."

### 3. Interface proof, live firmware data (1 min)
In MPLAB X: click in the UART 1 Output window, Ctrl+A, Ctrl+C. Then in PowerShell:
```
Get-Clipboard | python live_serial.py -
```
Fallback with the saved log (same 516 frames from an earlier firmware run):
```
python live_serial.py frames_log.txt
```
Expect: `Trained on 3000 normal frames -> 150 windows`, then one line per 20 frames with score and ok or ALERT, then a `Done:` line.
Say: "These frames were just produced by the firmware in the simulator, copied from its UART window. Zero rejected by the checksum, so the firmware and the PC parser agree."
Say: "The firmware replays a 400 frame table, so the data is scripted, but every frame goes through the real framing, checksum and UART code."
Pattern for the saved log, windows counted from 1 as printed (`.` ok, `A` alert):
```
. . A . . . . . . . A A A A . . . . . . . . A . .
```
- Windows 11 to 14 alert: the intruder segment.
- Window 15 is missed. Say so. Do not hide it.
- Window 3 (and 23, the repeat) is a false alarm: a harmless 3-frame PIR burst.
- The model is trained with a fixed seed, so a live copy that starts from firmware reset (table frame 0) should show the same pattern for as many windows as you copied. [Likely] Check this in the dry run.
- Do not claim live streaming. It is copy then score.

### 4. Detection results (2 min)
Run:
```
python run_demo.py
```
This is the controlled test: the stream comes from generator.py so it has ground truth labels, which the firmware log does not. Takes about 9 s. Expect, in this order:
- `Test stream: 3080 frames sent, 62 rejected by checksum (2.0%)`
- seed 7 per-class table (100% and 100% with 0.8% false alarms). **Do not quote this one as the result. It is one lucky draw.**
- the 20-seed table. **Quote this:**

| Class | 20-seed mean | Range |
|---|---|---|
| normal flagged (false alarm) | 1.3% | 0 to 5% |
| intruder detected | 84.5% | 56 to 100% |
| blocking detected | 91.0% | 70 to 100% |

Then show anomaly_scores.png. Say: "Blue line is the model's score per window. Dashed line is the threshold. Coloured bands are ground truth from the generator. The model never saw labels."

### 5. Limits, said by you first (1 min)
- All data is simulated and scripted. This validates the pipeline, not real-world accuracy.
- The model trains on the same generator that makes the test data, so results are partly circular.
- Blocking is defined as D=0 on 90% of frames. A one-line rule would probably do as well. The model's value is the intruder class, where weak signals combine.
- The false alarm rate is partly set by the threshold choice (`contamination=0.02`).

### 6. Close (30 s)
Say: "Next step would be real sensor data to set the threshold and check the false alarm rate."

## If something breaks

| Problem | Do this |
|---|---|
| MPLAB X will not open or crashes | Use the screenshot of the UART window and run `python live_serial.py frames_log.txt`. Steps 4 to 6 do not need MPLAB. |
| Live copy gives too few windows or odd results | Run `python live_serial.py frames_log.txt` and say the log is from an earlier firmware run |
| `frames_log.txt` missing | Re-copy from MPLAB into a file: `Get-Clipboard | Set-Content -Encoding utf8 frames_log.txt`, then run it. If MPLAB is also down, skip to step 4 and show the screenshot |
| `ModuleNotFoundError: sklearn` or `serial` | `python -m pip install scikit-learn numpy matplotlib pyserial` |
| Plot does not open | `start anomaly_scores.png` in PowerShell |
| `run_demo.py` slow or crashes | Show the saved anomaly_scores.png and read the table from this file |
| Examiner asks for a live COM port | Say: virtual COM needs a file bridge and the simulator UART could not be saved to a file, so we replayed the captured log. The parser path is identical. |

## Likely questions
- Why ML vs a threshold? Why Isolation Forest? Why on the PC? Why simulated data? Where is the embedded part? Answers to be written in your own words (see TODO.md).
- "Your model flagged a normal window." Yes, window 3. A short PIR burst in a 4 s window looks unusual, and about 1 to 2% of normal windows alert by design.
- "Why is blocking only 91%?" Isolation Forest cannot tell how far a value is outside what it trained on. Trained glitch rate was about 1%, so 90% no-echo does not stand out as much as it should.
