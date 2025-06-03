"""
Date: 02.06.2025
Purpose:
    - Use OpenCV to capture camera feed
    - Convert feed to grayscale
    - Display the result in a window
"""

import cv2 as ocv

def initialize_camera(index=0):
    cam = ocv.VideoCapture(index)
    if not cam.isOpened():
        raise IOError("Cannot open camera.")
    return cam

def read_frame(camera):
    success, frame = camera.read()
    return success, frame

def convert_to_grayscale(frame):
    return ocv.cvtColor(frame, ocv.COLOR_BGR2GRAY)

def display_frame(window_name, frame):
    ocv.imshow(window_name, frame)

def main():
    camera = initialize_camera()

    try:
        while True:
            success, frame = read_frame(camera)
            if not success:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            gray_frame = convert_to_grayscale(frame)
            display_frame('Camera Feed (Grayscale)', gray_frame)

            if ocv.waitKey(1) == ord('q'):
                break
    finally:
        camera.release()
        ocv.destroyAllWindows()

if __name__ == "__main__":
    main()