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

HOVER_VALUE = 36000
UP_VALUE = 39000
DOWN_VALUE = 31000

def wait_for_param_download(cf):
    while not cf.param.is_updated:
        time.sleep(SLEEP_TIME)

def control(cf):
    if mode == 0:
        cf.commander.send_setpoint(0, 0, 0, HOVER_VALUE)
    elif mode == 1:
        for _ in range(10):
            cf.commander.send_setpoint(0, 0, 0, UP_VALUE)
            time.sleep(SLEEP_TIME)
    elif mode == 2:
        cf.commander.send_setpoint(0, 0, 0, DOWN_VALUE)
    elif mode == 3:
        cf.commander.send_setpoint(-5, 0, 0, HOVER_VALUE)
    elif mode == 4:
        cf.commander.send_setpoint(5, 0, 0, HOVER_VALUE)
    else:
        pass

def landing(cf):
    print("Landing process initiated...")
    for _ in range(10):
        cf.commander.send_setpoint(0, 0, 0, HOVER_VALUE)
        time.sleep(SLEEP_TIME)
    
    cf.commander.send_stop_setpoint()
    print("Landed.")

def on_press(key):
    global mode, stop
    try:
        if key == keyboard.Key.esc:
            print("Exc pressed")
            stop = True
        elif key == keyboard.Key.up:
            mode = 1
        elif key == keyboard.Key.down:
            mode = 2
        elif key == keyboard.Key.left:
            mode = 3
        elif key == keyboard.Key.right:
            mode = 4
    except Exception as e:
        print(f"Error: {e}")
        sys.exit()

def on_release(key):
    global mode
    mode = 0

def main():
    cflib.crtp.init_drivers()
    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='cache')) as scf:
            wait_for_param_download(scf.cf)
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