"""
Date: 16.07.2025

Author: Nelio Gautschi

Purpose:
This module serves two main purposes:
    - Checks if the Flowdeck V2 is attached to the Crazyflie
    - Maps know error messages to user-friendly output

If executed directly, it will:
    - Return all available Crazyflie URIs
"""

import sys
import time
from threading import Event

import cflib.crtp
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie import Crazyflie

import my_config


URI = my_config.MY_URI
EXCEPTIONS = my_config.my_exceptions
ERROR_END = "-----------------------------------------------------"


def get_uri():
    """
    Scans for all available interfaces.
    Prints the URIs that can be used to connect.
    """

    print("🔍 Scanning interfaces for Crazyflies...")
    available = cflib.crtp.scan_interfaces()

    if not available:
        print("❌ No Crazyflies found.")
    else:
        print("✅ Available Crazyflie URIs:")
        for uri, _ in available:
            print(f"    - {uri} -")


def detect_deck():
    """
    Checks if the Flowdeck V2 is attached to the Crazyflie.
    """

    print("🔍 Scanning interfaces for Decks...")

    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache="cache")) as scf:
            scf.cf.param.add_update_callback(
                group="deck",
                name="bcFlow2",
                cb=param_deck_flow)
            time.sleep(1)

    except Exception as e:
        handle_error(e)


def param_deck_flow(_, value_str):
    """
    Callback to handle the deck detection result based on parameter value.
    """

    deck_attached_event = Event()
    value = int(value_str)

    if value:
        deck_attached_event.set()
        print("✅ Deck is attached!")
    else:
        print("❌ Deck is NOT attached!")
        print(ERROR_END)
        sys.exit(1)


def handle_error(e):
    """
    Handles known exceptions by replacing know error messages with user-friendly ones.
    """

    for error_message, user_friendly_message in EXCEPTIONS.items():
        if error_message in str(e):
            print(user_friendly_message)
            print(ERROR_END)
            sys.exit(1)


def main(*mode):
    """
    Initializes Crazyflie drivers.
    Runs the selected mode with optional arguments.
    """

    cflib.crtp.init_drivers()

    func = MODES[mode[0]]
    args = mode[1:]
    func(*args)


MODES = {
    "uri": get_uri,
    "deck": detect_deck,
    "error": handle_error
}

if __name__ == "__main__":
    main("uri")
