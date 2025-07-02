import cv2 as ocv

# Load predefined ArUco dictionary
dictionary = ocv.aruco.DICT_4X4_50
arucoDict = ocv.aruco.getPredefinedDictionary(dictionary)

# Load and convert the image to grayscale
image_path = "POC/Markers/Marker.png"
arucoMarker = ocv.imread(image_path)

if arucoMarker is None:
    print(f"ERROR: Could not read image at '{image_path}'. Check the file path.")
    exit()

arucoMarker_gray = ocv.cvtColor(arucoMarker, ocv.COLOR_BGR2GRAY)

# Create detector with updated API
parameters = ocv.aruco.DetectorParameters()
detector = ocv.aruco.ArucoDetector(arucoDict, parameters)

# Detect markers
corners, ids, rejected = detector.detectMarkers(arucoMarker_gray)

# Output
print("Detected corners:", corners)
print("Detected IDs:", ids)
