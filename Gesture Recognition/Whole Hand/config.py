"""
Date: 14.10.2025

Author: Nelio Gautschi

Purpose:
    - Stores project-wide important information
"""

import time

import cv2


MY_ARUCO_DICT = cv2.aruco.DICT_4X4_50
USED_TAGS = [1, 2, 3, 4]
MY_URI = "radio://0/80/2M/E7E7E7E7E7"

DEFAULT_HEIGHT = 0.5

T_DZ = 0.06
A_DZ = 100
Y_DZ = 0.01

VT = 0.5 # tilt (forward/backward) velocity
VA = 0.2 # altitude (up/down) velocity
VY = 30 # yaw (right/left) velocity

my_exceptions = {
    f"No driver found or malformed URI: {MY_URI}": "❌ Crazyradio not plugged in.",
    "Could not load link driver: Cannot find a Crazyradio Dongle": "❌ Crazyradio not plugged in.",
    "Too many packets lost": "❌ Crazyflie not turned on."
}


def draw_text(frame, mode):
    """
    Draws text and animations based on current state of the calibration process.
    """

    flipped_frame = cv2.flip(frame, 1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    gray = (200, 0, 0)

    lines = [
        (f"Calibrating{'.' * ((int(time.time() / 0.75) % 3) + 1)}", (0, 255, 0), 2),
        ("Failed. Try again.", (0, 0, 255), 2),
        ("Position your hand 30cm away from the camera in the middle of the screen.", gray, 2),
        ("Press 's' when you see red dots on all tag corners.", gray, 1)
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
