import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

import my_debug
import my_config

URI = my_config.MY_URI
DEFAULT_HEIGHT = 1.0
SLEEP_TIME = 1

class Controller:
    def __init__(self):
        self.enough_batt = True

    def fly(self, scf):
        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            while self.enough_batt:
                time.sleep(SLEEP_TIME)
            mc.stop()


def main():
    cflib.crtp.init_drivers()
    my_debug.main("deck")

    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache="cache")) as scf:
            cf = scf.cf

            controller = Controller()

            def log_callback(timestamp, data, logconf):
                lvl = data.get("pm.batteryLevel")
                if lvl is None:
                    return
                print(f"Battery: {lvl}%")
                if lvl <= 5:
                    controller.enough_batt = False

            logconf = LogConfig(name="Battery", period_in_ms=500)
            logconf.add_variable("pm.batteryLevel", "uint8_t")
            logconf.data_received_cb.add_callback(log_callback)
            cf.log.add_config(logconf)
            logconf.start()

            cf.platform.send_arming_request(True)
            time.sleep(1.0)

            controller.fly(cf)


    except Exception as e:
        my_debug.main("error", e)

    finally:
        try:
            logconf.stop()
        except Exception:
            pass

if __name__ == "__main__":
    main()
