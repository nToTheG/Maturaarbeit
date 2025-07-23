"""
Date: 16.07.2025
Author: Nelio Gautschi
Purpose:
    - First flight test (drone goes up about 50 centimetres and lands)
"""

import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

URI = 'radio://0/80/2M/E7E7E7E7E7'

hover_value = 37000
up_value = 39000
down_value = 35000
sleep_time = 0.1

def simple_connect(cf):
    for _ in range(10):
        cf.commander.send_setpoint(0, 0, 0, 0)
        time.sleep(sleep_time)

    for _ in range(10):
        cf.commander.send_setpoint(0, 0, 0, up_value)
        time.sleep(sleep_time)

    for _ in range(10):
        cf.commander.send_setpoint(0, 0, 0, hover_value)
        time.sleep(sleep_time)

    for _ in range(25):
        cf.commander.send_setpoint(0, 0, 0, down_value)
        time.sleep(sleep_time)

    for _ in range(30):
        cf.commander.send_setpoint(0, 0, 0, 0)
        time.sleep(sleep_time)

def main():
    cflib.crtp.init_drivers()
    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='cache')) as scf:
            simple_connect(scf.cf)
    except Exception as e:
        print("❌ Exception:", e)

if __name__ == '__main__':
    main()