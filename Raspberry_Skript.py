#!/usr/bin/env python3

import serial
import os
import smtplib
import time
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv

# --- KONFIGURATION ---
PORT = '/dev/ttyACM0'
BAUD = 115200
FOLDER = '/mnt/data/'
SCHWELLE_GEWICHT = 2000.0  # Gramm
TIMEOUT_ABBRUCH = 500        # Sekunden unter Schwelle bis zum Ende

# E-Mail Konfiguration
load_dotenv('/mnt/data/.env')
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORT = os.getenv("EMAIL_PASSWORT")
EMAIL_EMPFAENGER = "inkenmbrandt@gmail.com"
SMTP_SERVER = "smtp.th-wildau.de"
SMTP_PORT = 25

# --- INITIALISIERUNG ---
timestamp_start = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
csv_filename = f"messung_{timestamp_start}.csv"
csv_path = os.path.join(FOLDER, csv_filename)

def sende_email_mit_anhang(dateipfad):
    print(f"Sende E-Mail mit Anhang: {dateipfad}...")
    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_EMPFAENGER
    msg["Subject"] = f"Messung abgeschlossen - {timestamp_start}"
    msg.set_content(f"Die Messung wurde automatisch beendet.\nAnbei findest du die Daten: {csv_filename}")

    # Datei als Anhang hinzufügen
    try:
        with open(dateipfad, 'rb') as f:
            file_data = f.read()
            msg.add_attachment(
                file_data,
                maintype='text',
                subtype='csv',
                filename=csv_filename
            )

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORT)
            server.send_message(msg)
        print("E-Mail erfolgreich gesendet!")
    except Exception as e:
        print(f"Fehler beim E-Mail-Versand: {e}")

# --- HAUPTPROGRAMM ---
try:
    arduino = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(3) 
except Exception as e:
    print(f"Serieller Fehler: {e}")
    exit()

# Header schreiben
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

with open(csv_path, 'w') as f:
    f.write('System_Zeit,Arduino_ms,Gewicht_g\n')

unter_schwelle_seit = None
messung_aktiv = True


try:
    with open(csv_path, 'a') as f:
        while messung_aktiv:
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').strip()
                if line and "," in line:
                    try:
                        parts = line.split(',')
                        arduino_ms = parts[0]
                        weight = float(parts[1])
                        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                        f.write(f"{now_str},{arduino_ms},{weight}\n")
                        f.flush()
                        
                        # Abbruch-Logik
                        if weight < SCHWELLE_GEWICHT:
                            if unter_schwelle_seit is None:
                                unter_schwelle_seit = time.time()
                            elif (time.time() - unter_schwelle_seit) >= TIMEOUT_ABBRUCH:
                                print("\nSchwelle unterschritten. Beende Messung...")
                                messung_aktiv = False
                        else:
                            unter_schwelle_seit = None
                            
                    except (IndexError, ValueError):
                        continue
except KeyboardInterrupt:
    print("\nManuell abgebrochen.")

# Nach dem Ende der Schleife: E-Mail senden
arduino.close()
sende_email_mit_anhang(csv_path)
print("Programm beendet.")