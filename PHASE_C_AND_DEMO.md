# Phase C (sensor day) and demo

Replace `COM5` with the real port everywhere. All commands run from this folder in PowerShell.
Every number from this day is a **hardware** result. Nothing from `replays/` is ever reported.

## Before the sensor day (laptop that holds the board)
- [ ] `pip install pyserial numpy scikit-learn joblib`
- [ ] `python test_ids_live.py` prints `10 of 10 passed`
- [ ] Rehearsal works: `python make_replays.py`, then run the commands it prints (record, train, evaluate on `replays/`)
- [ ] Latest `esp32_ids.ino` is on the teammate's laptop and compiles
- [ ] Port name noted from Phase B, with the Arduino IDE settings that worked

## Phase C, in this order (plan 2 to 3 hours)

### 1. Link check (10 min, before any wiring)
Re-upload `esp32_ids.ino`, close the Serial Monitor (only one program can hold the port), then:
```
python ids_live.py check --port COM5
```
Expect about 300 frames, 0 rejected. If it fails, stop and fix this first.

### 2. Bring up the sensors one at a time (30 to 45 min)
Follow section 10 of `FIRMWARE_GUIDE.md`. After each sensor run `python ids_live.py check --port COM5 --seconds 20` and look at the line for that sensor. Do not record training data until all three behave.

### 3. Cover test (10 min)
Record each case, so the real `D` values are on file:
```
python ids_live.py record --port COM5 --label cover_hand --seconds 40 --out cover_hand.csv
python ids_live.py record --port COM5 --label cover_card --seconds 40 --out cover_card.csv
python ids_live.py record --port COM5 --label cover_tape --seconds 40 --out cover_tape.csv
```
Hand 1 cm in front, a card 5 cm in front, tape or cloth over both transducers. Write down what `D` shows (0, a small constant, or jumping). **This decides how blocking is handled.**

### 4. Recordings (about 25 min of recording)
Same room, same sensor position for every session. Keep the sensors still between sessions.

| Order | File | Label | Seconds | What happens |
|---|---|---|---|---|
| 1 | `normal_train.csv` | normal | 600 | Room as it normally is. Normal life only, nobody trying to look like an intruder. |
| 2 | `normal_test.csv` | normal | 300 | A **separate** session of the same normal conditions. |
| 3 | `walk.csv` | walk | 180 | Someone walks in, moves around, walks out, a few times. |
| 4 | `loiter.csv` | loiter | 180 | Someone stays in front of the sensors, fidgets, stays close. |
| 5 | `cover.csv` | cover | 120 | Sensor covered in the way the cover test showed (use the case you will demo). |

Example:
```
python ids_live.py record --port COM5 --label normal --seconds 600 --out normal_train.csv
```
Rules:
- Train only on `normal_train.csv`. Do not tune anything on the test files.
- A 4 s window is one decision, so 180 s is only about 9 windows. Report counts, such as "7 of 9", not just percentages.

### 5. Train and evaluate (5 min)
```
python ids_live.py train normal_train.csv --model model.joblib
python ids_live.py evaluate --model model.joblib normal_test.csv walk.csv loiter.csv cover.csv
```
Copy the table into the results below.

### 6. Blocking decision
Look at the cover row. If detection is weak, either report it as a limitation, or tell me to add a rule on `no_echo_ratio` beside the model. Do not change the model settings to fix it.

## Results to fill in (source: hardware)

| Class | Windows | Flagged | Rate |
|---|---|---|---|
| normal (test, false alarms) | | | |
| walk | | | |
| loiter | | | |
| cover | | | |

Setup to write next to it: room, sensor position, who moved, date, 10 minutes of training.

## The demo (about 5 minutes)
1. Say in one breath: ESP32 samples three sensors every 200 ms and sends a checksummed text frame over USB. The PC groups 20 frames into a 4 s window, computes 10 features and scores it with an Isolation Forest trained on normal behaviour only.
2. Run `python ids_live.py check --port COM5 --seconds 20` to show the link: frame rate, rejected frames, the sensor values.
3. Run `python ids_live.py live --port COM5 --model model.joblib`. Each line shows the window number, score, `ok` or `ALERT`, and the PIR, sound, distance and no-echo values, so the audience sees why it alerts.
   - Stay still for two or three windows: expect `ok`.
   - Walk in front: expect `ALERT` on some windows.
   - Cover the HC-SR04: show what happens, whatever it is.
4. Run `python ids_live.py evaluate` on the recorded files and show the table above.
5. Say the limits yourself: one room, one session, few windows per class, scripted behaviour by us, no real intruders. Results show the pipeline works on this setup, not real world accuracy.

### If something fails on the day
| Problem | Do this |
|---|---|
| Live window does not appear | Close the Serial Monitor and Arduino plotter, check the port name, unplug and replug |
| Sensor misbehaves | Show `check.csv` and the recorded CSVs with `evaluate`, and say live mode did not work today |
| No frames at all | Re-upload the sketch, check the USB CDC On Boot setting against the port you used (section 5 of the firmware guide) |
| `live` starts but nothing prints | A window needs 20 valid frames (4 s). If it stays empty, run `check` |

## Honest claims (what the firmware does)
Hardware timer interrupt for the 200 ms period. Pin change interrupt for sound, plus the pin level at frame time. UART frames with an XOR checksum at 115200 baud. Ultrasonic distance from the echo pulse width, with `pulseIn` blocking up to 30 ms.
Do not claim interrupt driven echo capture, RMT, DMA, an RTOS, Wi-Fi, or anything about sensor behaviour you have not measured.
