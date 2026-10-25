# Hardware shopping list (ESP32-S3 intrusion detector)

Built from FIRMWARE_GUIDE.md sections 3, 8 to 11. "Have" is what the guide says is already in hand. Quantities marked **unsure** are my estimate, not a count from the guide.

Status key: **HAVE** (in hand), **BUY** (not yet ordered), **CHECK** (confirm whether you have it).

## Core parts

| # | Item | Qty to have | Status | Notes |
|---|---|---|---|---|
| 1 | ESP32-S3 dev board, ESP32-S3-N16R8 module, two USB-C ports | 1 | HAVE | Check the header pins are soldered on. If not, you need to solder them or buy a board with headers. |
| 2 | HC-SR04 ultrasonic sensor (5 V) | 1 to use + 1 spare = **2** | BUY | The HC-SR04P variant works at 3.3 V and needs no divider, but the guide is written for the 5 V one. Check the listing says "P" only if you want that one. |
| 3 | HC-SR501 PIR motion module | 1 to use + 1 spare = **2** | BUY | Has a jumper (set to H, repeat trigger) and two knobs (delay and sensitivity). |
| 4 | Digital sound module, LM393 type, pins DO, GND, VCC, with threshold knob | 1 to use + 1 spare = **2** | BUY | The guide says to buy a spare of the HC-SR04 and PIR. I added a spare sound module, since they are cheap. [My addition] |
| 5 | Resistor 1k ohm | 1 needed, buy **5** | BUY | For the ECHO divider. 10k and 20k also work. Resistors are sold in packs, so buy extra. |
| 6 | Resistor 2k ohm | 1 needed, buy **5** | BUY | Same divider. 2k is an uncommon value, so a 10k + 20k pair, or two 1k in series, is a fallback. |
| 7 | Breadboard | 1 | HAVE | Guide says it exists. Size not stated. A half size (400 point) board is enough. |
| 8 | USB cable that carries data (USB-C to your laptop) | 1 | **CHECK** | Charge-only cables are a common cause of "no COM port". Buy a second as a spare if unsure. |

## Wires

| # | Item | Qty | Status | Notes |
|---|---|---|---|---|
| 9 | Male to male jumper wires | about 15 | BUY | **Unsure.** Wiring needs 10 connections (PIR 3, sound 3, HC-SR04 4) plus the divider and ground rails. A pack of 20 or 40 is the usual size. |
| 10 | Male to female jumper wires | about 10 | BUY | **Unsure.** Needed if the board or modules have pins that don't fit the breadboard directly. Buy a mixed pack. |

## For testing (not parts, but you need them)

| # | Item | Qty | Status | Notes |
|---|---|---|---|---|
| 11 | Ruler or tape measure | 1 | CHECK | For the distance test at 10, 30 and 100 cm. |
| 12 | Card or stiff paper | 1 | CHECK | For the cover test (hand at 1 cm and a card at 5 cm). |
| 13 | Tape or cloth | 1 | CHECK | For the "covered with tape or cloth" blocking test I suggested. |
| 14 | Laptop with Arduino IDE 2.x, ESP32 core, Python 3 and `pyserial numpy scikit-learn joblib` | 1 | HAVE | Software, not a purchase. Listed because the board needs a free USB port. |

## Optional (only if something goes wrong)

| Item | Qty | Notes |
|---|---|---|
| Multimeter | 1 | To check the divider gives about 3.3 V at GPIO 7. **Unsure** whether you need it, the guide doesn't ask for one. |
| Soldering iron and solder | 1 | Only if the board's header pins or a module's pins are not soldered. **Unsure**, depends on what arrives. |
| Second ESP32-S3 board | 1 | Not in the guide. Only if you want a spare against a dead board. [My addition, probably not needed] |

## Not needed
Camera, relay, display, external 5 V supply (everything runs from USB), Wi-Fi hardware. The guide says do not order a camera, relay or display.

## Connection summary (for checking you have enough wire)

| Sensor | Pin | Goes to |
|---|---|---|
| PIR | VCC, GND, OUT | 5V, GND, GPIO 4 |
| Sound | VCC, GND, DO | **3V3** (not 5 V), GND, GPIO 5 |
| HC-SR04 | VCC, GND, TRIG, ECHO | 5V, GND, GPIO 6, GPIO 7 **through the 1k and 2k divider** |

## Minimum to order today
HC-SR04 x2, HC-SR501 x2, LM393 sound module x2, 1k resistors, 2k resistors, jumper wire packs (male to male and male to female). Check the USB cable and the board's header pins.
