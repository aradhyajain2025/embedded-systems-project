# PPT content: Research Gap, Contribution, Results, Limitations, Future Work

Two sections for the slides. Each has slide-ready bullets (short, paste into the slide) and speaker notes (what to say, with the detail behind the bullet).

Numbers come from `run_demo.py` (20-seed run) and `frames_log.txt`. Paper descriptions come from abstracts and repository pages, not full texts. See "Check before you present" at the bottom.

---

# Section 1: Research Gap and Our Contribution

## Slide 1a: What the literature does (table for the slide)

| # | Paper | What it does | Where it stops, relative to our goal |
|---|---|---|---|
| 1 | Sahoo & Pati, 2017 (RTEICT) | PIR based intrusion alert with GSM and ESP8266 (IoT alerting) | One motion trigger means one alarm. No model of what "normal" looks like |
| 2 | Lau et al., 2018 (IEEE IoT J.) | Fuses PIR with an analog sound sensor, calibrates PIR to cut false alarms from weather and environment | Aimed at measuring space usage in a smart city, not detecting intrusion |
| 3 | Sajana et al., 2009 (ISSNIP) | Low complexity PIR network algorithm: Haar transform features plus an SVM to separate humans from wind blown vegetation | Supervised, needs labelled data. PIR only |
| 4 | Gaddipati et al., 2021 (Springer) | Arduino, PIR and Wi-Fi camera. HOG and Haar cascade features plus an SVM cut false alarms from animals, then alert the phone | Camera based and supervised. Heavier compute, privacy cost, needs labelled images |
| 5 | Liu, Ting & Zhou, 2008 (ICDM) | Isolation Forest: isolates anomalies by random partitioning | A general algorithm, not a security system. This is the model we use |
| 6 | Pathak et al., 2021 (IEEE ICC) | Isolation Forest and a decision tree to detect sensor tampering in an office IoT system | Works on network traffic patterns, not on the physical sensor readings. Targets tampering, not intrusion |
| 7 | Datta & Majeed, 2026 (IJSAT) | ESP32, four PIR plus a vibration sensor. Learns a 60 s baseline at start up, computes a weighted Disturbance Index, classes: normal, suspicious, confirmed intrusion. Telegram alert | Closest to us. Hand weighted index and thresholds, no learned model. Not benchmarked against ours |

## Slide 1b: The gap (3 bullets)
- Simple PIR systems (1) raise an alarm on any motion trigger, so harmless activity causes false alarms.
- Systems that cut false alarms with ML (3, 4) are supervised, so they need labelled intrusion data that is impractical to collect.
- Isolation Forest has been used for tampering on network traffic (6), but within our papers we found none that applies unsupervised anomaly detection to windows of PIR, ultrasonic and sound readings, trained on normal behaviour only.

Say "within our seven papers", not "nobody has done this".

## Slide 1c: Our contribution (4 to 5 bullets)
- **Unsupervised, normal only training:** Isolation Forest learns normal behaviour and flags what deviates. No labelled intrusion data needed.
- **Three sensors, one decision:** 20 frame windows (4 s at 5 frames per second) give 10 features across PIR, ultrasonic and sound, including `no_echo_ratio` for a covered ultrasonic sensor.
- **A tamper class at sensor level:** blocking the ultrasonic sensor is detected from its readings (paper 6 detects tampering from network traffic).
- **Whole chain built and connected:** PIC16F877A firmware (Timer2 interrupt, hardware USART at 9600 baud, XOR checksum framing) into a PC parser that rejects corrupt frames, then windows, features, Isolation Forest, alert.
- **Honest evaluation:** 20 seeds, per class rates and ranges, plus firmware frames passing through the real parser.

## Speaker notes for Section 1
- Open with the problem: a PIR sensor says "motion", not "intruder". Cats, fans and heat all trigger it.
- Papers 3 and 4 fix that with supervised ML. Good accuracy, but they need labelled intrusions, and nobody has a pile of labelled break ins. That is why we use unsupervised detection. This also matches our literature set: the ESP32 paper (7) avoided ML for exactly this reason and used a hand weighted index instead. [Likely that this is paper 7, check the paper]
- Be direct that paper 7 is the closest work. Its idea of learning a baseline is the same idea as ours. The difference is that we learn the baseline with a model over many window features instead of a hand tuned weighted index. We did not run a head to head comparison.
- Why ML on the PC: the PIC16F877A cannot hold the model. The PIC does what it is good at: sampling on a timer, framing and sending.
- Why Isolation Forest (Liu et al.): it needs only normal data, it is fast and light because it uses random splits and no distance or density calculations, and anomalies get isolated in few splits. It is also easy to explain: "odd points are easy to isolate".

---

# Section 2: Current Results, Limitations and Future Work

## Slide 2a: Current results (table for the slide)

**Pipeline test on simulated data, 20 train and test seeds, rates per 4 s window:**

| Class | Mean | Range over seeds |
|---|---|---|
| Normal flagged (false alarm) | 1.3% | 0 to 5% |
| Intruder detected | 84.5% | 56 to 100% |
| Blocking (covered ultrasonic) detected | 91.0% | 70 to 100% |

Setup: trained on 3000 normal frames (150 windows), test stream mixes normal, intruder and blocking segments with 2% UART corruption. Each seed's test stream has about 130 normal, 12 intruder and 12 blocking windows.

**Firmware frames through the PC pipeline (`frames_log.txt`):**
- 516 frames copied from the MPLAB simulator UART window, **0 rejected** by the checksum. Firmware framing and PC parser agree.
- 25 windows scored. Intruder segment (windows 11 to 15): windows 11 to 14 alert, window 15 missed (4 of 5).
- Windows 3 and 23 are false alarms. They are the same scripted 3 frame PIR burst, which appears twice because the firmware table repeats.

**Other facts for the slide:**
- UART link: 9600 baud, a frame every 200 ms (5 per second).
- Corrupted frames: XOR checksum catches every single character flip, so 2% corruption was filtered out before windowing.

## Slide 2b: Limitations (say these yourself, first)
- **All data is simulated and scripted.** Results validate the pipeline, not real world accuracy.
- **Partly circular.** The model trains on `generator.py` and the test data also comes from `generator.py`. The firmware plays back a scripted 400 frame table from the same generator.
- **No real sensors were run.** The read functions exist behind `USE_FAKE_SENSORS` but were never exercised. CCP capture and interrupt on change are not implemented.
- **Wide spread over seeds.** Each seed has only about 12 intruder windows, so the intruder rate swings from 56% to 100%. Quote the mean and the range, not one lucky run.
- **Small firmware sample.** The log has only 20 normal windows, so 2 false alarms looks like 10%. It is one scripted burst counted twice. The 1.3% figure is the better estimate.
- **Blocking is easy by construction.** It is defined as no echo on 90% of frames, and a one line rule on `no_echo_ratio` would probably do as well. The model's value is the intruder class, where several weak signals combine.
- **Weak on extreme values.** Isolation Forest cannot tell how far a value is outside its training range, and our training glitch rate was about 1%, so blocking is detected less strongly than it should be.
- **False alarm rate is partly a setting.** `contamination=0.02` fixes roughly how many training windows are treated as unusual.
- **Latency.** A window is 4 s, so an alert comes up to 4 s after the event.
- **Not benchmarked.** We did not compare against a threshold rule or against the baseline method in paper 7.

## Slide 2c: Future work
- **Real hardware and real data:** run the real sensor read functions on the PIC with real PIR, ultrasonic and sound sensors, record normal behaviour in a real room, and retrain on that.
- **Calibrate on real data:** set the threshold and measure the real false alarm rate.
- **Use more of the PIC:** CCP capture for echo timing and interrupt on change for the digital sensors would suit the real hardware. Today they are not implemented.
- **Honest baselines:** compare against a plain threshold rule and against a baseline plus weighted index method like paper 7.
- **Robustness tests:** widen the glitch rates in training and re-run 20 seeds, report whichever way it goes. Try overlapping windows to cut alert latency.
- **Live link:** stream frames over a real or virtual COM port instead of copying the UART window.

## Speaker notes for Section 2
- Lead with the limits, then the numbers. It sounds stronger than waiting to be asked.
- Say "validates the pipeline, not real world accuracy" once, clearly.
- Quote the 20 seed table. Do not quote the single seed 7 run, it was a lucky draw (100% and 100%).
- Point at the miss (window 15) and the false alarm (window 3) on the firmware log yourself.
- What the results do show: the parser and the firmware agree, the model separates the scripted classes better than chance, and the false alarm rate is low on simulated normal data.
- Close: the next step is real sensor data.

---

## Likely questions on these slides

| Question | Short answer |
|---|---|
| Why ML and not a threshold? | A threshold on one sensor cannot see combinations, such as short PIR bursts plus sound plus moving distance. Labelled intrusions are impractical to collect, so we use unsupervised detection. For the blocking class a threshold would probably do as well, and we say so. |
| Why Isolation Forest? | Trains on normal only, light and fast, easy to explain, and used for IoT tampering in paper 6. |
| Is your gap real? | Within our seven papers, yes. We do not claim to have surveyed all literature. The closest is paper 7, and we have not benchmarked against it. |
| Why is intruder detection only 84.5%? | Intruder windows can look like normal ones when motion is brief, and there are only about 12 intruder windows per seed, so the range is wide (56 to 100%). |
| Why is the result trustworthy if you made the data? | It is not proof of real world accuracy. It shows the pipeline works end to end and the features separate the scripted classes. Real data is the next step. |
| Where is the embedded part? | Timer2 interrupt for 200 ms sampling, hardware USART at 9600 baud, XOR checksum framing, Timer1 as a microsecond counter for echo timing. |

## Do not say
- Do not claim CCP capture or interrupt on change are implemented.
- Do not claim live streaming. The demo is copy then score.
- Do not claim real world accuracy or real sensor results.
- Do not claim "first" or "novel" without "within our literature set".

---

## Check before you present
- **Paper descriptions come from abstracts and repository pages.** Read the full texts of 1, 4 and 7 if you can, and edit the table row if a detail is wrong.
- **Paper 4:** the Springer chapter was matched through an Amrita University listing. The abstract confirms a Wi-Fi camera, PIR, HOG and Haar features with an SVM. The author name "Gaddipati" was not confirmed, so check it on the Springer page before you cite it.
- **Paper 1:** only the abstract was found (keywords PIR, GSM, ESP8266). The "one trigger, one alarm" limitation is inferred from the abstract, so soften it if the full text shows more.
- **Paper 6:** the 84% and 91.62% accuracy figures from that paper use different metrics (silhouette for the forest, cross validation accuracy for the tree). Do not put them side by side as if comparable with our rates.
- **Paper 7 as the ESP32 paper:** CLAUDE.md mentions "the ESP32 paper in our literature set avoided ML". Paper 7 uses an ESP32 and no learned model, so it is probably the one. Confirm.

## Sources used for the paper summaries
- Paper 1: [NIT Rourkela repository record](https://dspace.nitrkl.ac.in/dspace/handle/2080/2716)
- Paper 2: [arXiv preprint 1710.01581](https://arxiv.org/abs/1710.01581v2)
- Paper 3: [IISc ePrints](https://eprints.iisc.ac.in/33851/), [Chalmers research portal](https://research.chalmers.se/en/publication/185959)
- Paper 4: [Amrita publication listing](https://www.amrita.edu/publication/real-time-human-intrusion-detection-for-home-surveillance-based-on-iot/)
- Paper 6: [CPS-VO record](https://archive.cps-vo.org/node/81815)
- Paper 7: [IJSAT paper PDF](https://www.ijsat.org/papers/2026/2/10874.pdf)
- Paper 5 (Isolation Forest): described from general knowledge of the paper, not looked up here.
