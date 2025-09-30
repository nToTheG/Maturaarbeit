"""
Date: 30.09.2025

Author: Nelio Gautschi

Purpose:
    - Log the height returned by the Flow Deck V2
"""

import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig

import my_config

URI = my_config.MY_URI

class Logger:
    """
    Logger class that logs the height of the crazyflie
    """

    def __init__(self):
        self.current_height = 0.0

    def log_callback(self, _, data, __):
        """
        Logging callback function.
        """

        self.current_height = data["range.zrange"] / 1000.0

    def add_log_subs(self, scf):
        """
        Creates the height logging subscription.
        """

        log_conf = LogConfig(name='Height', period_in_ms=100)
        log_conf.add_variable('range.zrange', 'uint16_t')
        scf.cf.log.add_config(log_conf)
        log_conf.data_received_cb.add_callback(self.log_callback)
        log_conf.start()

def main():
    """
    Initializes Crazyflie connection.
    Initializes logging.
    """

    cflib.crtp.init_drivers()
    logger = Logger()

    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='cache')) as scf:
            logger.add_log_subs(scf)

            while True:
                print(f"Height: {logger.current_height} m")
                time.sleep(1.0)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
