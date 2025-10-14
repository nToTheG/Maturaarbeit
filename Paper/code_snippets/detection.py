"Autor: Nelio Gautschi"

import cv2 # Importiert die OpenCV-Bibliothek für Bildverarbeitung

cam = cv2.VideoCapture(0) # Zugriff auf die Kamera

# Überprüfen, ob die Kamera erfolgreich geöffnet wurde
if not cam.isOpened():
    raise IOError("Cannot open camera.")

while True: # Schleife zum kontinuierlichen Einlesen von Bildern
    success, frame = cam.read()
    if not success:
        print("Cannot receive frame. Exiting ...")
        break

    # Umwandeln des Farbbilds in ein Graustufenbild
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Definition der verwendeten ArUco-Bibliothek
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    # Erstellen eines Parameterobjekts für den Erkennungsprozess
    parameters = cv2.aruco.DetectorParameters()

    # Initialisieren des ArUco-Detektors
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # Erkennen der Marker im aktuellen Kamerabild
    corners, ids, rejected = detector.detectMarkers(gray_frame)
