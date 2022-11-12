# coding: utf8
# import struct
import hue_lib.hue_bridge
import hue_lib.hue_bridge as hue_bridge
import hue_lib.supp_fct as supp_fct
import hue_lib.html_server as html_server

import unittest
import ssl
import urllib2
import urlparse
import socket
import time
import json

import threading
import BaseHTTPServer
import SocketServer

import random


class hsl20_4:
    LOGGING_NONE = 0

    def __init__(self):
        pass

    class BaseModule:
        debug_output_value = {}  # type: {int, any}
        debug_set_remanent = {}  # type: {int, any}
        debug_input_value = {}  # type: {int: any}

        def __init__(self, a, b):
            self.module_id = 0

        def _get_framework(self):
            f = hsl20_4.Framework()
            return f

        def _get_logger(self, a, b):
            return 0

        def _get_remanent(self, key):
            # type: (str) -> any
            return 0

        def _set_remanent(self, key, val):
            # type: (str, any) -> None
            self.debug_set_remanent = val

        def _set_output_value(self, pin, value):
            # type: (int, any) -> None
            self.debug_output_value[int(pin)] = value
            print (str(time.time()) + "\t# Out: pin " + str(pin) + " <- \t" + str(value))

        def _set_input_value(self, pin, value):
            # type: (int, any) -> None
            self.debug_input_value[int(pin)] = value
            print "# In: pin " + str(pin) + " -> \t" + str(value)

        def _get_input_value(self, pin):
            # type: (int) -> any
            if pin in self.debug_input_value:
                return self.debug_input_value[pin]
            else:
                return 0

        def _get_module_id(self):
            # type: () -> int
            if self.module_id == 0:
                self.module_id = random.randint(1, 1000)
            return self.module_id

    class Framework:
        def __init__(self):
            self.my_ip = "127.0.0.1"

        def _run_in_context_thread(self, a):
            pass

        def create_debug_section(self):
            d = hsl20_4.DebugHelper()
            return d

        def get_homeserver_private_ip(self):
            # type: () -> str
            return self.my_ip

        def get_instance_by_id(self, id):
            # type: (int) -> str
            return ""

    class DebugHelper:
        def __init__(self):
            pass

        def set_value(self, cap, text):
            print(str(time.time()) + "\tValue:\t'" + str(cap) + "': " + str(text))

        def add_message(self, msg):
            print(str(time.time()) + "\tMsg:  \t" + str(msg))

    ############################################


class HueGroup_14100_14100(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "hsl20_3_Hue")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE, ())
        self.PIN_I_TRIGGER = 1
        self.PIN_I_HUE_KEY = 2
        self.PIN_I_PORT = 3
        self.PIN_I_ITM_IDX = 4
        self.PIN_I_ON_OFF = 5
        self.PIN_I_BRI = 6
        self.PIN_I_R = 7
        self.PIN_I_G = 8
        self.PIN_I_B = 9
        self.PIN_I_REL_DIM = 10
        self.PIN_I_DIM_RAMP = 11
        self.PIN_O_STATUS_ON_OFF = 1
        self.PIN_O_BRI = 2
        self.PIN_O_R = 3
        self.PIN_O_G = 4
        self.PIN_O_B = 5
        self.PIN_O_REACHABLE = 6

    ########################################################################################################
    #### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
    ###################################################################################################!!!##

    global eventstream_is_connected  # type: bool
    global instances  # type: int

    sbc_data_lock = threading.Lock()

    def log_msg(self, text):
        # type: (str) -> None
        self.DEBUG.add_message("14100: Module ID " + str(self._get_module_id()) + ", " + str(text))

    def log_data(self, key, value):
        # type: (str, any) -> None
        self.DEBUG.set_value("14100: Module ID " + str(self._get_module_id()) + ", " + str(key), str(value))

    def set_output_value_sbc(self, pin, val):
        # type:  (int, any) -> None
        self.sbc_data_lock.acquire()
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                print (str(time.time()) + "\t# SBC: pin " + str(pin) + " <- data not send / " + str(val).decode(
                    "utf-8"))
                self.sbc_data_lock.release()
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val
        self.sbc_data_lock.release()

    def process_json(self, msg):
        # type: (json) -> bool
        supp_fct.log_debug("Entering process_json")
        try:
            out = json.dumps(msg)
        except Exception as e:
            self.log_msg("In process_json #620, " + str(e))
            return False

        if "status" in msg and "data" in msg:
            msg = msg["data"]

        if type(msg) == str:
            msg = json.loads(msg)

        if type(msg) == dict:
            msg = [msg]

        try:
            for msg_entry in msg:
                if "data" not in msg_entry:
                    supp_fct.log_debug("In process_json #629, no 'data' field in '" + msg_entry + "'.")
                    continue

                if type(msg_entry["data"]) == str:
                    msg_entry["data"] = json.loads(msg_entry["data"])

                for data in msg_entry["data"]:
                    device_id = supp_fct.get_val(data, "id")

                    if device_id in self.associated_rids:
                        supp_fct.log_debug("In process_json #646, found data for own ID.")

                        if "on" in data:
                            is_on = bool(data["on"]["on"])
                            self.set_output_value_sbc(self.PIN_O_STATUS_ON_OFF, is_on)

                        bri = 0
                        if "dimming" in data:
                            dimming = data["dimming"]
                            bri = dimming["brightness"]
                            self.curr_bri = bri
                            self.set_output_value_sbc(self.PIN_O_BRI, int(bri))

                        if "color" in data:
                            color = supp_fct.get_val(data, "color")
                            xy = supp_fct.get_val(color, "xy")
                            x = supp_fct.get_val(xy, "x")
                            y = supp_fct.get_val(xy, "y")
                            [r, g, b] = self.xy_bri_to_rgb(x, y, self.curr_bri)
                            self.set_output_value_sbc(self.PIN_O_R, r)
                            self.set_output_value_sbc(self.PIN_O_G, g)
                            self.set_output_value_sbc(self.PIN_O_B, b)

                    else:
                        supp_fct.log_debug("In process_json #662, id " + device_id + " not found in associated ids " +
                                           str(self.associated_rids))

        except Exception as e:
            self.log_msg("In process_json #666, '" + str(e) + "', with message '" + str(out) + "'")

    def get_rid(self):
        # type: () -> [HueGroup_14100_14100.HueDevice]
        # Returns the device of the id given by the user to the module

        rid = str(self._get_input_value(self.PIN_I_ITM_IDX))
        if not rid:
            self.log_msg("In get_rid #652, ITM_ID not set.")
            return None

        my_devices = []
        for device in self.devices.values():
            if rid in device.get_device_ids():
                my_devices.append(device)

        return my_devices


    def prep_dim(self, val):
        """

        :param val:
        :return:
        """
        self.log_msg("Dim cmd, str(val)" + " " + str(type(val)))

        if (type(val) is float) or (type(val) is int):
            val = int(val)
            val = chr(val)
            val = bytearray(val)

        if val[-1] == 0x00:
            self.stop = True
            #self.timer.cancel()
            self.timer = None
            print("abort")
            return

        sgn_bte = int((val[-1] & 0x08) >> 3)
        val = int(val[-1] & 0x07)

        self.interval = round(255.0 / pow(2, val - 1), 0)

        if sgn_bte == 1:
            pass
        else:
            self.interval = int(-1 * self.interval)

        self.stop = False
        self.do_dim()

    def do_dim(self):
        """
        Method to perform the dim
        :return: None
        """
        if self.stop:
            return

        new_bri = int(self.curr_bri + self.interval)
        if new_bri > 255:
            new_bri = 255
        elif new_bri < 1:
            new_bri = 1

        self.set_bri(new_bri)

        duration = float(self._get_input_value(self.PIN_I_DIM_RAMP))
        steps = 255 / abs(self.interval)
        step = float(round(duration / steps, 4))

        self.timer = threading.Timer(step, self.do_dim)
        self.timer.start()

    def eventstream_start(self, key):
        """
        Method to start the eventstream functionality in a thread

        :type key: str
        :param key:
        """
        supp_fct.log_debug("Entering register_eventstream")
        if not get_eventstream_is_connected():
            self.eventstream_thread = threading.Thread(target=self.eventstream, args=(self.eventstream_running, key,))
            self.eventstream_thread.start()

    def eventstream(self, running, key):
        """
        Method exclusively called by *register_eventstream* only

        :type key: str
        :param key:
        :type running: threading.Event
        :param running:

        """
        supp_fct.log_debug("Entering eventstream")
        set_eventstream_is_connected(True)

        msg_sep = "\n\n\r\n"

        sock = socket.socket()

        while running.is_set():
            supp_fct.log_debug("In eventstream #581, connecting...")

            while not hue_bridge.get_bridge_ip():
                supp_fct.log_debug("In eventstream #584, waiting for Hue discovery to connect to eventstream.")
                time.sleep(5)

            api_path = 'https://' + hue_bridge.get_bridge_ip() + '/eventstream/clip/v2'
            url_parsed = urlparse.urlparse(api_path)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_NONE)

            try:
                sock.bind(('', 0))
                sock.connect((hue_bridge.get_bridge_ip(), 443))
                sock.send("GET /eventstream/clip/v2 HTTP/1.1\r\n")
                sock.send("Host: " + url_parsed.hostname + "\r\n")
                sock.send("hue-application-key: " + key + "\r\n")
                sock.send("Accept: text/event-stream\r\n\r\n")

            except Exception as e:
                supp_fct.log_debug("In eventstream #602, disconnecting due to " + str(e))
                sock.close()
                time.sleep(5)
                continue

            data = str()  # type: str

            while running.is_set():
                try:
                    while running.is_set():
                        data = data + sock.recv()
                        if msg_sep in data:
                            break

                except socket.error as e:
                    supp_fct.log_debug(
                        "In eventstream #617, socket error " + str(e.errno) + " '" + str(e.message) + "'")

                msgs = data.split(msg_sep)

                supp_fct.log_debug("In eventstream #621, " + str(len(msgs)) + " messages received.")
                for i in range(len(msgs)):
                    if "data" not in msgs[i]:
                        continue

                    msg = msgs[i][msgs[i].find("data: ") + 6:]
                    try:
                        msg = json.loads(msg)
                        supp_fct.log_debug("In eventstream #629, processing msg '" + json.dumps(msg) + "'.")

                        # store received data / message
                        self.event_list.append(msg)

                    except Exception as e:
                        supp_fct.log_debug("In eventstream #632, '" + str(e) + "'.")
                        continue
                    else:
                        msgs[i] = str()  # remove successful processed msg

                last_msg = msgs[-1]
                if msg_sep in last_msg:
                    index = last_msg.rfind(msg_sep)
                    data = last_msg[index:]  # keep not yet finished messages

        # gently disconnect and wait for re-connection
        sock.close()
        supp_fct.log_debug("In eventstream #644, Disconnected from hue eventstream.")
        time.sleep(4)

        supp_fct.log_debug("In eventstream #647, exit eventstream. No further processing.")
        set_eventstream_is_connected(False)

    def stop_eventstream(self):
        """
        Stops the eventstream thread

        :return:
        """
        try:
            while self.eventstream_thread.is_alive():
                print("Eventstream still living...")
                self.eventstream_running.clear()
                time.sleep(3)
        except AttributeError:
            print("Error in stop_eventstream #889, eventstream not yet initiated (no worries)")
        finally:
            pass

    def on_init(self):

        # debug
        supp_fct.log_debug("entering on_init")
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.g_out_sbc = {}  # type: {int, object}
        self.debug = False  # type: bool

        # global variables
        global instances  # type: int
        try:
            instances = instances + 1
        except NameError:
            instances = 1
        finally:
            self.DEBUG.set_value("Instances", instances)

        # eventstream
        self.eventstream_thread = threading.Thread()  # type: threading.Thread
        self.eventstream_running = threading.Event()
        self.eventstream_running.set()
        self.event_list = []

        # Connections
        hue_bridge.discover_hue(self.FRAMEWORK.get_homeserver_private_ip())
        self.bridge = hue_bridge.HueBridge()
        self.bridge.register_devices(self._get_input_value(self.PIN_I_HUE_KEY),
                                     self._get_input_value(self.PIN_I_ITM_IDX))

        self.bridge.eventstream_start(self._get_input_value(self.PIN_I_HUE_KEY))

        # get own lamp data if already registered
        data = self.get_data("light/" + self.device.light_id)

        if int(data["status"]) == 200:
            self.process_json(data)
        else:
            print("Could not retrieve data for master light id in on_init")

    def on_input_value(self, index, value):
        # Process State
        # itm_idx = str(self._get_input_value(self.PIN_I_ITM_IDX))

        if self._get_input_value(self.PIN_I_HUE_KEY) == "":
            self.log_msg("Hue key not set. Abort processing.")
            return

        # If trigger == 1, get data via web request
        if (self.PIN_I_TRIGGER == index) and (bool(value)):
            item_types = {"device", "light", "room", "scene", "zone", "grouped_light"}

            for item_type in item_types:
                data = self.get_data(item_type)
                self.process_json(data)

        # Process set commands
        if self.PIN_I_ON_OFF == index:
            self.set_on(bool(value))

        elif self.PIN_I_BRI == index:
            self.set_on(True)
            self.set_bri(int(value))

        elif self.PIN_I_ITM_IDX == index:
            self.init_device_list()
            self.register_devices()

            # get own lamp data if registered
            data = self.get_data("light/" + self.device.light_id)

            if data["status"] == 200:
                self.process_json(data)
            else:
                print("Could not retrieve data for master light id in on_init")

        # # todo set rgb
        elif ((self.PIN_I_R == index) or
              (self.PIN_I_G == index) or
              (self.PIN_I_B == index)):

            self.set_on(True)
            r = int(int(self._get_input_value(self.PIN_I_R)))
            g = int(int(self._get_input_value(self.PIN_I_G)))
            b = int(int(self._get_input_value(self.PIN_I_B)))

            self.set_color_rgb(r, g, b)

        # todo do relative dim
        elif self.PIN_I_REL_DIM == index:
            self.prep_dim(value)


def get_eventstream_is_connected():
    # type: () -> bool
    global eventstream_is_connected_lock
    try:
        eventstream_is_connected_lock.locked()
    except NameError:
        eventstream_is_connected_lock = threading.Lock()
    finally:
        eventstream_is_connected_lock.acquire()

    global eventstream_is_connected
    try:
        if eventstream_is_connected:
            pass
    except NameError:
        eventstream_is_connected = False

    ret = eventstream_is_connected
    eventstream_is_connected_lock.release()
    return ret


def set_eventstream_is_connected(is_connected):
    # type: (bool) -> bool
    global eventstream_is_connected_lock
    try:
        eventstream_is_connected_lock.locked()
    except NameError:
        eventstream_is_connected_lock = threading.Lock()
    finally:
        eventstream_is_connected_lock.acquire()

    global eventstream_is_connected  # type: bool
    eventstream_is_connected = is_connected
    eventstream_is_connected_lock.release()
    return is_connected



############################################


class UnitTests(unittest.TestCase):

    def setUp(self):
        print("\n### setUp")
        with open("credentials.json") as f:
            self.cred = json.load(f)

        self.dummy = HueGroup_14100_14100(0)

        self.dummy.debug_input_value[self.dummy.PIN_I_HUE_KEY] = self.cred["PIN_I_SUSER"]
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_light_id_studio"]
        # self.dummy.debug_rid = self.cred["hue_light_id"]

        # self.dummy.on_init()
        self.dummy.DEBUG = self.dummy.FRAMEWORK.create_debug_section()
        self.dummy.g_out_sbc = {}  # type: {int, object}
        self.dummy.debug = False  # type: bool
        hue_bridge.set_bridge_ip(self.cred["PIN_I_SHUEIP"])

        self.dummy.FRAMEWORK.my_ip = self.cred["my_ip"]

        self.device = hue_lib.hue_item.HueDevice()
        self.device.id = self.cred["hue_light_id_studio"]
        self.device.rtype = "light"

        self.ip = self.cred["PIN_I_SHUEIP"]
        self.key = self.cred["PIN_I_SUSER"]
        self.scene_dyn = self.cred["hue_dyn_scene_studio"]

    def tearDown(self):
        print("\n### tearDown")
        try:
            self.dummy.stop_server()
            self.dummy.stop_eventstream()
            del self.dummy
        except:
            pass
        finally:
            pass

    def test_08_print_devices(self):
        print("\n### ###test_08_print_devices")

        hue_bridge.set_bridge_ip(self.ip)

        bridge = hue_bridge.HueBridge()
        amount = bridge.register_devices(self.key, self.device.id)
        self.assertTrue(amount > 0)

        html_page = bridge.get_html_device_list()
        with open("../tests/debug_server_return.html", 'w') as out_file:
            out_file.write(html_page)

        self.assertTrue(len(html_page) > 0)

    def test_08_server(self):
        print("\n### ###test_08_server")

        server = html_server.HtmlServer()
        server.run_server(self.dummy.FRAMEWORK.get_homeserver_private_ip(), 8080)

        text = "Hello World!"
        server.set_html_content(text)

        time.sleep(1)

        api_path = 'http://' + self.dummy.FRAMEWORK.get_homeserver_private_ip() + ':8080'
        url_parsed = urlparse.urlparse(api_path)
        headers = {'Host': url_parsed.hostname}
        request = urllib2.Request(api_path, headers=headers)
        response = urllib2.urlopen(request, data=None, timeout=5)
        data = response.read()

        self.assertEqual(response.getcode(), 200)
        self.assertEqual(data, text)

    def test_09_singleton_eventstream(self):
        print("test_09_singleton_eventstream")

        module_1 = HueGroup_14100_14100(0)
        module_2 = HueGroup_14100_14100(0)

        module_1.on_init()
        module_2.on_init()
        time.sleep(3)

        self.assertTrue(module_2.get_eventstream_is_connected())

    def test_10_eventstream_reconnect(self):
        print("\n### test_10_eventstream_reconnect")
        self.assertTrue(False, "Test not implemented")

    def test_11_discover(self):
        print("\n###test_11_discover")
        self.dummy.bridge_ip = None
        msg, ip = hue_bridge.discover_hue(self.dummy.FRAMEWORK.get_homeserver_private_ip())
        print msg

        self.assertTrue("192" in hue_bridge.get_bridge_ip(), "### IP not discovered")

    def test_12_set_on_off_light(self):
        print("\n### test_12_set_on_off_light")

        ret = self.device.set_on(self.ip, self.key, False)
        self.assertTrue(ret)
        time.sleep(3)

        ret = self.device.set_on(self.ip, self.key, True)
        self.assertTrue(ret)
        time.sleep(3)

        ret = self.device.set_on(self.ip, self.key, False)
        self.assertTrue(ret)
        time.sleep(3)

        ret = self.device.set_on(self.ip, "0", False)
        self.assertFalse(ret)

    def test_14_on_off_zone(self):
        # on / off not available for zones, so just chek that nothing happens
        print("\n### test_14_on_off_zone")
        self.dummy.on_init()
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_zone_id"]
        self.dummy.on_init()

        time.sleep(3)
        ret = self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, True)
        self.assertFalse(ret)

    def test_15_on_off_room(self):
        # on / off not available for rooms, so just chek that nothing happens
        print("\n### test_15_on_off_room")
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_room_id"]
        self.dummy.on_init()

        time.sleep(3)
        ret = self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, True)
        self.assertFalse(ret)

    def test_16_eventstream_on_off(self):
        print("\n### test_16_eventstream_on_off")
        self.dummy.on_init()

        time.sleep(2)
        self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, False)
        time.sleep(3)
        self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, True)
        time.sleep(3)
        self.dummy.eventstream_running.clear()
        self.assertTrue(self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF])
        time.sleep(5)
        print(str(time.time()) + "\t+++ End +++")

    def test_17_dimming(self):
        print("\n### test_17_dimming")
        self.dummy.on_init()
        self.dummy.eventstream_running.clear()
        time.sleep(2)
        print("------ On")
        self.dummy.set_on(True)
        time.sleep(2)
        print("------ 70%")
        res = self.dummy.set_bri(70)
        self.assertTrue(res)
        time.sleep(2)
        print("------ 30%")
        self.dummy.on_input_value(self.dummy.PIN_I_BRI, 30)
        time.sleep(2)
        res = abs(30 - float(self.dummy.debug_output_value[self.dummy.PIN_O_BRI]))
        self.assertTrue(res <= 1, "#1153")
        print("------ off")
        self.dummy.eventstream_running.set()
        self.dummy.set_on(False)
        time.sleep(2)

    def test_18_get_data(self):
        print("\n### test_get_data")
        self.dummy.on_init()
        self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF] = None
        self.dummy.g_out_sbc = {}

        self.dummy.on_input_value(self.dummy.PIN_I_TRIGGER, 1)
        res = self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF]

        self.assertTrue(bool == type(res))

    def test_19_xy_to_rgb(self):
        print("\n### test_19_xy_to_rgb")
        [r, g, b] = supp_fct.xy_bri_to_rgb(0.4849, 0.3476, 1)
        self.assertEqual([255, 165, 135], [r, g, b], "#1217")

        [r, g, b] = supp_fct.xy_bri_to_rgb(0.640, 0.330, 0.1043)
        self.assertEqual([125, 0, 0], [r, g, b], "#1220")

    def test_19_rgb_to_xy(self):
        print("\n### test_19_rgb_to_xy")
        [x, y, bri] = supp_fct.rgb_to_xy_bri(255, 0, 0)
        self.assertEqual([0.675, 0.322, 1], [x, y, bri], "#1153")

    def test_19_set_color(self):
        print("\n### test_19_set_color")
        ret = self.device.set_color_rgb(self.ip, self.key, 255, 0, 0)
        self.assertTrue(ret)

    def test_dynamic_scene(self):
        print("\n### test_dynamic_scene")
        ret = self.device.set_dynamic_scene(self.ip, self.key, self.scene_dyn)
        self.assertTrue(ret)


#     def test_dim(self):
#         self.dummy.debug = True
#         self.dummy.curr_bri = 255
#
#         api_url = "192.168.0.10"
#         api_port = "80"
#         api_user = "debug"
#         group = "1"
#         light = 3
#
#         self.dummy.prep_dim(0x85)
#         self.assertEqual(-16, self.dummy.interval)
# #        self.assertEqual(10, self.dummy.timer.interval)
#         time.sleep(3)
#         self.dummy.prep_dim(0.0)
#         # self.assertEqual(dummy.g_timer.interval, 1000)
#         # self.assertFalse(dummy.g_timer.is_alive())
#
#         self.dummy.prep_dim(0x8d)
#         self.assertEqual(16, self.dummy.interval)
# #        self.assertEqual(10, self.dummy.timer.interval)
#         time.sleep(3)
#         self.dummy.prep_dim(0.0)
#         # self.assertEqual(dummy.g_timer.interval, 1000)
#         # self.assertFalse(dummy.g_timer.is_alive())


if __name__ == '__main__':
    unittest.main()
