"""
Date: 16.07.2025
Author: Nelio Gautschi
Purpose:
    - Debug script that can be used (manually or as import) for multiple things: 
    - Mode = "uri": Scans for all available interfaces, prints the URIs that can be used to connect
    - Mode = "deck": Scans for decks
"""
import my_config

import sys
import time
from threading import Event

import cflib.crtp
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie import Crazyflie

# START OF "uri"
def GET_URI():
    print("🔍 Scanning interfaces for Crazyflies...")
    available = cflib.crtp.scan_interfaces()

    if not available:
        print("❌ No Crazyflies found.")
    else:
        print("✅ Available Crazyflies:")
        for uri, desc in available:
            print(f"    {uri} - {desc}")
# END OF "uri"

# START OF "deck"
def DETECT_DECK():
    print("🔍 Scanning interfaces for Decks...")
    URI = my_config.my_uri
    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='cache')) as scf:
            scf.cf.param.add_update_callback(
                group="deck", 
                name="bcFlow2", 
                cb=param_deck_flow)
            time.sleep(1)

    except Exception as e:
        error_handling(e)

def error_handling(e):
    for error_message in EXCEPTIONS:
        if error_message in str(e):
            print(EXCEPTIONS[error_message])
            print(ERROR_END)
            sys.exit(1)

def param_deck_flow(_, value_str):
    deck_attached_event = Event()
    value = int(value_str)
    if value:
        deck_attached_event.set()
        print("✅ Deck is attached!")
    else:
        print("❌ Deck is NOT attached!")
        print(ERROR_END)
        sys.exit(1)
# END OF "deck"

MODES = {
    "uri": GET_URI, 
    "deck": DETECT_DECK
}

MODE = "deck" # change for manual use!

EXCEPTIONS = my_config.my_exceptions

ERROR_END = "-----------------------------------------------------"

def main(mode):
    cflib.crtp.init_drivers()
    MODES[mode]()

if __name__ == '__main__':
    main(MODE)