/*
  Context-aware intrusion detection: ESP32-S3 sensor front end.
  Samples PIR, ultrasonic distance and a digital sound sensor every 200 ms
  and sends one frame per sample over UART:   P:1,D:45,S:0*7D
  The part after '*' is the XOR of every payload character, as 2 hex digits.
  D = 0 means "no echo came back".

  Pins (ESP32-S3, avoid 26-37 flash/PSRAM and strapping pins 0, 3, 45, 46):
    PIR output      -> GPIO 4
    Sound DO        -> GPIO 5
    HC-SR04 TRIG    -> GPIO 6
    HC-SR04 ECHO    -> GPIO 7  THROUGH a 5V -> 3.3V divider (e.g. 1k + 2k)
*/
#include <Arduino.h>

#define PIN_PIR    4
#define PIN_SOUND  5
#define PIN_TRIG   6
#define PIN_ECHO   7

const int      SOUND_ACTIVE_LEVEL = HIGH;   // set LOW if your sound module pulls DO low on sound
const uint32_t SAMPLE_PERIOD_US   = 200000; // 200 ms -> 5 frames per second
const uint32_t ECHO_TIMEOUT_US    = 30000;  // about 5 m, longer means "no echo"
const uint32_t WARMUP_MS          = 30000;  // PIR modules need time to settle

volatile bool sampleFlag = false;           // set by the timer interrupt
volatile bool soundHit   = false;           // set by the sound pin interrupt
hw_timer_t *sampleTimer  = nullptr;

void IRAM_ATTR onSampleTimer() { sampleFlag = true; }
void IRAM_ATTR onSoundEdge()   { if (digitalRead(PIN_SOUND) == SOUND_ACTIVE_LEVEL) soundHit = true; }

int readDistanceCm() {
  digitalWrite(PIN_TRIG, LOW);  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  unsigned long us = pulseIn(PIN_ECHO, HIGH, ECHO_TIMEOUT_US);
  if (us == 0) return 0;                    // no echo
  int cm = (int)(us / 58);
  if (cm < 1) cm = 1;                       // keep 0 reserved for "no echo"
  if (cm > 400) cm = 400;
  return cm;
}

void sendFrame(int p, int d, int s) {
  char payload[32];
  snprintf(payload, sizeof(payload), "P:%d,D:%d,S:%d", p, d, s);
  uint8_t cs = 0;
  for (const char *c = payload; *c; ++c) cs ^= (uint8_t)*c;
  Serial.printf("%s*%02X\n", payload, cs);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_PIR, INPUT);
  pinMode(PIN_SOUND, INPUT);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  digitalWrite(PIN_TRIG, LOW);

  Serial.println("# warming up sensors");
  delay(WARMUP_MS);
  Serial.println("# running");

  attachInterrupt(digitalPinToInterrupt(PIN_SOUND), onSoundEdge, CHANGE);

#if ESP_ARDUINO_VERSION_MAJOR >= 3
  sampleTimer = timerBegin(1000000);                       // 1 MHz tick
  timerAttachInterrupt(sampleTimer, &onSampleTimer);
  timerAlarm(sampleTimer, SAMPLE_PERIOD_US, true, 0);      // periodic
#else
  sampleTimer = timerBegin(0, 80, true);                   // 80 MHz / 80 = 1 MHz
  timerAttachInterrupt(sampleTimer, &onSampleTimer, true);
  timerAlarmWrite(sampleTimer, SAMPLE_PERIOD_US, true);
  timerAlarmEnable(sampleTimer);
#endif
}

void loop() {
  if (!sampleFlag) return;
  sampleFlag = false;

  int p = digitalRead(PIN_PIR) ? 1 : 0;
  int d = readDistanceCm();
  int s = soundHit ? 1 : 0;
  soundHit = false;
  sendFrame(p, d, s);
}
