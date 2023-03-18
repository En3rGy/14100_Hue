import unittest
import logging
import json

import supp_fct

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

    def tearDown(self):
        pass

    def test_rgb_to_xy_bri(self):
        # rgb(255,0,0) 	xy(0.675,0.322)
        # rgb(0,128,0) 	xy(0.4091,0.518)
        # rgb(221,160,221) 	xy(0.3495,0.2545)
        [x, y, bri] = supp_fct.rgb_to_xy_bri(255, 0, 0, "C")
        self.assertEqual([0.675, 0.322, 1], [round(x, 4), round(y, 4), bri], "red")
        [x, y, bri] = supp_fct.rgb_to_xy_bri(0, 128, 0, "C")
        self.assertEqual([0.4091, 0.518, 1], [round(x, 4), round(y, 4), bri], "lime")
        [x, y, bri] = supp_fct.rgb_to_xy_bri(221, 160, 221, "C")
        self.assertEqual([0.3495, 0.2545, 1], [round(x, 4), round(y, 4), bri], "plum")

    def test_xy_bri_to_rgb(self):
        print("\n### test_19_xy_to_rgb")
        [r, g, b] = supp_fct.xy_bri_to_rgb(0.675, 0.322, 1, "C")
        self.assertEqual([255, 70, 2], [r, g, b], "red")

        [r, g, b] = supp_fct.xy_bri_to_rgb(0.4091, 0.518, 1, "C")
        self.assertEqual([0, 128, 0], [r, g, b], "red")

        [r, g, b] = supp_fct.xy_bri_to_rgb(0.3495, 0.2545, 1, "C")
        self.assertEqual([221, 160, 221], [r, g, b], "red")

    def test_hex2int(self):
        ret = supp_fct.hex2int("\x01")
        self.assertEqual(1, ret)
        ret = supp_fct.hex2int("\x00")
        self.assertEqual(0, ret)
        ret = supp_fct.hex2int("\xA6")
        self.assertEqual(166, ret)
        ret = supp_fct.hex2int("\xA6\xFF\xC1\x00")
        self.assertEqual(2801778944, ret)
        ret = supp_fct.hex2int("")
        self.assertEqual(0, ret)

    def test_get_val(self):
        ret = supp_fct.get_val({"test": "1", "test2": 2}, "test")
        self.assertEqual(ret, "1")
        ret = supp_fct.get_val({"test": "1", "test2": 2}, "test2")
        self.assertEqual(ret, 2)
        ret = supp_fct.get_val('{"test": "1", "test2": 2}', "test2")
        self.assertEqual(ret, str())
        ret = supp_fct.get_val({"test": "1", "test2": 2}, "test3")
        self.assertEqual(ret, str())

    def test_get_data(self):
        print("\n### test_get_data")
        ret = supp_fct.get_data(self.bridge_ip, self.key, "light", self.logger)
        self.assertTrue("data" in ret)
        self.assertTrue("status" in ret)
        self.assertTrue(len(ret["data"]) > 0)
        self.assertEqual(int(200), int(ret["status"]))

        self.logger.info("Expecting an error message in the following...")
        ret = supp_fct.get_data(self.ip, self.key, "error", self.logger)
        self.assertNotEqual(int(ret["status"]), 200)


    def test_http_put(self):
        self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
