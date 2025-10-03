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

from my_config2 import MY_ARUCO_DICT


aliases = {
    "auto": "### AUTONOMOUS FLIGHT ###",
    "live": "### LIVE CONTROL ###",
}


class TagEvaluater:
    def __init__(self):
        self.ids = None
        self.tags = []
        self.allignment = "neutral"

    def get_allignment(self):

        formatted_tags = self.get_side_length()
        if len(formatted_tags) == 1:
            formatted_tag = formatted_tags[0]

            forward = formatted_tag[0] / formatted_tag[2]
            backward = formatted_tag[2] / formatted_tag[0]
            right = formatted_tag[1] / formatted_tag[3]
            left = formatted_tag[3] / formatted_tag[1]
            directions = {
                forward: "forward",
                backward: "backward",
                right: "right",
                left: "left"
            }
            most_tilt = max(forward, backward, right, left)
            if most_tilt < 1.1:
                self.allignment = "neutral"
            else:
                self.allignment = directions[most_tilt]
        else:
            self.allignment = "neutral"


    def get_side_length(self):
        """
        Convert the 4 points of each tag in 4 sides going from each corner to the next.
        """

        tags_as_sides = []
        for tag in self.tags:
            tag_as_sides = []
            for i in range(4):
                tag_as_sides.append(math.dist(tag[i], tag[(i+1) % 4]))
            tags_as_sides.append(tag_as_sides)

        return tags_as_sides

    def format_tags(self, corners):
        """ 
        Converts the given corners into a more readable format
        """

        self.tags = []
        tag_coords = []
        if self.ids is not None:
            for i, _ in enumerate(self.ids.flatten()):
                for corner in corners[i][0]:
                    x, y = corner
                    tag_coords.append((x, y))
                self.tags.append(tag_coords)
                tag_coords = []

    def main(self, ids, tags):
        self.ids = ids
        self.format_tags(tags)
        self.get_allignment()
        return self.tags



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

    aruco_dict = cv2.aruco.getPredefinedDictionary(MY_ARUCO_DICT)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    return detector.detectMarkers(aruco_frame)


def modify_frame(feed_frame, corners, sw, te):
    """
    Draws detected corners onto the frame.
    Draw current control mode onto the frame.
    """

    if corners is not None:
        for tag in corners:
            for i, corner in enumerate(tag):
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

    direction_string = str(te.allignment)
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

    try:
        while True:
            frame, ids, raw_corners = process_frame(cam, sw)
            tags = te.main(ids, raw_corners)
            modify_frame(frame, tags, sw, te)
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
