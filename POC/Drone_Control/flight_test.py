"""
Date: 16.07.2025

Author: Nelio Gautschi

Purpose:
    - First flight test (drone goes up about 50 centimeters and lands)
"""

import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

import my_config
import my_debug


URI = my_config.MY_URI
HOVER_VALUE = 37000
UP_VALUE = HOVER_VALUE + 2000
DOWN_VALUE = HOVER_VALUE - 2000
SLEEP_TIME = 0.1


def simple_flight(cf):
    """
    Executes a basic flight sequence: takeoff, hover, descend, and stop.
    """

    for _ in range(10):
        cf.commander.send_setpoint(0, 0, 0, 0)
        time.sleep(SLEEP_TIME)

    for _ in range(10):
        cf.commander.send_setpoint(0, 0, 0, UP_VALUE)
        time.sleep(SLEEP_TIME)

    for _ in range(10):
        cf.commander.send_setpoint(0, 0, 0, HOVER_VALUE)
        time.sleep(SLEEP_TIME)

    for _ in range(25):
        cf.commander.send_setpoint(0, 0, 0, DOWN_VALUE)
        time.sleep(SLEEP_TIME)

    for _ in range(30):
        cf.commander.send_setpoint(0, 0, 0, 0)
        time.sleep(SLEEP_TIME)


def main():
    """
    Initializes Crazyflie connection.
    Runs the simple flight sequence.
    """

    cflib.crtp.init_drivers()

    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache="cache")) as scf:
            simple_flight(scf.cf)
    except Exception as e:
        my_debug.main("error", e)


if __name__ == "__main__":
    main()
