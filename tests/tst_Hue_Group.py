# coding: utf8
# import struct
import hue_lib.hue_item as hue_item
import hue_lib.hue_bridge as hue_bridge
import hue_lib.supp_fct as supp_fct

import unittest
import time
import json
import logging


################################
# get the code
with open('framework_helper.py', 'r') as f1, open('../src/14100_Hue Group (14100).py', 'r') as f2:
    framework_code = f1.read()
    debug_code = f2.read()

exec (framework_code + debug_code)


################################
# unit tests
class UnitTests(unittest.TestCase):

    def load_data(self, module, itm_id=None):
        """

        :param module:
        :param itm_id:
        :type module: HueGroup_14100_14100
        """
        module.debug_input_value[self.dummy.PIN_I_HUE_KEY] = self.cred["PIN_I_SUSER"]

        # self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_light_id_esszimmer"]
        if not itm_id:
            module.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_light_id"]
            # module.debug_rid = self.cred["hue_light_id"]
        else:
            module.debug_input_value[self.dummy.PIN_I_ITM_IDX] = itm_id
            # module.debug_rid = itm_id

        # self.dummy.on_init()
        module.DEBUG = self.dummy.FRAMEWORK.create_debug_section()
        module.g_out_sbc = {}
        module.debug = False
        # hue_bridge.set_bridge_ip(self.cred["PIN_I_SHUEIP"])

        # module.FRAMEWORK.my_ip = self.cred["my_ip_wlan"]

        global EVENTSTREAM_TIMEOUT
        EVENTSTREAM_TIMEOUT = 1
        global EVENTSTREAM_RECONNECT_ELAPSE
        EVENTSTREAM_RECONNECT_ELAPSE = 60

    def setUp(self):
        print("\n### setUp")

        logging.basicConfig()
        self.logger = logging.getLogger("UnitTests")
        self.logger.setLevel(logging.DEBUG)
        with open("credentials.json") as f:
            self.cred = json.load(f)

        self.dummy = HueGroup_14100_14100(0)

        self.load_data(self.dummy)

        self.device = hue_item.HueDevice(self.dummy.logger)
        # self.device.id = self.cred["hue_light_id_studio"]
        self.device.id = self.cred["hue_light_id_esszimmer"]
        self.device.rtype = "light"

        self.ip = self.cred["PIN_I_SHUEIP"]
        self.key = self.cred["PIN_I_SUSER"]

    def tearDown(self):
        print("\n### tearDown")
        try:
            self.dummy.server.stop_server()
        except:
            pass
        try:
            self.dummy.stop_eventstream()
        except:
            pass

        finally:
            del self.dummy
            print("\n\nFinished.\n\n")

    def helper_light_test_device(self, itm_idx, rtype):
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = itm_idx
        self.device = hue_item.HueDevice(self.dummy.logger)
        self.device.id = itm_idx
        self.device.rtype = rtype
        ret = self.device.set_on(self.ip, self.key, False)
        self.assertTrue(ret)
        time.sleep(3)
        ret = self.device.set_on(self.ip, self.key, True)
        self.assertTrue(ret)
        time.sleep(3)

    def helper_light_test_full(self, itm_idx):
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = itm_idx
        self.dummy.on_init()
        self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, False)
        time.sleep(3)
        # self.assertFalse(self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF])
        self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, True)
        time.sleep(3)
        # self.assertTrue(self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF])

    def test_00_init(self):  # 2022-11-16 OK
        print("\n### ### test_00_init")
        self.dummy.on_init()

    def test_09_singleton_eventstream(self):
        self.logger.info("test_09_singleton_eventstream")

        module_1 = HueGroup_14100_14100(0)
        # module_1.FRAMEWORK.my_ip = self.cred["my_ip2"]
        module_1.on_init()

        module_2 = HueGroup_14100_14100(0)
        # module_2.FRAMEWORK.my_ip = self.cred["my_ip2"]
        module_2.on_init()

        self.assertTrue(module_1.eventstream_thread.is_alive())
        self.assertFalse(module_2.eventstream_thread.is_alive())

        time.sleep(3)

        module_1.stop_eventstream()
        module_2.stop_eventstream()

        time.sleep(3)

        self.assertFalse(get_eventstream_is_connected())
        self.assertFalse(module_1.eventstream_thread.is_alive())
        self.assertFalse(module_2.eventstream_thread.is_alive())

    def test_log_eventstream(self):
        # ec86940a-ce69-414d-9b6c-81e50793f8c4
        self.dummy.on_init()
        time.sleep(30)

    def test_10_16_eventstream(self):  # 2022-11-16 OK
        self.logger.info("### test_10_eventstream")

        self.dummy.on_init()

        module_1 = HueGroup_14100_14100(0)
        self.load_data(module_1)
        self.device = hue_item.HueDevice(module_1.logger)
        self.device.id = self.cred["hue_light_id_studio"]
        self.device.rtype = "light"
        module_1.on_init()

        print("--- Helper module ID {}".format(module_1.module_id))
        print("--- Test Obj. ID {}".format(self.dummy.module_id))

        time.sleep(2)

        module_1.on_input_value(module_1.PIN_I_ON_OFF, False)
        time.sleep(2)
        ret = self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF]
        self.assertFalse(ret)

        module_1.on_input_value(module_1.PIN_I_ON_OFF, True)
        time.sleep(2)
        ret = self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF]
        self.assertTrue(ret)

        self.logger.info("\n\nTest on your own :)\n\n")
        time.sleep(20)

        module_1.stop_eventstream()
        self.dummy.stop_eventstream()

    def test_10_eventstream_reconnect(self):  # 2022-11-17 OK
        print("\n### test_10_eventstream_reconnect")
        self.dummy.on_init()
        time.sleep(2)
        self.assertTrue(get_eventstream_is_connected())

        print("\n\nDisconnect network")
        time.sleep(10)
        print("Continuing")
        self.assertFalse(get_eventstream_is_connected())

        print("\n\nReconnect network")
        time.sleep(10)
        print("Continuing")
        self.assertFalse(get_eventstream_is_connected())

    def test_on_off_light_w_device(self):
        print("\n### test_on_off_light_w_device")
        rid = self.cred["hue_light_id"]
        self.helper_light_test_device(rid, "light")

    def test_on_off_light_full(self):
        print("\n### test_on_off_light_full")
        rid = self.cred["hue_light_id"]
        self.helper_light_test_full(rid)

    def test_on_off_grouped_light_w_device(self):
        print("\n### test_on_off_gouped_light_w_device")
        rid = self.cred["hue_grouped_light"]
        self.helper_light_test_device(rid, "grouped_light")

    def test_on_off_grouped_light_full(self):
        print("\n### test_on_off_gouped_light_full")
        rid = self.cred["hue_grouped_light"]
        self.helper_light_test_full(rid)

    def test_14_on_off_zone(self):
        # on / off not available for zones, so just check that nothing happens
        print("\n### test_14_on_off_zone")
        rid = self.cred["hue_zone_id"]

        bridge = hue_bridge.HueBridge(self.dummy.logger)
        bridge.register_devices(self.key, rid, self.dummy.FRAMEWORK.get_homeserver_private_ip())
        device = bridge.get_own_device(rid)

        ret = device.set_on(self.ip, self.key, True)
        self.assertTrue(ret)

        ret = device.set_on(self.ip, self.key, False)
        self.assertTrue(ret)

        ret = device.set_on(self.ip, self.key, "error")
        self.assertFalse(ret)

    def test_21_scene(self):
        scene_id = self.cred["hue_scene_id"]
        ret = self.device.set_scene(self.ip, self.key, scene_id)
        self.assertTrue(ret)

    def test_15_on_off_room(self):
        # on / off not available for rooms, so just chek that nothing happens
        print("\n### test_15_on_off_room")
        rid = self.cred["hue_room_id"]

        bridge = hue_bridge.HueBridge(self.dummy.logger)
        bridge.register_devices(self.key, rid, self.dummy.FRAMEWORK.get_homeserver_private_ip())
        device = bridge.get_own_device(rid)

        ret = device.set_on(self.ip, self.key, True)
        self.assertTrue(ret)

        ret = device.set_on(self.ip, self.key, False)
        self.assertTrue(ret)

        ret = device.set_on(self.ip, self.key, "error")
        self.assertFalse(ret)

    def test_17_dimming(self):  # 2022-11-16 OK
        print("\n### test_17_dimming")

        self.dummy.curr_bri = 255

        self.device.prep_dim(self.ip, self.key, 0x85, 5)
        self.assertEqual(-16, self.device.interval)
        # self.assertEqual(10, self.device.timer.interval)
        time.sleep(3)
        self.device.prep_dim(self.ip, self.key, 0x8d, 5)
        self.assertEqual(16, self.device.interval)

    def test_20_reachable(self):  # 2022-11-18 OK
        print("\n### test_20_reacable")
        ret = supp_fct.get_data(self.ip, self.key, "zigbee_connectivity/" + self.cred["hue_zigbee_studio"],
                                self.dummy.logger)
        self.assertTrue("data" in ret, "####1")
        data = ret["data"]
        data = json.loads(data)
        data = data["data"][0]
        self.assertTrue("status" in data)
        status = data["status"]
        self.assertEqual("connected", status)

    def test_dynamic_scene(self):  # 2022-11-16 OK
        print("\n### test_dynamic_scene")
        ret = self.device.set_dynamic_scene(self.ip, self.key, self.scene_dyn, 0.7)
        self.assertTrue(ret)

    def test_10_long_time_eventstream(self):  # 2022-11-16 OK
        logging.basicConfig()
        self.logger.info("### test_10_eventstream")

        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_light_id_wz"]
        self.dummy.logger.setLevel(logging.DEBUG)
        self.dummy.on_init()
        self.dummy.logger.setLevel(logging.DEBUG)

        # module_2 = HueGroup_14100_14100(0)
        # self.load_data(module_2, self.cred["hue_light_id_esszimmer"])
        # self.device = hue_item.HueDevice(module_2.logger)
        # self.device.id = self.cred["hue_light_id_esszimmer"]
        # self.device.rtype = "light"
        # module_2.on_init()
        # module_2.logger.setLevel(logging.DEBUG)

        print("\n\n")
        self.logger.info("Starting 24 h test")
        # self.logger.info("- Helper module 1 ID {}".format(module_1.module_id))
        # self.logger.info("- Helper module 2 ID {}".format(module_2.module_id))
        self.logger.info("- Test Obj. ID {}".format(self.dummy.module_id))
        print("\n\n")

        time.sleep(60 * 60 * 24)

        # module_1.stop_eventstream()
        # module_2.stop_eventstream()
        self.dummy.stop_eventstream()

    def test_init(self):
        self.logger.debug("### test_init ###")
        self.logger.setLevel(logging.CRITICAL + 1)
        self.dummy.on_init()
        time.sleep(30)

    def test_inputs(self):
        print("\n### test_inputs")

        # reset former data
        # del self.device
        # del self.ip
        # del self.key
        # bridge = hue_bridge.HueBridge(self.logger)
        # bridge.set_bridge_ip(str())

        print("###### on_init")
        self.dummy.on_init()
        print("###### sleep 5")
        time.sleep(5)

        print("###### off")
        self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, 0)
        self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, 1)
        time.sleep(2)
        self.assertEqual(True, self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF])

        print("\n\nPIN_I_TRIGGER ################################################\n\n")

        self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, 0)
        self.dummy.set_output_value_sbc(self.dummy.PIN_O_STATUS_ON_OFF, True)
        self.dummy.on_input_value(self.dummy.PIN_I_TRIGGER, 1)
        time.sleep(2)
        self.assertEqual(False, self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF])

        print("\n\nPIN_I_BRI ################################################\n\n")
        self.dummy.on_input_value(self.dummy.PIN_I_BRI, 50)
        time.sleep(2)
        self.assertEqual(50, self.dummy.debug_output_value[self.dummy.PIN_O_BRI])

        print("\n\nPIN_I_R / G / B ################################################\n\n")
        self.dummy.debug_input_value[self.dummy.PIN_I_R] = 100
        self.dummy.on_input_value(self.dummy.PIN_I_R, 100)
        time.sleep(2)
        self.assertEqual(100, self.dummy.debug_output_value[self.dummy.PIN_O_R])
        print("..................")

        self.dummy.debug_input_value[self.dummy.PIN_I_G] = 100
        self.dummy.on_input_value(self.dummy.PIN_I_G, 100)
        time.sleep(2)
        self.assertEqual(100, self.dummy.debug_output_value[self.dummy.PIN_O_G])
        print("..................")

        self.dummy.debug_input_value[self.dummy.PIN_I_B] = 100
        self.dummy.on_input_value(self.dummy.PIN_I_B, 100)
        time.sleep(2)
        self.assertEqual(100, self.dummy.debug_output_value[self.dummy.PIN_O_B])

        print("\n\nPIN_I_REL_DIM ################################################\n\n")

        self.dummy.debug_input_value[self.dummy.PIN_I_REL_DIM] = 0x85
        self.dummy.debug_input_value[self.dummy.PIN_I_DIM_RAMP] = 10
        self.dummy.on_input_value(self.dummy.PIN_I_REL_DIM, 0x85)
        time.sleep(2)
        self.assertEqual(18, self.dummy.debug_output_value[self.dummy.PIN_O_BRI])

        print("\n\nPIN_I_SCENE ################################################\n\n")
        self.dummy.on_input_value(self.dummy.PIN_I_SCENE, self.cred["hue_scene_id"])

        """
        self.dummy.PIN_I_HUE_KEY = 2
        self.dummy.PIN_I_PORT = 3
        self.dummy.PIN_I_ITM_IDX = 4
        self.dummy.PIN_I_DIM_RAMP = 11
        """

    def test_23_non_blocking(self):
        self.logger.info("test_23_non_blocking")
        self.logger.info("Disconnect network")
        time.sleep(10)
        self.logger.info("continue...")

        del self.device
        del self.ip
        del self.key
        bridge = hue_bridge.HueBridge(self.logger)
        bridge.set_bridge_ip(str())

        self.dummy.on_init()


if __name__ == '__main__':
    unittest.main()
