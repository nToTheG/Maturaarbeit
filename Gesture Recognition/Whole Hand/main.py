"""
Date: 14.10.2025

Autor: Nelio Gautschi

Purpose:

"""

import sys
import time
import math

import cv2
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

import config
import debug


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
            - vx is for back/forth
            - va is for left/right
            - vz is for up/down
        """

        vx, va, vz,  = velocities
        self.mc.start_linear_motion(vx, 0, vz, rate_yaw=va)

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


class TagEvaluater:
    """
    Handles all the image and aruco tag processing.
    """

    def __init__(self):
        self.ids = None
        self.tags = []
        self.calibrated = False
        self.distance_snapshot = (None, None)
        self.distance = None
        self.area_snapshot = None

    def determine_tilt(self):
        vx, vz, va = 0, 0, 0

        d = self.distance
        d_ss = self.distance_snapshot

        a = self._shoelace_formula()
        areas = dict(zip(self.ids, a))
        areas_ss = self.area_snapshot

        if d_ss[0]/d[0] > d_ss[1]/d[1] + config.V_DZ: # y-axis yaw detecked
            if areas[3] > areas[1]: # yaw to the right
                if areas[3] > areas_ss[3]: # left closer to screen than snapshot
                    va = config.VA

            elif areas[1] > areas[3]: # yaw to the left
                if areas[1] > areas_ss[1]: # right closer to screen than snapshot
                    va = -config.VA

        if d_ss[1]/d[1] > d_ss[0]/d[0] + config.H_DZ: # x-axis tilt detecked
            if areas[2] > areas[4]: # forwards-tilt
                if areas[2] > areas_ss[2]: # top closer to screen than snapshot
                    vx = config.VX

            elif areas[4] > areas[2]: # backward-tilt
                vx = -config.VX

        return (vx, va, vz)

    def _get_distance(self, id1, id2):
        tag1 = self.tags[self.ids.index(id1)]
        tag2 = self.tags[self.ids.index(id2)]
        vector1 = self._get_middle(tag1)
        vector2 = self._get_middle(tag2)
        distance = self._vector_subtraction(vector1, vector2)
        return distance

    def _get_middle(self, tag):
        sx = sum(corner[0] for corner in tag)
        sy = sum(corner[1] for corner in tag)
        mx = sx / 4
        my = sy / 4
        return (mx, my)

    def _vector_subtraction(self, v1, v2):
        v3 = (v1[0] - v2[0], v1[1] - v2[1])
        d = math.sqrt(v3[0]**2 + v3[1]**2)
        return d

    def _shoelace_formula(self):
        areas = []
        for tag in self.tags:
            x1, y1 = tag[0]
            x2, y2 = tag[1]
            x3, y3 = tag[2]
            x4, y4 = tag[3]

            area = 0.5 * abs(
                (x1*y2 + x2*y3 + x3*y4 + x4*y1) -
                (y1*x2 + y2*x3 + y3*x4 + y4*x1))

            areas.append(area)

        return areas

    def _numpy2list(self, tags):
        self.tags = []
        for i in range(len(self.ids)):
            tag_as_2d_array = []
            for corner in tags[i][0]:
                x, y = corner
                tag_as_2d_array.append((x, y))

            self.tags.append(tag_as_2d_array)

    def make_snapshot(self, tags, ids, cam):
        """
        Initiates the calibration process.
        Safes a snapshot of the data.
        """

        if ids is not None and all(_id in ids for _id in config.USED_TAGS):
            _ = self.update(tags, ids)
            self.distance_snapshot = self.distance
            areas = self._shoelace_formula()
            self.area_snapshot = dict(zip(self.ids, areas))
            self.calibrated = True
            reference_marker = self.tags[self.ids.index(4)]
            tl = reference_marker[0]
            br = reference_marker[2]
            k = 10
            start_point = (int(tl[0] - k), int(tl[1] - k))
            end_point = (int(br[0] + k), int(br[1] + k))
            cam.reference = [start_point, end_point]

    def update(self, tags, ids):
        """
        Updates variables.
        Executes formatting and calculating functions.
        Returns the calculated velocity tuple.
        """

        self.ids = [_id[0] for _id in ids]
        self._numpy2list(tags)
        self.distance = (self._get_distance(1, 3), self._get_distance(2, 4))
        if self.calibrated:
            return self.determine_tilt()
        return None


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


class Camera:
    """
    Handles the camera and the aruco detection.
    """

    def __init__(self):
        self.cam = None
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(config.MY_ARUCO_DICT)
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

        if not te.calibrated:
            now = time.perf_counter()
            if cv2.waitKey(1) == ord("s"):
                setpoint = now
            if cv2.waitKey(1) == ord("q"):
                sys.exit()

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

        cam.show_feed(corners, ids, config.draw_text(frame, mode))

def main():
    """
    Initiates all the classes.
    Catches errors.
    Connects to crazyflie with the MotionCommander
    """

    cam = Camera()
    sw = Timer()
    te = TagEvaluater()
    controller = DroneController()

    calibrate(te, cam)

    cflib.crtp.init_drivers()
    debug.main("deck")
    try:
        cam.open_cam()
        sw.reset()
        with SyncCrazyflie(config.MY_URI, cf=Crazyflie(rw_cache="cache")) as scf:
            scf.cf.platform.send_arming_request(True)
            time.sleep(1.0)
            with MotionCommander(scf, default_height=config.DEFAULT_HEIGHT) as mc:
                cam.open_cam()
                sw.reset()
                while controller.flying:
                    if cv2.waitKey(1) == ord("q"):
                        cam.close_cam()
                        break

                frame, corners, ids = cam.process_frame()

                if ids is not None and all(_id in ids for _id in config.USED_TAGS):
                    sw.reset()
                    direction = te.update(corners, ids)
                else:
                    direction = (0, 0, 0)
                    sw.safety_check(controller, cam)

                controller.determine_state(mc, direction)
                cam.show_feed(corners, ids, frame)

    except Exception as e:
        debug.handle_error(e)


if __name__ == "__main__":
    main()
