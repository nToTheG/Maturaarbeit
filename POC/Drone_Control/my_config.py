my_uri = "radio://0/80/2M/E7E7E7E7E7"

my_exceptions = {
    f"No driver found or malformed URI: {my_uri}": "❌ Crazyradio not plugged in.", 
    "Couldn't load link driver: Cannot find a Crazyradio Dongle": "❌ Crazyradio not plugged in.", 
    "Too many packets lost": "❌ Crazyflie not turned on."
}