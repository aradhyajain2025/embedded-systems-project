# Project: Context-aware intrusion detection (ESA course project)

## Situation
- Course: Embedded System Architecture (VIT Vellore, Semester 3). Two-person team.
- Presentation and simulation demo: Fri 23 Oct 2026, 8 am. Review 3 due 31 Oct 2026.
- Hardware is DROPPED. Simulation only. Teammate's PIC16F877A firmware (Embedded C, MPLAB X, XC8) runs in a simulator and emits UART frames. I (Aradhya) own the PC side in Python.
- Platform justification: the PIC16F877A has a hardware USART for the UART link, plus a CCP module and interrupt on change that would suit real hardware (echo capture, digital sensors). In this simulation build the firmware uses a Timer2 interrupt for 200 ms sampling, the hardware USART at 9600 baud, and Timer1 as a microsecond counter for echo timing, with the digital sensors polled. CCP and interrupt on change are NOT implemented, do not claim them. ML runs on the PC because the PIC cannot hold the model.

## System
Sensors: PIR (binary motion), ultrasonic (distance, cm), digital sound (binary).
Pipeline: firmware frames over UART -> parse + checksum -> windows -> features -> Isolation Forest (unsupervised, trained on normal behaviour only) -> anomaly score + alert.
Why ML at all: labelled intrusion data is impractical to collect; the ESP32 paper in our literature set avoided ML for that reason, so unsupervised anomaly detection is our answer.

## Files (all in this folder, Python on Windows, run from PowerShell)
- frames.py: checksum() and parse_frame(). Checksum = XOR of every payload character, two uppercase hex digits, frame is `payload*CS`.
- maker.py: make_frame(p, d, s) builds a frame string.
- generator.py: generate_frames(n, mode) with NORMAL and INTRUDER modes (about 5 frames per second).
- roundtrip.py, testparser.py: tests of the frame format.
- ids_pipeline.py: parser, windowing (20 frames), 9 features, Isolation Forest. Written by Claude; it ASSUMED the frame `$S,seq,t_ms,pir,dist_cm,sound*CS`. This must be reconciled with maker.py.
- simulator.py: Claude's own sensor model, to be replaced by generator.py.
- run_demo.py: train on normal, test on mixed stream, metrics, plot. Last result: false alarms 1.5%, intrusion 100%, loiter 100%, tamper 83%, noise only 50%.

## Known issues
- generator.py bug: the d_glitch_chance branch sets d = 0, then the next frame random walks from 0 and clamps to 2, so distance never returns to 250. Fix by using a separate output variable for the glitch.
- Real frames have no seq or timestamp (assumed), so windows are built by counting 20 valid frames.

## Rules for working with me
- Tight answers, no filler. Tag technical claims [Certain] / [Likely] / [Guessing].
- No dashes or hyphens as clause punctuation in prose.
- For concepts, ask what I think first. For debugging, point at the region before fixing, unless I say "just tell me".
- Be honest about weaknesses: results come from simulated data, so they validate the pipeline, not real world accuracy. Never overclaim.
- Viva questions to be ready for: why ML vs a threshold, why Isolation Forest, why PC side, why simulated data, where is the embedded part.


