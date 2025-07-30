"""
Date: 25.07.2025

Author: Nelio Gautschi

Purpose:
    - Store configuration values used across the project
"""

MY_URI = "radio://0/80/2M/E7E7E7E7E7"

my_exceptions = {
    f"No driver found or malformed URI: {MY_URI}": "❌ Crazyradio not plugged in.",
    "Could not load link driver: Cannot find a Crazyradio Dongle": "❌ Crazyradio not plugged in.",
    "Too many packets lost": "❌ Crazyflie not turned on."
}
