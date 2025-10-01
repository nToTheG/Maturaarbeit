"""
Date: 30.07.2025

Author: Nelio Gautschi

Purpose:
    - First use of MotionCommander together with Flowdeck V2
"""

import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

import my_debug
import my_config


URI = my_config.MY_URI
DEFAULT_HEIGHT = 1.0
SLEEP_TIME = 1


def send_instructions(scf):
    """
    Initializes MotionCommander.
    Sends flight instructions to drone.
    """

    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(2)
        mc.turn_left(180)
        mc.forward(1.5)
        time.sleep(2)
        mc.turn_left(180)
        time.sleep(2)
        mc.forward(1.5)
        mc.stop()


def main():
    """
    Initializes Crazyflie connection.
    Runs the MotionCommander function.
    """

    cflib.crtp.init_drivers()
    my_debug.main("deck")

    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='cache')) as scf:
            scf.cf.platform.send_arming_request(True)
            time.sleep(1.0)
            send_instructions(scf)

    except Exception as e:
        my_debug.main("error", e)


if __name__ == '__main__':
    main()
