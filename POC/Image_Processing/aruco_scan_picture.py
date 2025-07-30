"""
Date: 16.07.2025

Author: Nelio Gautschi

Purpose:
    - Load image from given file path
    - Find ArUco Tag in a picture
    - Print the coordinates in a user-friendly format
"""

import sys

import cv2

from my_config2 import MY_ARUCO_DICT


IMAGE_PATH = "POC/Markers/Marker.png"


def load_image(path):
    """
    Loads an image from the given path.
    """

    image = cv2.imread(path)
    if image is None:
        print(f"❌ ERROR: Could not read image at '{path}'. Check the file path.")
        sys.exit(1)
    return image


def detect_markers(gray_image):
    """
    Detects ArUco markers.
    """

    aruco_dict = cv2.aruco.getPredefinedDictionary(MY_ARUCO_DICT)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    return detector.detectMarkers(gray_image)


def print_detected_markers(corners, ids):
    """
    Prints detected markers in a readable format
    """

    labels = ["Top-right", "Top-left", "Bottom-left", "Bottom-right"]
    if ids is None or len(ids) == 0:
        print("❌ No markers detected.")
    else:
        for i, marker_id in enumerate(ids.flatten()):
            print(f"Marker ID: {marker_id}")
            print("Corners:")
            for corner, label in zip(corners[i][0], labels):
                x, y = corner
                print(f"    {label} corner: {x:.1f}/{y:.1f}")
            print()


def main():
    """
    Main function for ArUco detection.
    """

    image = load_image(IMAGE_PATH)
    corners, ids, _ = detect_markers(image)
    print_detected_markers(corners, ids)


if __name__ == "__main__":
    main()
