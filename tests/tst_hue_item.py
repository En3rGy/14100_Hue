import unittest
import logging
import json

import hue_item
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

        self.hue_device = HueDevice(self.logger)

        self.hue_device.interval = 0
        # self.hue_device.logger = self.logger
        # self.hue_device.id = str()
        self.hue_device.name = "name"
        self.hue_device.room_name = "room_name"
        self.hue_device.device_id = self.device_id
        self.hue_device.light_id = "light_id"
        self.hue_device.zigbee_connectivity_id = "zigbee_connectivity_id"
        self.hue_device.room = "room"
        self.hue_device.zone = "zone"
        self.hue_device.scenes = [{"id": "scenes_id_1", "name": "name1"},
                                  {"id": "scenes_id_2", "name": "name2"},
                                  {"id": "scenes_id_3", "name": "name3"}]
        self.hue_device.grouped_lights = ["grouped_light_1", "grouped_light_2", "grouped_light_3"]
        # self.hue_device.rtype = str()
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
        self.assertTrue(len(device_ids) is 11)


if __name__ == '__main__':
    unittest.main()
