# Presentation plan (Fri 23 Oct 2026, 8 am)

Built from RUNBOOK.md and TODO.md. Total about 7 minutes of showing, plus Q&A.

## Roles
- **Teammate:** the embedded half. MPLAB, the firmware, the UART frames and the hardware limits.
- **Aradhya:** the PC half. Parser, features, Isolation Forest, results and limits.
- **Handoff point:** the UART frame. The teammate's side ends at `P:1,D:15,S:1*79` and Aradhya's starts there.

## Plan

| # | Who | Time | What happens |
|---|---|---|---|
| 0 | Both | before walk in | Run the checklist below |
| 1 | Aradhya | 30 s | System in one breath: sensors, PIC, UART frame with XOR checksum, parse, window, features, Isolation Forest trained on normal only |
| 2 | Teammate | 1.5 min | Show the MPLAB UART 1 Output window, or the screenshot. Point at one frame: payload, `*`, two hex checksum digits. Say what the firmware does: Timer2 interrupt gives 5 frames per second, hardware USART at 9600 baud, Timer1 times the echo |
| 3 | Teammate | included in #2 | Say sensor values come from a hardcoded table, and the real read functions sit behind `USE_FAKE_SENSORS` and were not run |
| 4 | Both | 1 min | Teammate has had the firmware running since step 1 and copies the UART 1 Output window (Ctrl+A, Ctrl+C). Aradhya runs `Get-Clipboard \| python live_serial.py -`. Say "frames just produced by the firmware simulator, 0 rejected, so firmware and parser agree". Say it is copy then score, not live streaming. Point out misses and false alarms yourself (in the saved log: window 15 missed, window 3 false alarm) |
| 5 | Aradhya | 2 min | Run `python run_demo.py`. Quote only the 20-seed table (false alarms 1.3%, intruder 84.5%, blocking 91.0%), then show anomaly_scores.png |
| 6 | Aradhya | 1 min | Limits, said first by you. Data is simulated, results validate the pipeline not real-world accuracy. Model trains on its own generator, so results are partly circular. Blocking is a trivial rule |
| 7 | Teammate | 30 s | Close from the hardware side. What would change on real sensors: use the real read functions. CCP capture and interrupt on change would suit echo timing but are NOT implemented |
| 8 | Aradhya | 15 s | Next step: real sensor data to set the threshold |

## Q&A split
- **Teammate answers:** where is the embedded part, why those peripherals, how the checksum is built, what the fake table is, what `USE_FAKE_SENSORS` does.
- **Aradhya answers:** why ML vs a threshold, why Isolation Forest, why the ML is on the PC, why simulated data, any question about a number.
- **Rule for both:** if you do not know, say so. Never claim CCP or interrupt on change.

## Checklist before walk in
- [ ] Teammate sends the clean UART screenshot or recording (only open item from them)
- [ ] Aradhya runs `python run_demo.py` once so the plot is fresh and packages are warm
- [ ] Open anomaly_scores.png and check labels, threshold line, colours
- [ ] One timed dry run together, then a second as the real time
- [ ] Teammate starts the firmware at the start of step 1. Time how long until about 300 frames are in the UART window, in the dry run
- [ ] Test the live copy once: Ctrl+A, Ctrl+C in the UART window, then `Get-Clipboard | python live_serial.py -`
- [ ] Test the fallback once: `python live_serial.py frames_log.txt`
- [ ] Agree who types commands (suggest Aradhya, so the teammate can talk)
- [ ] Laptop charged, notifications off
- [ ] Confirm what the slides cover (still open in TODO.md)
- [ ] Each writes their own viva answers (Aradhya: ML and simulation questions, teammate: embedded questions)

## Notes
- CLAUDE.md is stale (says 9 features, "must be reconciled", old results). Do not read from it on stage. Use RUNBOOK.md.
- Only steps 2, 3 and 7 depend on the teammate. If MPLAB fails, the screenshot covers them.
- If something breaks on the PC side, see the table in RUNBOOK.md.
