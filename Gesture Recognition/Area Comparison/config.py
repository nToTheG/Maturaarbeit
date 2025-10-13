"""
Date: 13.10.2025

Author: Nelio Gautschi

Purpose:
    - Storing configuration values.
"""

import cv2


MY_ARUCO_DICT = cv2.aruco.DICT_4X4_50
USED_TAGS = [1, 2, 3, 4]
H_DZ = 0.1
V_DZ = 0.07

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
