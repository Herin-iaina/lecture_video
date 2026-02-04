// ================= CONFIG =================

// Pins boutons A → G
const uint8_t buttonPins[7] = {2, 3, 4, 5, 6, 7, 8};

// Commandes envoyées
const char commands[7] = {'A', 'B', 'C', 'D', 'E', 'F', 'G'};

// Timings (ms)
const unsigned long debounceDelay = 300;   // anti-rebond
const unsigned long noiseFilterDelay = 30; // filtre parasites

// ================= VARIABLES ==============

bool stableState[7];
bool lastReading[7];
unsigned long lastDebounceTime[7];

// ==========================================

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < 7; i++) {
    pinMode(buttonPins[i], INPUT);
    stableState[i] = LOW;
    lastReading[i] = LOW;
    lastDebounceTime[i] = 0;
  }

  delay(1000);
  Serial.println("READY");
}

void loop() {
  for (int i = 0; i < 7; i++) {
    bool reading = digitalRead(buttonPins[i]);

    // Détection changement
    if (reading != lastReading[i]) {
      lastDebounceTime[i] = millis();
    }

    // Si état stable assez longtemps
    if ((millis() - lastDebounceTime[i]) > debounceDelay) {

      // Changement réel détecté
      if (reading != stableState[i]) {
        stableState[i] = reading;

        // Appui validé (LOW -> HIGH)
        if (stableState[i] == HIGH) {
          Serial.println(commands[i]);
        }
      }
    }

    lastReading[i] = reading;
  }
}
