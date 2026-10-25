*HOW TO WORK (read first)*

This add-on is for understanding the job and agreeing a plan. It is not an instruction to start editing.

Understand. Read CLAUDE.md, this file, and every Python file in the folder. Also read esp32_ids.ino, ids_live.py and FIRMWARE_GUIDE.md if they are present. Make no edits in this phase.
Ask. Put the refinement questions below to me, grouped, a few at a time. Use the question tool if you have one. Do not guess answers. If an answer changes the plan, say how.
Plan. Write a step by step plan: each step, the files it touches, the check that proves it worked, and the risks. Wait for my approval or edits.
Execute. One step at a time. After each step run its check, show me the result in a few lines, and stop if something unexpected happens.
Safety. Copy any file into an archive/ folder before changing it. Ask before deleting anything. Never overwrite or "refresh" any result number without telling me.
What changed
The platform is now an ESP32-S3 dev board (ESP32-S3-N16R8 module) using the Arduino framework. Real hardware is back. The earlier lines "Hardware is DROPPED. Simulation only", the PIC16F877A firmware lines and the PIC platform justification are obsolete.
The firmware is owned by my teammate. I own the PC side in Python.
The PIC firmware is dropped. Do not edit or reference it except to remove stale mentions.
Interface contract (verify against the real files, do not trust blindly)
Item	Value
Frame	P:1,D:45,S:0*7D
Checksum	XOR of every payload character, two uppercase hex digits
D	cm, 1 to 400. 0 means no echo
S	1 if any sound event since the previous frame
Rate	5 frames per second (200 ms)
Baud	115200
Comment lines	start with #, ignored by the parser
Window	20 valid frames (4 s), non overlapping
Features (10)	pir_ratio, pir_transitions, sound_ratio, sound_transitions, pir_sound_overlap, dist_mean, dist_std, dist_min, dist_range, no_echo_ratio
Model	Isolation Forest. ids_live.py uses n_estimators=200, contamination=0.02, random_state=42

Pins on the board: PIR GPIO 4, sound DO GPIO 5, HC-SR04 TRIG GPIO 6, ECHO GPIO 7 through a divider.

Files provided by the chat session (treat as unverified)
esp32_ids.ino: firmware. Syntax checked against stub headers only. Never run on hardware.
ids_live.py: modes record, train, evaluate, live. Self contained, so it has its own parser and 10 feature definition. It was tested only on synthetic replay files. It may differ from the existing ids_pipeline.py.
FIRMWARE_GUIDE.md: the teammate's guide. Do not edit it unless I ask.
Candidate goals (to be refined with me, not decided)
G1 One frame format and one parser shared by simulator, replay and serial.
G2 One definition of the 10 features. Reconcile ids_pipeline.py (older 9 feature version) with ids_live.py.
G3 Update generator.py to the hardware semantics. Fix the d glitch bug. Add a BLOCKED mode whose behaviour matches what the real sensor does when covered (that value comes from my hardware test).
G4 One pipeline, two sources: a replay file for simulation and a serial port for hardware.
G5 Calibrate the NORMAL profile in the simulator from a real normal recording.
G6 Evaluation: keep the existing 20 seed simulated benchmark, and add separately labelled hardware trials with per class rates.
G7 Blocking on hardware: decide between reporting weak detection as a limitation and adding a rule based tamper check alongside the model. Decide only after seeing real data.
G8 Update run_demo.py, the plots and the test files.
G9 List every place that still says PIC, MPLAB, Timer2, USART, CCP or 9600 baud (CLAUDE.md, code comments, slides, report) and propose replacements.
Refinement questions to ask me before planning

Current state

Which ids_pipeline.py is current, and does it already have the 10 features? Is it the one that produced the 84.5%, 1.3% and 91.0% figures?
Do I want the old PIC era results kept as an archived simulated benchmark, or replaced?
Is simulator.py still used anywhere?

Hardware and data 4. Which parts do I actually have now? Is the HC-SR04 wired yet? 5. How will I record data: where, how long, and who moves in front of the sensors? 6. Can I record separate sessions for training and testing? (Test data must not come from the training recording.)

Blocking 7. What does the real sensor report when covered? If unknown, plan a test for it first. 8. If the model cannot detect blocking on real data, which do I prefer: report it as a limitation, or add a rule alongside the model?

Scope and time 9. What exactly must be shown at Review 3 on 31 Oct (live hardware demo, report, slides)? What is the priority order if time runs short? 10. Who runs which scripts, and on which machine (Windows, PowerShell)? 11. Which slides and report sections do I want updated by you, and which will I edit myself?

Constraints
Follow every rule in CLAUDE.md, especially the honesty rules.
Label every result with its source: simulated, replayed (simulated frames through the file path) or hardware.
Do not tune thresholds or settings on the test recordings without telling me.
Do not claim anything the firmware does not do. The firmware guide lists what is honest to claim.
Do not state the known figures from older runs as hardware results.
Checks that mean "done"
testparser.py and roundtrip.py pass with the final frame format.
A replay file and a serial recording of the same frames give identical features.
300 real frames from the board parse with 0 rejected.
run_demo.py still runs for the simulated benchmark and reports false alarms, intruder detection and blocking detection.
Each hardware trial class has its own row in the results (normal, walking in, loitering, covered).
No remaining stale references from G9, or each one is listed for me to decide.