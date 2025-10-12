"Author: Nelio Gautschi"

formatted_markers = [
    [(10, 10), (20, 10), (20, 20), (10, 20)], # erster Marker
    [(30, 15), (40, 15), (40, 25), (30, 25)], # zweiter Marker
    [(50, 12), (60, 12), (60, 22), (50, 22)], # dritter Marker
]

markers_as_areas = []
for marker in formatted_markers:
    x1, y1, x2, y2 = marker[0], marker[1]
    x3, y3, x4, y4 = marker[2], marker[3]

    # Shoelace-Formel
    area = 0.5 * abs(
        (x1*y2 + x2*y3 + x3*y4 + x4*y1) -
        (y1*x2 + y2*x3 + y3*x4 + y4*x1))

    # Speichern der berechneten Fläche
    markers_as_areas.append(area)
