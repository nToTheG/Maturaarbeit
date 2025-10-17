"""
Date: 14.10.2025

Author: Nelio Gautschi

Purpose:
    - Stores project-wide classes, constants and functions
"""

import time
import sys

import cv2


MY_ARUCO_DICT = cv2.aruco.DICT_4X4_50
USED_TAGS = [1, 2, 3, 4]
MY_URI = "radio://0/80/2M/E7E7E7E7E7"

DEFAULT_HEIGHT = 0.5

T_DZ = 0.06
A_DZ = 100
Y_DZ = 0.01

VT = 0.5 # tilt (forward/backward) velocity
VA = 0.2 # altitude (up/down) velocity
VY = 30 # yaw (right/left) velocity

my_exceptions = {
    f"No driver found or malformed URI: {MY_URI}": "❌ Crazyradio not plugged in.",
    "Could not load link driver: Cannot find a Crazyradio Dongle": "❌ Crazyradio not plugged in.",
    "Too many packets lost": "❌ Crazyflie not turned on."
}


class DroneController:
    """
    Drone controller class.
    Stores a value on if the drone should be flying.
    Sends movement instructions.
    """
    def __init__(self):
        self.flying = True
        self.mc = None

    def land(self):
        """
        Landing function; lands the drone safely if hand has gone undetecked for too long
        """

        self.mc.stop()

    def send_instructions(self, velocities):
        """
        Starts a linear motion with the velocities:
            - v_til is for back/forth
            - v_yaw is for left/right
            - v_alt is for up/down
        """

        v_til, v_alt, v_yaw = velocities
        self.mc.start_linear_motion(v_til, 0, v_alt, rate_yaw=v_yaw)

        time.sleep(0.1)

    def determine_state(self, mc, velocities):
        """
        Calls functions based on whether the drone should stay in air.
        """

        self.mc = mc
        if self.flying is False:
            self.land()
        else:
            self.send_instructions(velocities)


class Camera:
    """
    Handles the camera and the aruco detection.
    """

    def __init__(self):
        self.cam = None
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(MY_ARUCO_DICT)
        self.parameters = cv2.aruco.DetectorParameters()
        self.reference = []

    def open_cam(self, index=0): # 0 for built-in camera
        """
        Opens the camera safely
        """

        self.cam = cv2.VideoCapture(index)
        if not self.cam.isOpened():
            raise IOError("Cannot open camera")

    def close_cam(self):
        """
        Closes the camera and destroys GUI.
        """

        self.cam.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    def process_frame(self):
        """
        Reads camera feed (ends script if feed is unsubscriptable).
        Creates detector instance.
        Converts feed to grayscale for better detection results.
        Returns important data.
        """

        success, frame = self.cam.read()
        if not success:
            print("Cannot receive frame (stream end?). Exiting ...")
            sys.exit()

        detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray_frame)

        return frame, corners, ids

    def show_feed(self, corners, ids, feed_frame):
        """
        Draws the reference marker onto camera feed.
        Draws detected corners of aruco tags onto feed.
        Displays feed.
        """

        if self.reference:
            tl = self.reference[0]
            br = self.reference[1]
            cv2.rectangle(feed_frame, tl, br, (0, 0, 255), 2)

        if ids is not None and len(ids) != 0:
            for i, _ in enumerate(ids.flatten()):
                for corner in corners[i][0]:
                    x, y = corner
                    feed_frame = cv2.circle(
                        feed_frame.copy(),
                        (int(x), int(y)),
                        radius=5,
                        color=(0, 0, 255),
                        thickness=-1)

        cv2.imshow("Camera Feed", cv2.flip(feed_frame, 1))


class Timer:
    """
    Imitates timer functionality.
    """

    def __init__(self, timeout=5):
        self.start_time = time.perf_counter()
        self.t = timeout

    def reset(self):
        """
        Starts and resets a timer.
        """

        self.start_time = time.perf_counter()

    def safety_check(self, controller, cam):
        """
        Compares the difference of the current time and when the timer started.
        Initiates the landing process of the drone if timeout was reached.
        """

        if time.perf_counter() - self.start_time >= self.t:
            controller.flying = False
            cam.close_cam()


def calibrate(te, cam):
    """
    Runs calibration process of the hand.
    Calls draw_text() function from custom config module.
    Displays the animation and text on feed.
    """

    setpoint = 5
    cam.open_cam()
    mode = None

    while True:
        frame, corners, ids = cam.process_frame()
        mode = [3, 4]

        if cv2.waitKey(1) == ord("q"):
            sys.exit()

        if not te.calibrated:
            now = time.perf_counter()
            if cv2.waitKey(1) == ord("s"):
                setpoint = now

            if now - setpoint < 4:
                if now - setpoint < 3:
                    te.make_snapshot(corners, ids, cam)
                    mode = [1]
                else:
                    mode = [2]
        else:
            mode = [5]

        if mode == [5]:
            cam.close_cam()
            break

        cam.show_feed(corners, ids, draw_text(frame, mode))


def draw_text(frame, mode):
    """
    Draws text and animations based on current state of the calibration process.
    """

    flipped_frame = cv2.flip(frame, 1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    blue = (200, 0, 0)

    lines = [
        (f"Calibrating{'.' * ((int(time.time() / 0.75) % 3) + 1)}", (0, 255, 0), 2),
        ("Failed. Try again.", (0, 0, 255), 2),
        ("Position your hand 20cm away from the camera in the middle of the screen.", blue, 2),
        ("Press 's' when you see red dots on all tag corners.", blue, 1)
    ]

    y_offset = 10

    for _, i in enumerate(mode):
        text, color, thickness = lines[i-1]
        text_size = cv2.getTextSize(text, font, 1.0, thickness)[0]
        x = (flipped_frame.shape[1] - text_size[0]) // 2
        y = y_offset + text_size[1]
        cv2.putText(flipped_frame, text, (x, y), font, 1.0, color, thickness)
        y_offset = y + 10

    return cv2.flip(flipped_frame, 1)
