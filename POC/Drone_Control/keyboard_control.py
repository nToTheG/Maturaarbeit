"""
Date: 16.07.2025

Author: Nelio Gautschi

Purpose:
    - Implement keyboard to move the drone
"""

import time

from pynput import keyboard
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

import my_debug
import my_config


URI = my_config.MY_URI
SLEEP_TIME = 0.1
HOVER_VALUE = 39000
UP_VALUE = HOVER_VALUE + 2000
DOWN_VALUE = HOVER_VALUE - 2000
TILT_VALUE = 5
TURN_VALUE = 90
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


class DroneController:
    """
    Handles keyboard-based control for Crazyflie.
    """

    def __init__(self):
        self.stop = False
        self.pressed_keys = set()

    def send_instructions(self, cf):
        """
        Sends a movement setpoint to Crazyflie based on current key input.
        """

        roll = 0.0
        pitch = self.get_pitch()
        yawrate = self.get_yawrate()
        thrust = self.get_thrust()

        cf.commander.send_setpoint(roll, pitch, yawrate, thrust)

    def get_pitch(self):
        """
        Determines tilt direction based on key input.
        """

        if "forward" in self.pressed_keys:
            return TILT_VALUE
        if "backward" in self.pressed_keys:
            return -TILT_VALUE
        return 0.0

    def get_yawrate(self):
        """
        Determines turn direction based on key input.
        """

        if "turn right" in self.pressed_keys:
            return TURN_VALUE
        if "turn left" in self.pressed_keys:
            return -TURN_VALUE
        return 0.0

    def get_thrust(self):
        """
        Determines thrust level based on key input.
        """

        if "up" in self.pressed_keys:
            return UP_VALUE
        if "down" in self.pressed_keys:
            return DOWN_VALUE
        return HOVER_VALUE

    def landing(self, cf):
        """
        Lands the Crazyflie to prevent supervisor-lock issues.
        """

        print("Landing process initiated...")
        for _ in range(30):
            cf.commander.send_setpoint(0, 0, 0, 0)
            time.sleep(SLEEP_TIME)
        print("Landed.")

    def on_press(self, key):
        """
        Handles key press events.
        """

        try:
            if hasattr(key, "char") and key.char in CHAR_KEYS:
                self.pressed_keys.add(CHAR_KEYS[key.char])

            elif key in SPECIAL_KEYS:
                self.pressed_keys.add(SPECIAL_KEYS[key])
                if SPECIAL_KEYS[key] == "esc":
                    self.stop = True
            else:
                pass
        except AttributeError:
            pass

    def on_release(self, key):
        """
        Handles key release events.
        """

        if hasattr(key, "char") and key.char in CHAR_KEYS:
            self.pressed_keys.discard(CHAR_KEYS[key.char])

        elif key in SPECIAL_KEYS:
            self.pressed_keys.discard(SPECIAL_KEYS[key])


def main():
    """
    Handles DroneController class.
    Handles keyboard listener.
    Initializes Crazyflie connection.
    """

    controller = DroneController()

    listener = keyboard.Listener(on_press=controller.on_press, on_release=controller.on_release)
    listener.start()

    cflib.crtp.init_drivers()

    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache="cache")) as scf:
            scf.cf.commander.send_setpoint(0, 0, 0, 0)
            while not controller.stop:
                controller.send_instructions(scf.cf)
                time.sleep(SLEEP_TIME)
            controller.landing(scf.cf)
            listener.stop()

    except Exception as e:
        my_debug.main("error", e)

if __name__ == "__main__":
    main()
