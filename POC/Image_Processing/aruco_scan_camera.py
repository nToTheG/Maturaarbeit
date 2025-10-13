"""
Date: 23.07.2025

Autor: Nelio Gautschi

Purpose:
    - get camera feed
    - Detect corners of ArUco Tag in camera feed
    - Draw the corners as red circles on the displayed feed
"""

import sys

import cv2

from my_config2 import MY_ARUCO_DICT


def process_frame(cam):
    """
    Reads camera feed.
    Displays camera feed.
    """

    success, frame = cam.read()
    if not success:
        print("Cannot receive frame (stream end?). Exiting ...")
        sys.exit()

    aruco_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detect_markers(aruco_frame)

    draw_detected_markers(corners, ids, frame)

    if cv2.waitKey(1) == ord('q'):
        sys.exit()


def detect_markers(aruco_frame):
    """
    Detects ArUco markers.
    """

    aruco_dict = cv2.aruco.getPredefinedDictionary(MY_ARUCO_DICT)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    return detector.detectMarkers(aruco_frame)


def draw_detected_markers(corners, ids, feed_frame):
    """
    Draws detected corners onto the frame.
    """
    flipped_frame = feed_frame
    print(ids)
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


def main():
    """
    Opens camera.
    Executes main loop.
    """

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise IOError("Cannot open camera.")

    try:
        while True:
            process_frame(cam)
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
