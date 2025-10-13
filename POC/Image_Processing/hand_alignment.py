"""
Date: 02.10.2025

Autor: Nelio Gautschi

Purpose:

"""

import sys
import time

import cv2

import my_config2


aliases = {
    "auto": "### AUTONOMOUS FLIGHT ###",
    "live": "### LIVE CONTROL ###",
}


class TagEvaluater:
    def __init__(self):
        self.ids = None
        self.tags = []

    def _sum(self, areas):
        A_OL = areas[self.ids.index(1)]
        A_OR = areas[self.ids.index(2)]
        A_UR = areas[self.ids.index(3)]
        A_UL = areas[self.ids.index(4)]

        S_O = A_OR + A_OL
        S_U = A_UR + A_UL
        S_R = A_OR + A_UR
        S_L = A_OL + A_UL

        Q_OU = (max(S_O, S_U)) / (min(S_O, S_U))
        Q_RL = (max(S_R, S_L)) / (min(S_R, S_L))

        if Q_OU < Q_RL - my_config2.V_DZ:
            if S_R > S_L:
                return "rechts"
            return "links"
        if Q_RL < Q_OU - my_config2.H_DZ:
            if S_O > S_U:
                return "vorwärts"
            return "rückwärts"
        return "hover"

    def scale(self, areas):
        scaled_areas = []
        for area in areas:
            scaled_area = area**2
            scaled_areas.append(scaled_area)
        return scaled_areas

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

        return self.tags

    def update(self, tags, ids):
        """
        Updates variables and executes formatting and calculating functions.
        """

        self.ids = [_id[0] for _id in ids]
        self.numpy_to_2d(tags)
        areas = self.shoelace_formula()
        scaled_areas = self.scale(areas)
        x = self._sum(scaled_areas)
        print(x)



class Stopwatch:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.timeout = 5
        self.mode = "auto"

    def reset(self):
        """
        Reset the timer.
        """

        self.start_time = time.perf_counter()
        self.mode = "live"

    def safety_check(self):
        """
        Switch the flight control mode.
        """

        if time.perf_counter() - self.start_time >= self.timeout:
            self.mode = "auto"


class Camera:
    def __init__(self):
        self.cam = None
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(my_config2.MY_ARUCO_DICT)
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

        return gray_frame, corners, ids


def main():
    """
    Executes main loop.
    """

    cam = Camera()
    cam.open_cam()
    sw = Stopwatch()
    te = TagEvaluater()

    try:
        while True:
            if cv2.waitKey(1) == ord("q"):
                break
            frame, corners, ids = cam.process_frame()
            draw_detected_markers(corners, ids, frame)
            if ids is not None:
                if all(_id in my_config2.USED_TAGS for _id in ids) and len(ids) == 4:
                    sw.reset()
                    te.update(corners, ids)
                else:
                    sw.safety_check()
            else:
                sw.safety_check()
    finally:
        cam.close_cam()
        cv2.destroyAllWindows()

def draw_detected_markers(corners, ids, feed_frame):
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
