"""
Date: 13.10.2025

Autor: Nelio Gautschi

Purpose:

"""


import time
import math

import cv2
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

import config
import debug


class TagEvaluater:
    """
    Handles all the image and aruco tag processing.
    """

    def __init__(self):
        self.ids = None
        self.tags = []
        self.calibrated = False
        self.distance_snapshot = (None, None)
        self.distance = None
        self.area_snapshot = None
        self.y_middle = None

    def determine_tilt(self):
        """
        Compares distances and areas to determine flight hand allignment on screen.
        """

        v_til, v_alt, v_yaw = 0, 0, 0

        d = self.distance
        d_ss = self.distance_snapshot

        a = self._shoelace_formula()
        areas = dict(zip(self.ids, a))
        areas_ss = self.area_snapshot

        if (d_ss[0]/d[0]) + (d_ss[2]/d[2]) > (d_ss[1]/d[1]) + (d_ss[3]/d[3]) + config.Y_DZ:
            # y-axis yaw detecked
            if areas[2] + areas[3] > areas[1] + areas[4]:
                # yaw to the right
                if areas[2] > areas_ss[2] and areas[3] > areas_ss[3]:
                    # left closer to screen than snapshot
                    v_yaw = -config.VY

            elif areas[1] + areas[4] > areas[2] + areas[3]:
                # yaw to the left
                if areas[1] > areas_ss[1] and areas[4] + areas_ss[4]:
                    # right closer to screen than snapshot
                    v_yaw = config.VY

        if (d_ss[1]/d[1]) + (d_ss[3]/d[3]) > (d_ss[0]/d[0]) + (d_ss[2]/d[2]) + config.T_DZ:
            # x-axis tilt detecked
            if areas[1] + areas[2] > areas[3] + areas[4]:
                # forwards-tilt
                if areas[1] > areas_ss[1] and areas[2] > areas_ss[2]:
                    # top closer to screen than snapshot
                    v_til = config.VT

            elif areas[3] + areas[4] > areas[1] + areas[2]:
                # backward-tilt
                if areas[3] > areas_ss[3] and areas[4] > areas_ss[4]:
                    # bottom closer to screen than snapshot
                    v_til = -config.VT

        big_marker = [self._get_middle(tag) for tag in self.tags]
        m_big_marker = self._get_middle(big_marker)
        ym_big_marker = m_big_marker[1]

        if self.y_middle - ym_big_marker > config.A_DZ: # Middle point above y-deadzone
            v_alt = config.VA
        elif ym_big_marker - self.y_middle > config.A_DZ: # Middle point below y-deadzone
            v_alt = -config.VA

        return (v_til, v_alt, v_yaw)

    def _get_distance(self, id1, id2):
        tag1 = self.tags[self.ids.index(id1)]
        tag2 = self.tags[self.ids.index(id2)]
        vector1 = self._get_middle(tag1)
        vector2 = self._get_middle(tag2)
        distance = self._vector_subtraction(vector1, vector2)
        return distance

    def _get_middle(self, tag):
        sx = sum(corner[0] for corner in tag)
        sy = sum(corner[1] for corner in tag)
        mx = sx / 4
        my = sy / 4
        return (mx, my)

    def _vector_subtraction(self, v1, v2):
        v3 = (v1[0] - v2[0], v1[1] - v2[1])
        d = math.sqrt(v3[0]**2 + v3[1]**2)
        return d

    def _shoelace_formula(self):
        areas = []
        for tag in self.tags:
            x1, y1 = tag[0]
            x2, y2 = tag[1]
            x3, y3 = tag[2]
            x4, y4 = tag[3]

            area = 0.5 * abs(
                (x1*y2 + x2*y3 + x3*y4 + x4*y1) -
                (y1*x2 + y2*x3 + y3*x4 + y4*x1))

            areas.append(area)

        return areas

    def _numpy2list(self, tags):
        self.tags = []
        for i in range(len(self.ids)):
            tag_as_2d_array = []
            for corner in tags[i][0]:
                x, y = corner
                tag_as_2d_array.append((x, y))

            self.tags.append(tag_as_2d_array)

    def _y_center(self, tags):
        m1 = self._get_middle(tags[1])
        m2 = self._get_middle(tags[2])
        m3 = self._get_middle(tags[3])
        m4 = self._get_middle(tags[4])

        big_middle = self._get_middle([m1, m2, m3, m4])

        self.y_middle = big_middle[1]

    def make_snapshot(self, tags, ids, cam):
        """
        Initiates the calibration process.
        Safes a snapshot of the data.
        """

        if ids is not None and all(_id in ids for _id in config.USED_TAGS):
            _ = self.update(tags, ids)
            self.distance_snapshot = self.distance

            areas = self._shoelace_formula()
            self.area_snapshot = dict(zip(self.ids, areas))

            assigned_tags = dict(zip(self.ids, self.tags))
            self._y_center(assigned_tags)

            reference_marker = self.tags[self.ids.index(4)]
            tl = reference_marker[0]
            br = reference_marker[2]
            k = 10
            start_point = (int(tl[0] - k), int(tl[1] - k))
            end_point = (int(br[0] + k), int(br[1] + k))
            cam.reference = [start_point, end_point]

            self.calibrated = True

    def update(self, tags, ids):
        """
        Updates variables.
        Executes formatting and calculating functions.
        Returns the calculated velocity tuple.
        """

        self.ids = [_id[0] for _id in ids]
        self._numpy2list(tags)
        self.distance = (
            self._get_distance(1, 2),
            self._get_distance(2, 3),
            self._get_distance(3, 4),
            self._get_distance(4, 1)
            )

        if self.calibrated:
            return self.determine_tilt()
        return None


def main():
    """
    Initiates all the classes.
    Catches errors.
    Connects to crazyflie with the MotionCommander
    """

    cam = config.Camera()
    sw = config.Timer()
    te = TagEvaluater()
    controller = config.DroneController()

    config.calibrate(te, cam)

    cflib.crtp.init_drivers()
    debug.main("deck")

    try:
        with SyncCrazyflie(config.MY_URI, cf=Crazyflie(rw_cache="cache")) as scf:
            scf.cf.platform.send_arming_request(True)
            time.sleep(1.0)
            with MotionCommander(scf, default_height=config.DEFAULT_HEIGHT) as mc:
                cam.open_cam()
                sw.reset()
                while controller.flying:
                    if cv2.waitKey(1) == ord("q"):
                        cam.close_cam()
                        controller.land()
                        break

                    frame, corners, ids = cam.process_frame()
                    if ids is not None and all(_id in ids for _id in config.USED_TAGS):
                        sw.reset()
                        direction = te.update(corners, ids)
                    else:
                        direction = (0, 0, 0)
                        sw.safety_check(controller, cam)

                    controller.determine_state(mc, direction)
                    cam.show_feed(corners, ids, frame)

    except Exception as e:
        debug.handle_error(e)


if __name__ == "__main__":
    main()
