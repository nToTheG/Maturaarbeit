"""
Date: 30.09.2025

Author: Nelio Gautschi

Purpose:
    - Implement keyboard to move the drone
"""

import time

from pynput import keyboard
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

import my_debug
import my_config


URI = my_config.MY_URI
DEFAULT_HEIGHT = 1.0
SLEEP_TIME = 0.1

SPECIAL_KEYS = {
    keyboard.Key.esc: "esc",
    keyboard.Key.up: "forward",
    keyboard.Key.down: "backward",
    keyboard.Key.left: "left",
    keyboard.Key.right: "right"
}
SK_VALS = SPECIAL_KEYS.values()

CHAR_KEYS = {
    "w": "up",
    "s": "down"
}
CK_VALS = CHAR_KEYS.values()

class KeyboardListener:
    """
    haha
    """

    def __init__(self):
        self.pressed_key = set()

    def on_press(self, key):
        """
        Handles key press events.
        """

        try:
            if not self.pressed_key:
                if hasattr(key, "char") and key.char in CHAR_KEYS:
                    self.pressed_key.add(CHAR_KEYS[key.char])

                elif key in SPECIAL_KEYS:
                    self.pressed_key.add(SPECIAL_KEYS[key])

        except AttributeError:
            pass

    def on_release(self, key):
        """
        Handles key release events.
        """

        if hasattr(key, "char") and key.char in CHAR_KEYS:
            self.pressed_key.discard(CHAR_KEYS[key.char])

        elif key in SPECIAL_KEYS:
            self.pressed_key.discard(SPECIAL_KEYS[key])

class DroneController:
    """
    Handles keyboard-based control for Crazyflie.
    """

    def __init__(self, listener):
        self.mode = "auto"
        self.listener = listener
        self.running = True

    def send_instructions(self, mc):
        """
        Sends a movement setpoint to Crazyflie based on current key input.
        """

        if "esc" in self.listener.pressed_key:
            print("ESC pressed → landing")
            self.running = False
            mc.stop()
            return

        if self.listener.pressed_key:
            key = next(iter(self.listener.pressed_key))

            if key == "left":
                mc.start_turn_left(30)

            elif key == "right":
                mc.start_turn_right(30)

        else:
            mc.start_linear_motion(0, 0, 0, rate_yaw=0.0)

        time.sleep(0.1)


    def main(self, scf):
        """
        Main function that initiates Motioncommander.
        """

        with MotionCommander(scf, default_height=0.5) as mc:
            while self.running:
                self.send_instructions(mc)

def main():
    """
    Handles DroneController class.
    Handles keyboard listener.
    Initializes Crazyflie connection.
    """

    kb_listener = KeyboardListener()
    listener = keyboard.Listener(on_press=kb_listener.on_press, on_release=kb_listener.on_release)
    listener.start()

    controller = DroneController(kb_listener)

    cflib.crtp.init_drivers()
    my_debug.main("deck")

    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='cache')) as scf:
            scf.cf.platform.send_arming_request(True)
            time.sleep(1.0)
            controller.main(scf)

    except Exception as e:
        my_debug.main("error", e)


if __name__ == "__main__":
    main()
