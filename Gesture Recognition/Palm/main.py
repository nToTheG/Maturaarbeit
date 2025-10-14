"""
Date: 13.10.2025

Autor: Nelio Gautschi

Purpose:

"""

import sys
import time
import math

import cv2
#import cflib.crtp
#from cflib.crazyflie import Crazyflie
#from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
#from cflib.positioning.motion_commander import MotionCommander

import config
import debug


class DroneController:
    def __init__(self):
        self.flying = True

    def send_instructions(self, mc, direction):
        """
        Sends a movement setpoint to Crazyflie based on current key input.
        """

        if self.flying is False:
            mc.stop()

        elif direction:
            if direction == "left":
                mc.start_turn_left(config.V_YAW)

            elif direction == "right":
                mc.start_turn_right(config.V_YAW)

            elif direction == "down":
                mc.start_down(config.V_ALT)

            elif direction == "up":
                mc.start_up(config.V_ALT)

            elif direction == "backward":
                mc.start_back(config.V_HOR)

            elif direction == "forward":
                mc.start_forward(config.V_HOR)

        else:
            mc.start_linear_motion(0, 0, 0, rate_yaw=0.0)

        time.sleep(0.1)

class TagEvaluater:
    """
    - Makes a snapshot of the distances between the markers and their sizes
    - Determines the tilt of the hand compared to the snapshot
    """

    def __init__(self):
        self.ids = None
        self.tags = []
        self.calibrated = False
        self.distance_snapshot = (None, None)
        self.distance = None
        self.area_snapshot = None
        self.area = None

    def determine_tilt(self):
        d_ss = self.distance_snapshot
        d = self.distance
        id_ss = self.area_snapshot[1]

        if d_ss[0]/d[0] > d_ss[1]/d[1] + config.V_DZ:
            if self.area[self.ids.index(2)] < self.area_snapshot[0][id_ss.index(2)]:
                return "right"
            return "left"

        if d_ss[0]/d[0] < d_ss[1]/d[1] - config.H_DZ:
            if self.area[self.ids.index(1)] > self.area_snapshot[0][id_ss.index(1)]:
                return "forwards"
            return "backwards"

        return "hover"

    def get_distance(self, id1, id2):
        tag1 = self.tags[self.ids.index(id1)]
        tag2 = self.tags[self.ids.index(id2)]
        vector1 = self.middle_point(tag1)
        vector2 = self.middle_point(tag2)
        distance = self.vector_subtraction(vector1, vector2)
        return distance

    def middle_point(self, tag):
        sx = sum(corner[0] for corner in tag)
        sy = sum(corner[1] for corner in tag)
        mx = sx / 4
        my = sy / 4
        return (mx, my)

    def vector_subtraction(self, v1, v2):
        v3 = (v1[0] - v2[0], v1[1] - v2[1])
        d = math.sqrt(v3[0]**2 + v3[1]**2)
        return d

    def shoelace_formula(self):
        """
        Function that uses the Shoelace formula.
        Shoelace formula: calculates the area of any quadrilateral.
        """

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

    def numpy_to_2d(self, tags):
        """ 
        Converts the corners from NumPy-Arrays into a 2D-Arrays.
        """

        self.tags = []
        for i in range(len(self.ids)):
            tag_as_2d_array = []
            for corner in tags[i][0]:
                x, y = corner
                tag_as_2d_array.append((x, y))

            self.tags.append(tag_as_2d_array)

    def make_snapshot(self, tags, ids):
        if all(_id in ids for _id in config.USED_TAGS):
            _ = self.update(tags, ids)
            self.distance_snapshot = self.distance
            self.area_snapshot = (self.area, self.ids)
            self.calibrated = True

    def update(self, tags, ids):
        """
        Updates variables and executes formatting and calculating functions.
        """

        self.ids = [_id[0] for _id in ids]
        self.numpy_to_2d(tags)
        self.area = self.shoelace_formula()
        self.distance = (self.get_distance(1, 2), self.get_distance(4, 1))
        if self.calibrated:
            return self.determine_tilt()
        return None


class Stopwatch:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.timeout = 5

    def reset(self):
        """
        Reset the timer.
        """

        self.start_time = time.perf_counter()

    def safety_check(self, controller):
        """
        Switch the flight control mode.
        """

        if time.perf_counter() - self.start_time >= self.timeout:
            controller.flying = False


class Camera:
    def __init__(self):
        self.cam = None
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(config.MY_ARUCO_DICT)
        self.parameters = cv2.aruco.DetectorParameters()

    def open_cam(self):
        self.cam = cv2.VideoCapture(0)
        if not self.cam.isOpened():
            raise IOError("Cannot open camera")

    def close_cam(self):
        self.cam.release()

    def process_frame(self):
        """
        Reads camera feed.
        Determines flight mode.
        Displays camera feed.
        """

        success, frame = self.cam.read()
        if not success:
            print("Cannot receive frame (stream end?). Exiting ...")
            sys.exit()

        detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray_frame)

        return frame, corners, ids


def calibrate(te, cam):
    add_text = ""
    while not te.calibrated:
        frame, corners, ids = cam.process_frame()
        if cv2.waitKey(1) == ord("s"):
            te.make_snapshot(corners, ids)
            if add_text == "":
                add_text = " (Try again)"
        show_feed(None, None, config.frame_text(frame, add_text))

def main():
    """
    Executes main loop.
    """

    cam = Camera()
    cam.open_cam()
    sw = Stopwatch()
    te = TagEvaluater()
    controller = DroneController()

    calibrate(te, cam)

    try:
        while True:
            if cv2.waitKey(1) == ord('q'):
                break

            frame, corners, ids = cam.process_frame()
            if ids is not None:
                if all(_id in ids for _id in config.USED_TAGS):
                    sw.reset()
                    direction = te.update(corners, ids)
                    print(direction)
                else:
                    sw.safety_check(controller)
            else:
                sw.safety_check(controller)

            show_feed(corners, ids, frame)

    except Exception as e:
        debug.main("error", e)

    finally:
        cam.close_cam()
        cv2.destroyAllWindows()
        sys.exit()

def show_feed(corners, ids, feed_frame):
    flipped_frame = feed_frame
    if ids is not None and len(ids) != 0:
        for i, _ in enumerate(ids.flatten()):
            for corner in corners[i][0]:
                x, y = corner
                painted_frame = cv2.circle(
                    feed_frame,
                    (int(x), int(y)),
                    radius=5,
                    color=(0, 0, 255),
                    thickness=-1)
                flipped_frame = cv2.flip(painted_frame, 1)
    else:
        flipped_frame = cv2.flip(feed_frame, 1)
    cv2.imshow("Camera Feed", flipped_frame)

if __name__ == "__main__":
    main()
