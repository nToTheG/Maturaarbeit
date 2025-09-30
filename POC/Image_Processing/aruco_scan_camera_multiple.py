"""
Date: 29.09.2025

Autor: Nelio Gautschi

Purpose:
    - Get camera feed
    - Detect corners of ArUco tags in camera feed
    - Draw the corners as red circles on the displayed feed
    - Look for ArUco tag 0 in feed
    - If found: live control, if not: autonomous flight
    - ArUco tag 0 has to be gone for more than Clock.timeout to count as gone
    - Show the current control mode on screen
"""

import sys
import time

import cv2

from my_config2 import MY_ARUCO_DICT


aliases = {
    "active": "### AUTONOMOUS FLIGHT ###",
    "inactive": "### LIVE CONTROL ###",
}

class Clock:
    """
    Tracks control mode and tag 0 timeout.
    """

    def __init__(self):
        self.now = time.time()
        self.steady_mode = "active"
        self.last_seen = time.time()
        self.timeout = 1.5

    def check_timeout(self):
        """
        Check if ArUco tag has been gone for more than timeout
        """

        if self.steady_mode == "inactive":
            if self.now - self.last_seen >= self.timeout:
                self.steady_mode = "active"

    def main(self, tag_found):
        """
        Update current time.
        Determine if timeout checks must happen.
        """

        self.now = time.time()

        if tag_found:
            self.last_seen = self.now
            if self.steady_mode == "active":
                self.steady_mode = "inactive"
        else:
            self.check_timeout()

def process_frame(cam, clock):
    """
    Reads camera feed.
    Determines flight mode.
    Displays camera feed.
    """

    success, frame = cam.read()
    if not success:
        print("Cannot receive frame (stream end?). Exiting ...")
        sys.exit()

    aruco_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detect_markers(aruco_frame)

    if ids is not None:
        id_list = [x for row in ids for x in row]
        if 0 in id_list:
            clock.main(True)
        else:
            clock.main(False)
    else:
        clock.main(False)

    draw_detected_markers(corners, ids, frame, clock)

    if cv2.waitKey(1) == ord("q"):
        sys.exit()


def detect_markers(aruco_frame):
    """
    Detects ArUco markers.
    """

    aruco_dict = cv2.aruco.getPredefinedDictionary(MY_ARUCO_DICT)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    return detector.detectMarkers(aruco_frame)


def draw_detected_markers(corners, ids, feed_frame, clock):
    """
    Draws detected corners onto the frame.
    Draw current control mode onto the frame.
    """

    if ids is not None:
        for i, _ in enumerate(ids.flatten()):
            for corner in corners[i][0]:
                x, y = corner
                feed_frame = cv2.circle(
                    feed_frame,
                    (int(x), int(y)),
                    radius=5,
                    color=(0, 0, 255),
                    thickness=-1)

    flipped_frame = cv2.flip(feed_frame, 1)

    text = str(aliases[clock.steady_mode])
    (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    pos_x = (flipped_frame.shape[1] - text_w) // 2
    pos_y = text_h + 10

    cv2.putText(
        flipped_frame,
        text,
        (pos_x, pos_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2
        )

    cv2.imshow("Camera Feed", flipped_frame)


def main():
    """
    Opens camera.
    Executes main loop.
    """

    clock = Clock()
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise IOError("Cannot open camera.")

    try:
        while True:
            process_frame(cam, clock)
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
