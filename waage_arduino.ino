#include "HX711.h"

// Arduino Pins
const int dt = 8;
const int sck = 9;

HX711 scale;
float calibration_faktor = -107.5; // Rohwert/Gewicht

void setup() {
  Serial.begin(115200);
  scale.begin(dt, sck);
  
  delay(1000);
  
  // Tarieren
  scale.tare();
  scale.set_scale(calibration_faktor);
  
  // Bestätigung an Raspberry senden
  Serial.println("READY");
}

void loop() {
  // Gewicht messen 
  float weight = scale.get_units();
  
  // Arduino-Zeit in Millisekunden
  unsigned long timestamp = millis();
  
  // CSV-Format senden: timestamp,gewicht
  Serial.print(timestamp);
  Serial.print(",");
  Serial.println(weight, 1); 
  
}