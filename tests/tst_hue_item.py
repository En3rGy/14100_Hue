import time
import unittest
import logging
import json

import supp_fct
from hue_item import HueDevice


TRACE = 5


class TestModuleRegistration(unittest.TestCase):
    class FunctionHandler(logging.Handler):
        def __init__(self):
            super(TestModuleRegistration.FunctionHandler, self).__init__()

        def emit(self, record):
            print("{level}:{msg}".format(msg=record.getMessage(), level=record.levelname))

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        logging.addLevelName(TRACE, "TRACE")

        def trace(self, message, *args, **kws):
            if self.isEnabledFor(TRACE):
                self._log(TRACE, message, args, **kws)

        logging.Logger.trace = trace

        handler = self.FunctionHandler()
        self.logger.addHandler(handler)

        self.logger.setLevel(logging.DEBUG)

        with open("credentials.json") as f:
            self.cred = json.load(f)
            self.ip = self.cred["my_ip2"]
            self.bridge_ip = self.cred["PIN_I_SHUEIP"]
            self.key = self.cred["PIN_I_SUSER"]
            self.device_id = self.cred["hue_device_id"]
            self.light_id = self.cred["hue_light_id"]

        self.hue_device = HueDevice(self.logger)

        self.hue_device.interval = 0
        # self.hue_device.logger = self.logger
        self.hue_device.id = self.light_id
        self.hue_device.name = "name"
        self.hue_device.room_name = "room_name"
        self.hue_device.device_id = self.device_id
        self.hue_device.light_id = self.light_id
        self.hue_device.zigbee_connectivity_id = "zigbee_connectivity_id"
        self.hue_device.room = "room"
        self.hue_device.zone = "zone"
        self.hue_device.scenes = [{"id": "scenes_id_1", "name": "name1"},
                                  {"id": "scenes_id_2", "name": "name2"},
                                  {"id": "scenes_id_3", "name": "name3"}]
        self.hue_device.grouped_lights = ["grouped_light_1", "grouped_light_2", "grouped_light_3"]
        self.hue_device.rtype = "light"
        # self.hue_device.curr_bri = 0
        # self.hue_device.stop = False
        # self.hue_device.timer = threading.Timer(10, self.do_dim)
        # self.hue_device.ip = str()
        # self.hue_device.key = str()
        # self.hue_device.dim_ramp = 0
        # self.hue_device.gamut_type = str()

    def tearDown(self):
        pass

    def test_str(self):
        self.logger.debug(self.hue_device)
        self.assertTrue(str(self.hue_device))

    def test_get_device_ids(self):
        device_ids = self.hue_device.get_device_ids()
        self.logger.debug(device_ids)
        self.assertEqual(len(device_ids), 11)

        hue_device = HueDevice(self.logger)
        device_ids = hue_device.get_device_ids()
        self.logger.debug(device_ids)
        self.assertEqual(len(device_ids), 0)

    def test_set_on(self):
        ret = self.hue_device.set_on(self.bridge_ip, self.key, True)
        self.assertTrue(ret)
        time.sleep(1)
        ret = self.hue_device.set_on(self.bridge_ip, self.key, False)
        self.assertTrue(ret)

    def test_set_bri(self):
        self.hue_device.set_on(self.bridge_ip, self.key, True)

        ret = self.hue_device.set_bri(self.bridge_ip, self.key, 30)
        self.assertTrue(ret)
        time.sleep(1)
        ret = self.hue_device.set_bri(self.bridge_ip, self.key, 80)
        self.assertTrue(ret)

        self.hue_device.set_on(self.bridge_ip, self.key, False)

    def test_set_color_xy_bri(self):
        self.hue_device.set_on(self.bridge_ip, self.key, True)
        self.hue_device.set_bri(self.bridge_ip, self.key, 100)

        # green
        ret = self.hue_device.set_color_xy_bri(self.bridge_ip, self.key, 0.3, 0.6)
        [r, g, b] = supp_fct.xy_bri_to_rgb(0.3, 0.6, 1, self.hue_device.gamut_type)  # (235, 255, 67)
        print(r, g, b)
        self.assertTrue(ret)
        time.sleep(3)
        ret = self.hue_device.set_color_rgb(self.bridge_ip, self.key, r, g, b)
        # ret = self.hue_device.set_color_rgb(self.bridge_ip, self.key, 92, 100, 92)
        self.assertTrue(ret)
        time.sleep(3)

        # red
        ret = self.hue_device.set_color_xy_bri(self.bridge_ip, self.key, 1, 0)
        self.assertTrue(ret)
        time.sleep(3)
        ret = self.hue_device.set_color_xy_bri(self.bridge_ip, self.key, 1, 1)
        self.assertTrue(ret)
        time.sleep(3)
        self.hue_device.set_on(self.bridge_ip, self.key, False)

    def test_set_color_rgb(self):
        self.hue_device.set_on(self.bridge_ip, self.key, True)

        ret = self.hue_device.set_color_rgb(self.bridge_ip, self.key, 80, 0, 0)
        self.assertTrue(ret)
        time.sleep(1)
        ret = self.hue_device.set_color_rgb(self.bridge_ip, self.key, 0, 80, 0)
        self.assertTrue(ret)
        time.sleep(1)
        ret = self.hue_device.set_color_rgb(self.bridge_ip, self.key, 0, 0, 80)
        self.assertTrue(ret)
        time.sleep(1)
        self.hue_device.set_on(self.bridge_ip, self.key, False)

    def test_set_scene(self):
        ret = self.hue_device.set_scene(self.bridge_ip, self.key, self.cred["hue_scene_id"])
        self.assertTrue(ret)
        time.sleep(1)
        ret = self.hue_device.set_scene(self.bridge_ip, self.key, "No scene")
        self.assertFalse(ret)
        time.sleep(1)
        ret = self.hue_device.set_scene(self.bridge_ip, self.key, "No_scene")
        self.assertFalse(ret)
        time.sleep(1)
        self.hue_device.set_on(self.bridge_ip, self.key, False)

    def test_set_dynamic_scene(self):
        ret = self.hue_device.set_dynamic_scene(self.bridge_ip, self.key, self.cred["hue_scene_id"], 0.5)
        self.assertTrue(ret)
        time.sleep(1)
        self.hue_device.set_on(self.bridge_ip, self.key, False)

    def test_prep_dim(self):
        self.assertTrue(False)

    def test_do_dim(self):
        self.assertTrue(False)

    def test_get_type_of_device(self):
        ret = self.hue_device.get_type_of_device()
        self.assertEqual(ret, "light")


if __name__ == '__main__':
    unittest.main()
