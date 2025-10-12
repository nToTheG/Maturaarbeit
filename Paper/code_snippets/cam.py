"""
cam.py
Autor: Nelio Gautschi
"""

import cv2  # Importiert die OpenCV-Bibliothek für Bildverarbeitung

# Zugriff auf die Standardkamera (Index 0)
cam = cv2.VideoCapture(0)

# Überprüfen, ob die Kamera erfolgreich geöffnet wurde
if not cam.isOpened():
    raise IOError("Cannot open camera.")

# Endlosschleife zum kontinuierlichen Einlesen von Kamerabildern
while True:
    # success: Status, frame: aktuelles Kamerabild
    success, frame = cam.read()
    if not success:
        print("Cannot receive frame. Exiting ...")
        break

    # Umwandeln des Farbbilds in ein Graustufenbild
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Spiegelung entlang der vertikalen Achse
    flipped_frame = cv2.flip(gray_frame, 1)
