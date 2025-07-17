"""
Date: 16.07.2025
Author: Nelio Gautschi
Purpose:
    - Implement keyboard arrows to move the drone
"""

import time
from pynput import keyboard

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

URI = 'radio://0/80/250K/E7E7E7E7E7' #Todo: /E7... might not work

hover_value = 33000
up_value = 36000
down_value = 31000

mode = 0

def control(cf):
    if mode == -1:
        return False
    elif mode == 0:
        cf.commander.send_setpoint(0, 0, 0, hover_value)
    elif mode == 1:
        cf.commander.send_setpoint(0, 0, 0, up_value)
    elif mode == 2:
        cf.commander.send_setpoint(0, 0, 0, down_value)
    elif mode == 3:
        cf.commander.send_setpoint(-20, 0, 0, hover_value)
    elif mode == 4:
        cf.commander.send_setpoint(20, 0, 0, hover_value)

def landing():
    value = hover_value
    div = 0.9
    while value >= 0:
        for _ in range(10):
            cf.commander.send_setpoint(0, 0, 0, value)
        value = value * div
        div -= 0.2

def on_press(key):
    global mode
    try:
        if key == keyboard.Key.esc:
            mode = -1
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

def on_release(key):
    global mode
    try:
        mode = 0
    except Exception as e:
        print(f"Error: {e}")

def main():
    global mode

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    cflib.crtp.init_drivers()
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='cache')) as scf:
        while True:
            if not control(scf.cf):
                break
            time.sleep(0.1)

    listener.stop()
    landing()

if __name__ == '__main__':
    main()