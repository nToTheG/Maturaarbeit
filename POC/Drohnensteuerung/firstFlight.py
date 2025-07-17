"""
Date: 16.07.2025
Author: Nelio Gautschi
Purpose:
    - First flight test
"""

import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

URI = 'radio://0/80/250K/E7E7E7E7E7' #Todo: /E7... might not work

hover_value = 33000
up_value = 36000

def simple_connect(cf):
    if up_value <= 38000: # safety check
        cf.commander.send_setpoint(0, 0, 0, 0) # unlock motors by sending zero thrust
        time.sleep(0.05)

        for _ in range(40):
            cf.commander.send_setpoint(0, 0, 0, up_value)
            time.sleep(0.05)
            cf.commander.send_setpoint(0, 0, 0, up_value)
            time.sleep(0.05)

        for _ in range(20):
            cf.commander.send_setpoint(0, 0, 0, hover_value)
            time.sleep(0.05)
            cf.commander.send_setpoint(0, 0, 0, hover_value)
            time.sleep(0.05)

        cf.commander.send_setpoint(0, 0, 0, 0) #Todo: either here
        cf.commander.send_stop_setpoint() # stop motors
        cf.commander.send_setpoint(0, 0, 0, 0) #Todo: or here


def main():
    cflib.crtp.init_drivers()
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='cache')) as scf:
        simple_connect(scf.cf)

if __name__ == '__main__':
    main()