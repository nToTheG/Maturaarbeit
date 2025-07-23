"""
Date: 16.07.2025
Author: Nelio Gautschi
Purpose:
    - Implement keyboard arrows to move the drone
"""

import sys
import time
from pynput import keyboard

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

URI = 'radio://0/80/2M/E7E7E7E7E7'

mode = 0
SLEEP_TIME = 0.1
stop = False

HOVER_VALUE = 37000
UP_VALUE = HOVER_VALUE + 2000
DOWN_VALUE = HOVER_VALUE - 2000
TILT_VALUE = 5
TURN_VALUE = 90

pressed_keys = set()
SPECIAL_KEYS = {
    keyboard.Key.esc: "esc",
    keyboard.Key.up: "forward",
    keyboard.Key.down: "backward",
    keyboard.Key.left: "turn left",
    keyboard.Key.right: "turn right"
}

CHAR_KEYS = {
    "w": "up",
    "s": "down"
}

def control(cf):
    roll = 0.0
    pitch = tilt()
    yawrate = turn()
    thrust = power()
    cf.commander.send_setpoint(roll, pitch, yawrate, thrust)

def tilt():
    if "forward" in pressed_keys:
        return TILT_VALUE
    elif "backward" in pressed_keys:
        return -TILT_VALUE
    else:
        return 0.0

def turn():
    if "turn right" in pressed_keys:
        return TURN_VALUE
    elif "turn left" in pressed_keys:
        return -TURN_VALUE
    else:
        return 0.0

def power():
    if "up" in pressed_keys:
        return UP_VALUE
    elif "down" in pressed_keys:
        return DOWN_VALUE
    else:
        return HOVER_VALUE

def landing(cf):
    print("Landing process initiated...")
    for _ in range(30):
        cf.commander.send_setpoint(0, 0, 0, 0)
        time.sleep(SLEEP_TIME)
    print("Landed.")

def on_press(key):
    global stop
    try:
        if hasattr(key, "char") and key.char in CHAR_KEYS:
            pressed_keys.add(CHAR_KEYS[key.char])

        elif key in SPECIAL_KEYS:
            pressed_keys.add(SPECIAL_KEYS[key])
            if SPECIAL_KEYS[key] == "esc":
                stop = True

        else:
            pass
    except Exception as e:
        print(f"Error: {e}")

def on_release(key):
    if hasattr(key, "char") and key.char in CHAR_KEYS:
        pressed_keys.discard(CHAR_KEYS[key.char])

    elif key in SPECIAL_KEYS:
        pressed_keys.discard(SPECIAL_KEYS[key])

def main():
    cflib.crtp.init_drivers()
    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='cache')) as scf:
            scf.cf.commander.send_setpoint(0, 0, 0, 0)
            while not stop:
                control(scf.cf)
                time.sleep(SLEEP_TIME)
            landing(scf.cf)

    except Exception as e:
        print("❌ Exception:", e)
        sys.exit()

if __name__ == '__main__':
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    main()
    listener.stop()