"""
Date: 02.10.2025

Autor: Nelio Gautschi

Purpose:
    - Get camera feed
    - Detect corners of ArUco tags in camera feed
    - Draw the corners as red circles on the displayed feed
    - Look for ArUco tag 0 in feed
    - If found: live control, if not: autonomous flight
    - ArUco tag 0 has to be gone for more than sw.timeout to count as gone
    - Show the current control mode on screen

Corner order in 'tag' list:
    (1)--a--(2)
     |       |
     d       b
     |       |
    (4)--c--(3)
"""

import sys
import time
import math

import cv2

import my_config2


USED_TAGS = my_config2.USED_TAGS

aliases = {
    "auto": "### AUTONOMOUS FLIGHT ###",
    "live": "### LIVE CONTROL ###",
}


class TagEvaluater:
    def __init__(self):
        self.ids = None
        self.ids_h = None
        self.raw_tags = None
        self.tags = []
        self.tags_as_areas = []
        self.tilt = "neutral"


    def shoelace_area(self):
        """
        Function that uses the Shoelace formula.
        Shoelace formula: calculates the area of any quadrilateral.
        """

        self.format_tags()
        self.tags_as_areas = []
        for tag in self.tags:
            print(tag)
            x1, y1 = tag[0]
            x2, y2 = tag[1]
            x3, y3 = tag[2]
            x4, y4 = tag[3]

            area = 0.5 * abs(
                (x1*y2 + x2*y3 + x3*y4 + x4*y1) -
                (y1*x2 + y2*x3 + y3*x4 + y4*x1))

            self.tags_as_areas.append(area)

    def format_tags(self):
        """ 
        Converts the given corners into a more readable format.
        """

        tag_coords = []

        self.ids_h = [id[0] for id in self.ids]
        for i in range(len(self.ids_h)):
            for corner in self.raw_tags[i][0]:
                x, y = corner
                tag_coords.append((x, y))

            self.tags.append(tag_coords)
            tag_coords = []

        return self.tags

    def main(self, ids, tags):
        if ids is not None and all(_id in USED_TAGS for _id in ids):
            self.ids_h = None
            self.tags = []
            self.ids = ids
            self.raw_tags = tags
            self.shoelace_area()
            return True
        return False



class Stopwatch:
    """
    Tracks control mode and tag 0 timeout.
    """

    def __init__(self):
        self.start_time = time.perf_counter()
        self.timeout = 1.5
        self.mode = "auto"

    def reset(self):
        """
        Reset the timer.
        """

        self.start_time = time.perf_counter()
        self.mode = "live"

    def switch_mode(self):
        """
        Switch the flight control mode.
        """

        if time.perf_counter() - self.start_time >= self.timeout:
            self.mode = "auto"


def process_frame(cam, sw):
    """
    Reads camera feed.
    Determines flight mode.
    Displays camera feed.
    """

    if cv2.waitKey(1) == ord("q"):
        sys.exit()

    success, frame = cam.read()
    if not success:
        print("Cannot receive frame (stream end?). Exiting ...")
        sys.exit()

    aruco_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detect_markers(aruco_frame)

    if ids is not None:
        id_list = [x for row in ids for x in row]
        if 0 in id_list:
            sw.reset()
        else:
            sw.switch_mode()
    else:
        sw.switch_mode()

    return frame, ids, corners


def detect_markers(aruco_frame):
    """
    Detects ArUco markers.
    """

    aruco_dict = cv2.aruco.getPredefinedDictionary(my_config2.MY_ARUCO_DICT)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    return detector.detectMarkers(aruco_frame)


def modify_frame(feed_frame, sw, te, tags_detecked):
    """
    Draws detected corners onto the frame.
    Draw current control mode onto the frame.
    """

    if tags_detecked:
        tags = te.tags
        for tag in tags:
            for corner in tag:
                x, y = corner
                feed_frame = cv2.circle(
                    feed_frame,
                    (int(x), int(y)),
                    radius=5,
                    color=(0, 0, 255),
                    thickness=-1)

    flipped_frame = cv2.flip(feed_frame, 1)

    mode_string = str(aliases[sw.mode])
    (text_w, text_h), _ = cv2.getTextSize(mode_string, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    pos_x = (flipped_frame.shape[1] - text_w) // 2
    pos_y = text_h + 10

    cv2.putText(
        flipped_frame,
        mode_string,
        (pos_x, pos_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
        )

    direction_string = str(te.tilt)
    (text_w, text_h), _ = cv2.getTextSize(direction_string, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    pos_x = (flipped_frame.shape[1] - text_w) // 2
    pos_y = flipped_frame.shape[0] - text_h - 10

    cv2.putText(
        flipped_frame,
        direction_string,
        (pos_x, pos_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 100, 100),
        2
        )


    cv2.imshow("Camera Feed", flipped_frame)


def main():
    """
    Opens camera.
    Executes main loop.
    """

    sw = Stopwatch()
    te = TagEvaluater()

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise IOError("Cannot open camera.")

    tags_detecked = False
    try:
        while True:
            frame, ids, raw_corners = process_frame(cam, sw)
            tags_detecked = te.main(ids, raw_corners)
            modify_frame(frame, sw, te, tags_detecked)
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
