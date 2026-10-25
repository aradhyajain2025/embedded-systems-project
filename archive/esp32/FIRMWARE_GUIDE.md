# ESP32-S3 Firmware Guide

Audience: the teammate who owns the firmware. Read all of it once. The work is split into phases so you can start before you hold any hardware.

## 1. Your deliverable

Firmware that reads three sensors every 200 ms and prints one text frame per sample over USB serial. The PC side (Python) reads those frames, checks the checksum, builds windows and runs the anomaly detector.

You hand over:
1. `esp32_ids.ino`, working on the real board.
2. A 60 second raw serial log with all three sensors connected.
3. The completed test table from section 11, including the cover test result.

Starting point: `esp32_ids.ino` (provided). It has been syntax checked only. It has never run on a real board. Read every line, understand it, and fix anything that does not behave. You will be asked about it in the viva.

Files you need from the PC side: `esp32_ids.ino` and `ids_live.py`.

## 2. Where things stand

| Item | Status | Who can use it now |
|---|---|---|
| ESP32-S3 dev board | In hand, held by the PC side | Whoever holds it |
| HC-SR04, PIR, sound module | **Not yet ordered** | Nobody |
| Resistors, jumper wires | **Not yet ordered** (the breadboard exists) | Nobody |

So the order of work is:
- **Phase A (now, no hardware):** install, compile, desk check, run a simulator.
- **Phase B (board in hand, no sensors):** flash and check the frame stream.
- **Phase C (sensors arrived):** wire up, test, hand over.

Until you hold the board yourself, send your sketch to the person who has it. They flash it, run the checks in Phase B and report back. You then fix and resend.

## 3. Parts

| Item | Detail |
|---|---|
| Board | ESP32-S3 dev board with an ESP32-S3-N16R8 module (16 MB flash, 8 MB octal PSRAM), two USB-C ports |
| Ultrasonic | HC-SR04 (5 V). The HC-SR04P variant works at 3.3 V and needs no divider. Check the listing says "P" |
| Motion | HC-SR501 PIR module |
| Sound | Digital sound module with a DO pin and a threshold knob (LM393 type), marked DO, GND, VCC |
| Resistors | One 1k and one 2k (or 10k and 20k) for the echo divider |
| Wires | Male to female and male to male jumper wires |
| USB | A cable that carries data, not charge only |

**To order:** HC-SR04, HC-SR501, the sound module, the resistors and the jumper wires. Buy a spare HC-SR04 and a spare PIR, because breadboard wiring fails often and the parts are cheap. Do not order a camera, relay or display.

## 4. Software to install

1. **Arduino IDE 2.x** from arduino.cc.
2. **ESP32 board support.** In File, Preferences, add this to "Additional boards manager URLs":
   `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
   Then open Tools, Board, Boards Manager, search "esp32" and install the package by Espressif Systems. The sketch compiles on core 2.x and 3.x, so note which version you installed.
3. **USB driver** (only once you have the board). If no COM port appears, install the driver for the USB to serial chip on the board. The chip name (often CH340 or CP210x) is printed on the small chip near the USB ports. [Likely]
4. **Python 3 and the PC side libraries**, to check your output with `ids_live.py`:
   `pip install pyserial numpy scikit-learn joblib`

Stay on the Arduino framework. Do not switch to ESP-IDF or PlatformIO.

## 5. Arduino IDE settings

| Setting | Value |
|---|---|
| Board | ESP32S3 Dev Module |
| USB CDC On Boot | Disabled if the cable is in the port marked UART or COM. Enabled if it is in the port marked USB |
| Flash Size | 16MB |
| PSRAM | Disabled (unused. Choosing the wrong PSRAM mode on an octal PSRAM part can cause boot loops) [Likely] |
| Everything else | Default |
| Port | The new COM port that appears when the board is plugged in |

If upload fails to connect: hold BOOT, tap RST, release BOOT, then upload again.

## 6. Frame contract

The PC parser depends on this. Do not change it without telling the PC side.

```
P:1,D:45,S:0*7D
```

| Part | Meaning |
|---|---|
| `P` | PIR level, 0 or 1 |
| `D` | Distance in cm, 1 to 400. **0 means no echo came back** |
| `S` | 1 if any sound event happened since the previous frame, else 0 |
| `*7D` | XOR of every character before the `*`, as two uppercase hex digits |

Worked example: the payload `P:1,D:45,S:0` has XOR 0x7D, so the frame ends `*7D`.

Other rules:
- One frame per line, ending in `\n`.
- Baud rate 115200.
- One frame every 200 ms (5 per second). The PC builds windows of 20 frames (4 seconds).
- Lines starting with `#` are comments. The parser ignores them. Use them for warm-up messages only.
- Print nothing else on the serial port. A stray debug line is counted as a corrupted frame.

## 7. What the firmware must do

1. **Setup.** Configure pins. Print `# warming up`, wait 30 seconds for the PIR, print `# running`.
2. **Sampling timer.** A hardware timer fires every 200 ms. The interrupt service routine (ISR) only sets a flag. No Serial calls and no sensor reads inside the ISR.
3. **Sound.** A pin change interrupt on the sound pin latches a flag when the pin is at its active level. Each frame reports the latch and then clears it. If your module goes LOW on sound, change `SOUND_ACTIVE_LEVEL`.
4. **PIR.** Read the pin level at sample time.
5. **Ultrasonic.** Send a 10 microsecond pulse on TRIG, measure the width of the echo pulse on ECHO, and compute `cm = microseconds / 58`. If no echo arrives within 30 ms, report `D = 0`. Clamp real readings to 1 to 400 so that 0 stays reserved for no echo.
6. **Frame.** Build the payload, compute the XOR checksum, print the frame.
7. **Loop.** Do work only when the timer flag is set.

Timing budget: the echo wait can take up to 30 ms, well inside the 200 ms period.

## 8. Phase A: before you have the board

No hardware needed.

1. **Install the software** (section 4, items 1, 2 and 4).
2. **Compile the sketch.** Open `esp32_ids.ino` in a folder named `esp32_ids`. Set Board to ESP32S3 Dev Module and press Verify (the tick). It must compile with no errors. Verify works without a board connected. This catches typos and API differences between core versions.
3. **Check the checksum on your PC.** Compile and run this small C program. The output must be `7D`:
   ```c
   #include <stdio.h>
   #include <stdint.h>
   int main(void) {
       const char *p = "P:1,D:45,S:0";
       uint8_t cs = 0;
       for (; *p; ++p) cs ^= (uint8_t)*p;
       printf("%02X\n", cs);
       return 0;
   }
   ```
4. **Desk check against section 7.** Go through the sketch and tick off each of the seven points. Note anything you would change.
5. **Optional: run it in a simulator.** The Wokwi online simulator (wokwi.com) offers an ESP32-S3 board, an HC-SR04 and a PIR sensor. [Likely] If it has no sound sensor, drive the sound pin with a pushbutton. Create an ESP32-S3 Arduino project, paste the sketch, wire the parts to GPIO 4 (PIR), 5 (sound), 6 (TRIG), 7 (ECHO), and read the serial output. Temporarily set `WARMUP_MS` to 2000 and restore it to 30000 before the real board. Wokwi may not model every ESP32-S3 peripheral exactly. [Guessing] If something fails there, that proves nothing about the real board, so rely on Verify and Phase B.
6. **Check the simulator output with the PC tool.** Copy the serial output into a text file `sim_frames.txt` and run:
   `python ids_live.py record --replay sim_frames.txt --label normal --out sim_check.csv`
   The rejected count should be 0.

## 9. Phase B: board in hand, no sensors

1. **Toolchain check.** Upload the built in Blink example. If this fails, fix the port and driver before anything else.
2. **Frames with no sensors.** Upload `esp32_ids.ino` with nothing connected. After 30 seconds, frames should appear at 5 per second. `D` should be 0. `P` and `S` may flicker because the inputs are floating. That is expected.
3. **Check against the parser.** Run `python ids_live.py record --port COMx --label normal --seconds 60 --out check.csv`. Rejected frames should be 0 or very close to it, and about 300 frames should be saved.

If Phase B passes, the serial path, the timer and the checksum are all confirmed. Only the sensor readings remain.

## 10. Phase C: sensors arrived

### Wiring

Power the board over USB. Join all grounds on one breadboard rail.

| Sensor pin | Connect to | Notes |
|---|---|---|
| PIR VCC | 5V pin | |
| PIR GND | GND | |
| PIR OUT | GPIO 4 | Output is about 3.3 V |
| Sound VCC | **3V3 pin** | Not 5 V. At 5 V the DO output can reach 5 V and damage the GPIO |
| Sound GND | GND | |
| Sound DO | GPIO 5 | |
| HC-SR04 VCC | 5V pin | |
| HC-SR04 GND | GND | |
| HC-SR04 TRIG | GPIO 6 | 3.3 V is enough to trigger it [Likely] |
| HC-SR04 ECHO | GPIO 7 through a divider | See below. Echo is 5 V |

Echo divider (ESP32 GPIOs are not 5 V tolerant):

```
ECHO ---[ 1k ]---+---> GPIO 7
                 |
               [ 2k ]
                 |
                GND
```

This gives about 3.3 V at GPIO 7. If you bought an HC-SR04P, connect ECHO straight to GPIO 7 and power it from 3V3.

PIR module settings: set the jumper to repeat trigger mode (H). Turn the time delay knob to its minimum. Turn the sensitivity knob to about the middle. The PIR needs 30 to 60 seconds after power up to settle.

Sound module: turn the threshold knob until the DO LED stays off in a quiet room and lights on a clap.

**Do not use these GPIOs:** 0, 3, 45, 46 (strapping), 19, 20 (native USB), 26 to 37 (flash and PSRAM), 43, 44 (UART0 used by the serial monitor).

### Bring up, one sensor at a time

1. **Ultrasonic only.** Connect the HC-SR04 with the divider. Test with a ruler at 10, 30 and 100 cm. Readings should be within 1 to 2 cm.
2. **PIR.** Connect it. Wave a hand, watch `P` go to 1, then drop after you stop.
3. **Sound.** Connect it. Clap and watch `S` go to 1 for one frame.
4. **Everything together.** Run for 60 seconds and save the log.
5. **Check against the parser.** Repeat the `record` command from Phase B. Rejected frames should be 0 or very close to it.

## 11. Test table

| Test | Expected | Result |
|---|---|---|
| Frame rate over 60 s | about 300 frames (295 to 305) | |
| Checksum rejects over 300 frames | 0 | |
| Distance at 10 / 30 / 100 cm | within 2 cm | |
| Nothing in front of the sensor, far wall | stable D, small jitter | |
| PIR: hand wave | P rises to 1, falls after motion stops | |
| Sound: clap | S is 1 for the frame, then 0 | |
| **Cover test** | see below | |

**Cover test (required).** Place a hand or a piece of card 1 cm in front of the HC-SR04 for 20 seconds. Record what `D` shows. Report one of:
- `D = 0` on most frames
- a small constant value (say which, for example 2 or 3 cm)
- random or jumping values

Send this result to the PC side. It decides how blocking is handled in the Python software.

## 12. What you can claim in the viva

Honest claims:
- A hardware timer interrupt sets the 200 ms sampling period.
- A pin change interrupt latches sound events.
- UART frames with an XOR checksum at 115200 baud.
- Ultrasonic distance from the echo pulse width.

Do not claim:
- Interrupt driven echo capture. `pulseIn` is a blocking wait of up to 30 ms, unless you replace it.
- RMT capture, DMA, RTOS task scheduling, Wi-Fi or low power modes. None are used.
- Anything about sensor behaviour you have not measured on the real board.

Optional upgrades, only if the basics work. Tell the PC side if you do any of them so the slides can change:
- Replace `pulseIn` with an interrupt on the ECHO pin that records `micros()` on both edges.
- Take the median of three distance readings per frame.

## 13. Troubleshooting

| Symptom | Likely cause |
|---|---|
| Verify fails | Wrong board selected, or a core version difference. Read the first error line |
| No COM port | Data cable, wrong USB port, or missing driver |
| Upload fails | Hold BOOT, tap RST, release BOOT |
| Serial monitor blank | USB CDC On Boot setting does not match the port you plugged into. Flip it and re-upload |
| Garbage characters | Serial monitor baud is not 115200 |
| Board reboots repeatedly | PSRAM setting, or weak power from a long thin cable |
| D always 0 | ECHO divider wrong, HC-SR04 not on 5 V, or TRIG and ECHO swapped |
| P stuck at 1 | PIR still warming up, jumper in the wrong mode, or time delay knob too high |
| S stuck at 1 | Sound threshold knob too sensitive, or the active level is inverted |
