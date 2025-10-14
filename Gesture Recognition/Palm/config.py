"""
Date: 13.10.2025

Author: Nelio Gautschi

Purpose:
    - Storing configuration values.
"""

import time

import cv2


MY_ARUCO_DICT = cv2.aruco.DICT_4X4_50
USED_TAGS = [1, 2, 3, 4]
H_DZ = 0.06
V_DZ = 0.01

MY_URI = "radio://0/80/2M/E7E7E7E7E7"

DEFAULT_HEIGHT = 1.0

V_ALT = 0.2
V_HOR = 0.8
V_YAW = 90

my_exceptions = {
    f"No driver found or malformed URI: {MY_URI}": "❌ Crazyradio not plugged in.",
    "Could not load link driver: Cannot find a Crazyradio Dongle": "❌ Crazyradio not plugged in.",
    "Too many packets lost": "❌ Crazyflie not turned on."
}

def frame_text(frame, add_text):
    flipped_frame = cv2.flip(frame, 1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    green = (0, 255, 0)
    gray = (0, 200, 0)
    lines = [
        (f"Calibrating{'.' * ((int(time.time() / 0.75) % 3) + 1)}{add_text}", 1, green, 2),
        ("Position your hand 30cm away from the camera in the middle of the screen.", 0.6, gray, 1),
        ("Press 's' when you are ready.", 0.6, gray, 1)
    ]

    y_offset = 10
    for text, scale, color, thickness in lines:
        text_size = cv2.getTextSize(text, font, scale, thickness)[0]
        x = (flipped_frame.shape[1] - text_size[0]) // 2
        y = y_offset + text_size[1]
        cv2.putText(flipped_frame, text, (x, y), font, scale, color, thickness)
        y_offset = y + 10

    return cv2.flip(flipped_frame, 1)
