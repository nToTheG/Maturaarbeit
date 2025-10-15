"""
Date: 14.10.2025

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

DEFAULT_HEIGHT = 0.5

V_ALT = 0.2
V_HOR = 0.5
V_YAW = 30

my_exceptions = {
    f"No driver found or malformed URI: {MY_URI}": "❌ Crazyradio not plugged in.",
    "Could not load link driver: Cannot find a Crazyradio Dongle": "❌ Crazyradio not plugged in.",
    "Too many packets lost": "❌ Crazyflie not turned on."
}


def frame_text(frame, mode):
    flipped_frame = cv2.flip(frame, 1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    green = (0, 255, 0)
    gray = (200, 0, 0)
    red = (0, 0, 255)

    lines = [
        (f"Calibrating{'.' * ((int(time.time() / 0.75) % 3) + 1)}", green, 2),
        ("Failed. Try again.", red, 2),
        ("Position your hand 30cm away from the camera in the middle of the screen.", gray, 2),
        ("Press 's' when you see red dots on all tag corners.", gray, 1),
        ("Success. Starting drone...", green, 2)
    ]

    y_offset = 10

    for _, i in enumerate(mode):
        text, color, thickness = lines[i-1]
        text_size = cv2.getTextSize(text, font, 1.0, thickness)[0]
        x = (flipped_frame.shape[1] - text_size[0]) // 2
        y = y_offset + text_size[1]
        cv2.putText(flipped_frame, text, (x, y), font, 1.0, color, thickness)
        y_offset = y + 10

    return cv2.flip(flipped_frame, 1)
