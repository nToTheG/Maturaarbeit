"Author: Nelio Gautschi"

import time

class Stopwatch:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.timeout = 5

    def reset(self): # Setze die Stopuhr zurück
        self.start_time = time.perf_counter()

    def safety_check(self, mc): # Überprüfe, ob t=5 erreicht wurde
        if time.perf_counter() - self.start_time >= self.timeout:
            mc.stop() # Lande die Crazyflie
