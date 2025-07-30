"""
Date: 02.06.2025

Autor: Nelio Gautschi

Purpose:
    - Use OpenCV to capture camera feed
    - Convert feed to grayscale
    - Display the result in a window
"""

import cv2


def initialize_camera(index=0):
    """
    Initializes the camera with the given index.
    """

    cam = cv2.VideoCapture(index)
    if not cam.isOpened():
        raise IOError("Cannot open camera.")
    return cam


def read_frame(camera):
    """
    Reads a single frame from the camera.
    """

    success, frame = camera.read()
    return success, frame


def convert_to_grayscale(frame):
    """
    Converts a frame to grayscale.
    """

    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return grey_frame


def flip(frame):
    """
    Horizontally flips the frame to create a mirror image.
    """

    flipped_frame = cv2.flip(frame, 1)
    return flipped_frame


def display_frame(window_name, frame):
    """
    Displays the given frame in a named window.
    """

    cv2.imshow(window_name, frame)


def main():
    """
    Runs the main camera loop:
    - Captures frames
    - Converts them to grayscale
    - Mirrors them
    - Displays the output
    Press "q" to exit.
    """

    camera = initialize_camera()

    try:
        while True:
            success, frame = read_frame(camera)
            if not success:
                print("Cannot receive frame (stream end?). Exiting ...")
                break

            gray_frame = convert_to_grayscale(frame)
            final_frame = flip(gray_frame)
            display_frame("Camera Feed (Grayscale)", final_frame)

            if cv2.waitKey(1) == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
