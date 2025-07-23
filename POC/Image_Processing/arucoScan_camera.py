"""
Date: 23.07.2025
Autor: Nelio Gautschi
Purpose:
    - Find ArUco Tag in camera feed
"""

import cv2 as ocv

# load predefined ArUco dictionary, parameters and detector
dictionary = ocv.aruco.DICT_4X4_50
arucoDict = ocv.aruco.getPredefinedDictionary(dictionary)
parameters = ocv.aruco.DetectorParameters()
detector = ocv.aruco.ArucoDetector(arucoDict, parameters)

# start camera
def initialize_camera(index=0):
    cam = ocv.VideoCapture(index)
    if not cam.isOpened():
        raise IOError("Cannot open camera.")
    return cam

# get the frame
def read_frame(camera):
    success, frame = camera.read()
    return success, frame

# convert the frame to greyscale
def convert_to_grayscale(frame):
    return ocv.cvtColor(frame, ocv.COLOR_BGR2GRAY)

# flip the frame to mirror the actual picture
def flip(frame):    
    return ocv.flip(frame, 1)

# show the frame on pc display
def display_frame(window_name, frame):
    ocv.imshow(window_name, frame)

# main logic
def main():
    camera = initialize_camera()

    try:
        while True:
            success, frame = read_frame(camera)
            if not success:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            aruco_frame = convert_to_grayscale(frame) # frame for detectMarkers function should not be flipped
            feed_frame = flip(convert_to_grayscale(frame))
            display_frame('Camera Feed (Grayscale)', feed_frame)

            corners, ids, rejected = detector.detectMarkers(aruco_frame)
            print("Detected corners:", corners)
            print("Detected IDs:", ids)
            if ocv.waitKey(1) == ord('q'):
                break
    finally:
        camera.release()
        ocv.destroyAllWindows()

if __name__ == "__main__":
    main()