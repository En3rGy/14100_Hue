# coding: utf8
# import struct
import hue_lib.hue_item as hue_item
import hue_lib.hue_bridge as hue_bridge
import hue_lib.supp_fct as supp_fct
import hue_lib.html_server as html_server
import hue_lib.singleton as singlet

import unittest
import ssl
import urllib2
import urlparse
import socket
import time
import json
import threading
import random


class hsl20_4:
    LOGGING_NONE = 0

    def __init__(self):
        self.module_id = random.randint(1, 1000)
        pass

    def _get_module_id(self):
        """
        Helper function to get ID of module.

        :return: Module ID
        :rtype: str
        """
        return self.module_id

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
            """

            :return: module id
            :rtype: int
            """
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
            # type: (int) -> HueGroup_14100_14100
            return HueGroup_14100_14100(0)

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
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_TRIGGER=1
        self.PIN_I_HUE_KEY=2
        self.PIN_I_PORT=3
        self.PIN_I_ITM_IDX=4
        self.PIN_I_SCENE=5
        self.PIN_I_DYN_SCENE=6
        self.PIN_I_DYN_SC_SPEED=7
        self.PIN_I_ON_OFF=8
        self.PIN_I_BRI=9
        self.PIN_I_R=10
        self.PIN_I_G=11
        self.PIN_I_B=12
        self.PIN_I_REL_DIM=13
        self.PIN_I_DIM_RAMP=14
        self.PIN_O_STATUS_ON_OFF=1
        self.PIN_O_BRI=2
        self.PIN_O_R=3
        self.PIN_O_G=4
        self.PIN_O_B=5
        self.PIN_O_REACHABLE=6

    ########################################################################################################
    #### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
    ###################################################################################################!!!##

    global eventstream_is_connected  # type: bool

    sbc_data_lock = threading.Lock()

    def log_msg(self, text):
        # type: (str) -> None
        device = self.bridge.get_own_device(self._get_input_value(self.PIN_I_ITM_IDX))
        intro = "HSID" + str(self._get_module_id()) + ", " + device.room_name + " " + device.name + ": "
        self.DEBUG.add_message(intro + str(text))

    def log_data(self, key, value):
        # type: (str, any) -> None
        device = self.bridge.get_own_device(self._get_input_value(self.PIN_I_ITM_IDX))
        intro = "HSID" + str(self._get_module_id()) + ", " + device.room_name + " " + device.name + ": "
        self.DEBUG.set_value(intro + str(key), str(value))

    def set_output_value_sbc(self, pin, val):
        # type:  (int, any) -> None
        self.sbc_data_lock.acquire()
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                supp_fct.log_debug("SBC: pin " + str(pin) + " <- data not send / " + str(val).decode("utf-8"))
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
            hue_device = self.bridge.get_own_device(self._get_input_value(self.PIN_I_ITM_IDX))

            for msg_entry in msg:
                if "data" not in msg_entry:
                    self.log_data("In process_json #183, no 'data' field",  msg_entry)
                    continue

                if type(msg_entry["data"]) == str:
                    msg_entry["data"] = json.loads(msg_entry["data"])

                for data in msg_entry["data"]:
                    device_id = supp_fct.get_val(data, "id")

                    if device_id not in hue_device.get_device_ids():
                        pass

                    else:
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
                            [r, g, b] = supp_fct.xy_bri_to_rgb(x, y, self.curr_bri)
                            r = int(r / 255.0 * 100)
                            g = int(g / 255.0 * 100)
                            b = int(b / 255.0 * 100)
                            self.set_output_value_sbc(self.PIN_O_R, r)
                            self.set_output_value_sbc(self.PIN_O_G, g)
                            self.set_output_value_sbc(self.PIN_O_B, b)

                        if supp_fct.get_val(data, "type") == "zigbee_connectivity":
                            if "status" in data:
                                self.set_output_value_sbc(self.PIN_O_REACHABLE, data["status"] == "connected")

        except Exception as e:
            self.log_data("Error in process_json #239", str(e) + " with\n\n" + str(out))

    def eventstream_start(self, key):
        """
        Method to start the eventstream functionality in a thread

        :type key: str
        :param key:
        """
        supp_fct.log_debug("Entering register_eventstream")
        if not get_eventstream_is_connected():
            self.eventstream_keep_running.set()
            self.eventstream_thread = threading.Thread(target=self.eventstream, args=(self.eventstream_keep_running, key,))
            self.eventstream_thread.start()

    def eventstream(self, running, key):
        """
        Method exclusively called by *register_eventstream* only

        :type key: str
        :param key:
        :type running: threading.Event
        :param running:
        """
        self.log_msg("Starting to connect to eventstream.")
        host_ip = self.FRAMEWORK.get_homeserver_private_ip()

        if not self.eventstream_keep_running.is_set():
            self.log_msg("Tried to connect to eventstream but self.eventstream_keep_running not set.")

        # msg_sep = "\n\n\r\n"
        msg_sep = "\n"

        sock = socket.socket()

        # in_file = open("../tests/eventstream_in.txt", 'w')
        # pro_file = open("../tests/eventstream_pro.txt", 'w')

        # get  connection loop
        while self.eventstream_keep_running.is_set():
            while not hue_bridge.get_bridge_ip(host_ip) and self.eventstream_keep_running.is_set():
                self.log_msg("In eventstream #277, waiting for Hue discovery to connect to eventstream.")
                time.sleep(5)

            api_path = 'https://' + hue_bridge.get_bridge_ip(host_ip) + '/eventstream/clip/v2'
            url_parsed = urlparse.urlparse(api_path)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_NONE)

            try:
                sock.bind(('', 0))
                sock.connect((hue_bridge.get_bridge_ip(host_ip), 443))
                set_eventstream_is_connected(True)
                sock.send("GET /eventstream/clip/v2 HTTP/1.1\r\n")
                sock.send("Host: " + url_parsed.hostname + "\r\n")
                sock.send("hue-application-key: " + key + "\r\n")
                sock.send("Accept: text/event-stream\r\n\r\n")

            except Exception as e:
                self.log_msg("In eventstream #274, disconnecting due to " + str(e))
                sock.close()
                set_eventstream_is_connected(False)
                time.sleep(5)
                continue

            self.log_msg("Connected to eventstream")

            # receive data loop
            while self.eventstream_keep_running.is_set():
                data = str()  # type: str
                try:
                    while self.eventstream_keep_running.is_set():
                        new_data = sock.recv()
                        data = data + new_data
                        # in_file.write("|<>|" + new_data)

                        # Received at least 1 complete msg
                        if data[-1] == msg_sep:
                            break

                except socket.error as e:
                    self.log_msg(
                        "In eventstream #291, socket error " + str(e.errno) + " '" + str(e.message) + "'")
                    set_eventstream_is_connected(False)
                    break

                msgs = data.split(msg_sep)
                supp_fct.log_debug("In eventstream #297, " + str(len(msgs)) + " lines received.")

                for msg in msgs:
                    if msg[:6] != "data: ":
                        continue

                    msg = msg[6:]
                    try:
                        # pro_file.write(msg + "\n")
                        msg = json.loads(msg)

                        # store received data / message
                        modules = singlet.get_module_register()
                        for module_id in modules:
                            if module_id == self._get_module_id():
                                continue
                            module_instance = self.FRAMEWORK.get_instance_by_id(module_id)
                            try:
                                module_instance.process_json(msg)
                            except Exception as e:
                                self.log_msg("In eventstream #336, calling remote modules, '" + str(e) + "'.")

                        self.process_json(msg)

                    except Exception as e:
                        self.log_msg("Eventstream #342, error with '" + e.message[:len(e.message)] + "'.")
                        self.log_data("Eventstream #342 error msg", str(e))
                        self.log_data("Eventstream #342 erroneous str", msg)

        # gently disconnect and wait for re-connection
        sock.close()
        self.log_msg("In eventstream #395, Disconnected from hue eventstream.")
        time.sleep(4)
        set_eventstream_is_connected(False)

    def stop_eventstream(self):
        """
        Stops the eventstream thread

        :return:
        """
        self.log_msg("Entering stop_eventstream")
        try:
            while self.eventstream_thread.is_alive():
                supp_fct.log_debug("Eventstream still living...")
                self.eventstream_keep_running.clear()
                time.sleep(3)
        except AttributeError as e:
            supp_fct.log_debug("Error in stop_eventstream #342 (no worries), " + e.message)
        finally:
            pass

    def do_init(self):
        """

        :return: False if errors occur
        :rtype: bool
        """
        key = self._get_input_value(self.PIN_I_HUE_KEY)
        device_id = self._get_input_value(self.PIN_I_ITM_IDX)
        self.bridge = hue_bridge.HueBridge()
        self.server = html_server.HtmlServer()
        self.singleton = singlet.Singleton(self._get_module_id())

        # Connections
        ip = hue_bridge.get_bridge_ip(self.FRAMEWORK.get_homeserver_private_ip())

        if ip == str():
            self.log_msg("No connection to bridge available.")
            return False

        if self.singleton.is_master():
            self.log_data("Hue bridge IP", str(ip))
            amount = self.bridge.register_devices(key, device_id, self.FRAMEWORK.get_homeserver_private_ip())
            self.log_data("Hue devices", amount)

            # server
            server_port = self._get_input_value(self.PIN_I_PORT)
            self.server.run_server(self.FRAMEWORK.get_homeserver_private_ip(), server_port)
            self.server.set_html_content(self.bridge.get_html_device_list())
            link = self.FRAMEWORK.get_homeserver_private_ip() + ":" + str(server_port)
            self.log_data("Info-Server", 'http://' + link)

        # get own lamp data if already registered
        device = self.bridge.get_own_device(device_id)
        data = supp_fct.get_data(ip, key, "light/" + device.light_id)

        if int(data["status"]) == 200:
            self.process_json(data)
        else:
            self.log_msg("Could not retrieve data for master light id in on_init")

        data = supp_fct.get_data(ip, key, "zigbee_connectivity/" + device.zigbee_connectivity_id)
        if int(data["status"]) == 200:
            self.process_json(data)
        else:
            self.log_msg("Could not retrieve zigbee connectivity data for master light")

        if self.singleton.is_master():
            # eventstream init & start
            self.eventstream_thread = threading.Thread()  # type: threading.Thread
            self.eventstream_keep_running = threading.Event()
            self.event_list = []
            self.eventstream_start(key)

        self.log_data("Hue ID", device.id + "\n" + device.rtype)
        return True

    def on_init(self):
        # debug
        supp_fct.log_debug("Entering on_init")
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.g_out_sbc = {}  # type: {int, object}
        self.debug = False  # type: bool

        self.do_init()
        supp_fct.log_debug("Leaving on_init")

    def on_input_value(self, index, value):
        # Process State
        # itm_idx = str(self._get_input_value(self.PIN_I_ITM_IDX))

        ip = hue_bridge.get_bridge_ip(self.FRAMEWORK.get_homeserver_private_ip())
        if ip == str():
            if not self.do_init():
                self.log_msg("Received new input but could not establish connection to bridge.")
                return

        device = self.bridge.get_own_device(self._get_input_value(self.PIN_I_ITM_IDX))
        key = self._get_input_value(self.PIN_I_HUE_KEY)

        if self._get_input_value(self.PIN_I_HUE_KEY) == "":
            self.log_msg("Hue key not set. Abort processing updated input.")
            return

        if not get_eventstream_is_connected():
            self.eventstream_start(key)

        # If trigger == 1, get data via web request
        if (self.PIN_I_TRIGGER == index) and (bool(value)):
            self.log_msg("Received Trigger input.")
            item_types = {"device", "light", "room", "scene", "zone", "grouped_light"}

            for item_type in item_types:
                data = supp_fct.get_data(ip, key, item_type)
                self.process_json(data)

        # Process set commands
        if self.PIN_I_ON_OFF == index:
            self.log_msg("Received on/off command.")
            device.set_on(ip, key, bool(value))

        elif self.PIN_I_SCENE == index:
            self.log_msg("Received scene input.")
            scene = hue_item.HueDevice()
            scene.id = value
            scene.rtype = "scene"
            scene.set_scene(ip, key, value)

        elif index == self.PIN_I_DYN_SCENE or index == self.PIN_I_DYN_SC_SPEED:
            dynamic_scene = self._get_input_value(self.PIN_I_DYN_SCENE)  # type: str
            speed = self._get_input_value(self.PIN_I_DYN_SC_SPEED)
            if not dynamic_scene:
                return

            if speed <= 0 or speed > 1:
                self.log_msg("Call of dynamic scene erroneous, speed shall be 0-1")
                return

            device.set_dynamic_scene(ip, key, dynamic_scene, speed)

        elif self.PIN_I_BRI == index:
            self.log_msg("Received Bri input.")
            device.set_on(ip, key, True)
            device.set_bri(ip, key, int(value))

        elif self.PIN_I_ITM_IDX == index:
            self.log_msg("Received Item Index input.")
            self.bridge.register_devices(key, value, self.FRAMEWORK.get_homeserver_private_ip())
            device = self.bridge.get_own_device(value)

            # get own lamp data if registered
            data = supp_fct.get_data(ip, key, "light/" + device.light_id)

            if data["status"] == 200:
                self.process_json(data)
            else:
                print("Could not retrieve data for master light id in on_init")

        elif ((self.PIN_I_R == index) or
              (self.PIN_I_G == index) or
              (self.PIN_I_B == index)):
            self.log_msg("Received r/g/b input.")

            r = int(int(self._get_input_value(self.PIN_I_R)))
            g = int(int(self._get_input_value(self.PIN_I_G)))
            b = int(int(self._get_input_value(self.PIN_I_B)))

            if r == 0 and g == 0 and b == 0:
                device.set_on(ip, key, False)
                return

            device.set_on(ip, key, True)
            device.set_color_rgb(ip, key, r, g, b)

        elif self.PIN_I_REL_DIM == index:
            device.prep_dim(ip, key, value, self._get_input_value(self.PIN_I_DIM_RAMP))


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
        self.dummy.g_out_sbc = {}
        self.dummy.debug = False
        hue_bridge.set_bridge_ip(self.cred["PIN_I_SHUEIP"])

        self.dummy.FRAMEWORK.my_ip = self.cred["my_ip"]

        self.device = hue_item.HueDevice()
        self.device.id = self.cred["hue_light_id_studio"]
        self.device.rtype = "light"

        self.ip = self.cred["PIN_I_SHUEIP"]
        self.key = self.cred["PIN_I_SUSER"]
        self.scene_dyn = self.cred["hue_dyn_scene_studio"]

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

    def test_08_print_devices(self):  # 2022-11-16 OK
        print("\n### ###test_08_print_devices")

        hue_bridge.set_bridge_ip(self.ip)

        bridge = hue_bridge.HueBridge()
        amount = bridge.register_devices(self.key, self.device.id, self.dummy.FRAMEWORK.get_homeserver_private_ip())
        self.assertTrue(amount > 0)

        html_page = bridge.get_html_device_list()
        with open("../tests/debug_server_return.html", 'w') as out_file:
            out_file.write(html_page)

        self.assertTrue(len(html_page) > 0)

    def test_08_server(self):  # 2022-11-16 OK
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

        self.assertTrue(get_eventstream_is_connected())

    def test_log_eventstream(self):
        # ec86940a-ce69-414d-9b6c-81e50793f8c4
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = "ec86940a-ce69-414d-9b6c-81e50793f8c4"
        self.dummy.on_init()
        time.sleep(30)

    def test_10_16_eventstream(self):  # 2022-11-16 OK
        print("\n### test_10_eventstream")
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = "fbbd07de-5bf0-4dd6-b819-db3d9ee9a429"
        self.dummy.on_init()
        time.sleep(2)

        # self.device.set_on(self.ip, self.key, False)
        # time.sleep(2)
        # ret = self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF]
        # self.assertFalse(ret)

        # self.device.set_on(self.ip, self.key, True)
        # time.sleep(2)
        # ret = self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF]
        # self.assertTrue(ret)

        print("\n\nTest on your own :)\n\n")
        time.sleep(20)

    def test_10_eventstream_reconnect(self):  # 2022-11-17 OK
        print("\n### test_10_eventstream_reconnect")
        self.dummy.on_init()
        time.sleep(2)
        self.assertTrue(get_eventstream_is_connected())

        print("Disconnect network")
        time.sleep(10)
        print("Continuing")
        self.assertFalse(get_eventstream_is_connected())

        print("Reconnect network")
        time.sleep(10)
        print("Continuing")
        self.assertFalse(get_eventstream_is_connected())

    def test_11_discover(self):  # 2022-11-16 OK
        print("\n###test_11_discover")
        self.dummy.bridge_ip = None
        msg, ip = hue_bridge.discover_hue(self.dummy.FRAMEWORK.get_homeserver_private_ip())
        print msg

        self.assertTrue("192" in hue_bridge.get_bridge_ip(self.dummy.FRAMEWORK.get_homeserver_private_ip()),
                        "### IP not discovered")

    def test_12_set_on_off_light(self):  # 2022-11-16 OK
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

    def test_on_off_grouped_light(self):
        print("\n### test_on_off_grouped_light")

        rid = self.cred["hue_grouped_light"]

        self.device = hue_item.HueDevice()
        self.device.id = rid
        self.device.rtype = "grouped_light"

        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = rid

        ret = self.device.set_on(self.ip, self.key, False)
        self.assertTrue(ret)
        time.sleep(3)

        ret = self.device.set_on(self.ip, self.key, True)
        self.assertTrue(ret)
        time.sleep(3)

        ret = self.device.set_on(self.ip, "0", False)
        self.assertFalse(ret)
        time.sleep(3)

        ret = self.device.set_on(self.ip, self.key, True)
        self.assertTrue(ret)

    def test_14_on_off_zone(self):
        # on / off not available for zones, so just chek that nothing happens
        print("\n### test_14_on_off_zone")
        rid = self.cred["hue_zone_id"]

        bridge = hue_bridge.HueBridge()
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

        bridge = hue_bridge.HueBridge()
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

    def test_18_get_data(self):  # 2022-11-16 OK
        print("\n### test_get_data")
        ret = supp_fct.get_data(self.ip, self.key, "light")
        self.assertTrue("data" in ret)
        self.assertTrue("status" in ret)
        self.assertTrue(len(ret["data"]) > 0)
        self.assertEqual(int(200), int(ret["status"]))

        ret = supp_fct.get_data(self.ip, self.key, "error")
        self.assertNotEqual(int(ret["status"]), 200)

    def test_19_xy_to_rgb(self):
        print("\n### test_19_xy_to_rgb")
        [r, g, b] = supp_fct.xy_bri_to_rgb(0.675, 0.322, 1)
        self.assertEqual([255, 0, 0], [r, g, b], "red")

        [r, g, b] = supp_fct.xy_bri_to_rgb(0.4091, 0.518, 1)
        self.assertEqual([0,128,0], [r, g, b], "red")

        [r, g, b] = supp_fct.xy_bri_to_rgb(0.3495,0.2545, 1)
        self.assertEqual([221,160,221], [r, g, b], "red")

    def test_19_rgb_to_xy(self):  # 2022-11-16 OK
        # rgb(255,0,0) 	xy(0.675,0.322)
        # rgb(0,128,0) 	xy(0.4091,0.518)
        # rgb(221,160,221) 	xy(0.3495,0.2545)
        print("\n### test_19_rgb_to_xy")
        [x, y, bri] = supp_fct.rgb_to_xy_bri(255, 0, 0)
        self.assertEqual([0.675, 0.322, 1], [round(x, 4), round(y, 4), bri], "red")
        [x, y, bri] = supp_fct.rgb_to_xy_bri(0, 128, 0)
        self.assertEqual([0.4091, 0.518, 1], [round(x, 4), round(y, 4), bri], "lime")
        [x, y, bri] = supp_fct.rgb_to_xy_bri(221, 160, 221)
        self.assertEqual([0.3495, 0.2545, 1], [round(x, 4), round(y, 4), bri], "plum")

    def test_19_set_color(self):  # 2022-11-16 OK
        print("\n### test_19_set_color")
        ret = self.device.set_color_rgb(self.ip, self.key, 100, 0, 0)
        self.assertTrue(ret)

    def test_20_reachable(self):  # 2022-11-18 OK
        print("\n### test_20_reacable")
        ret = supp_fct.get_data(self.ip, self.key, "zigbee_connectivity/" + self.cred["hue_zigbee_studio"])
        self.assertTrue("data" in ret)
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

    def test_inputs(self):
        print("\n### test_inputs")
        del self.device
        del self.ip
        del self.key
        hue_bridge.set_bridge_ip(str())

        self.dummy.on_init()
        time.sleep(5)
        print("\n\nPIN_I_ON_OFF ################################################\n\n")

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
        self.assertEqual(1, self.dummy.debug_output_value[self.dummy.PIN_O_BRI])

        print("\n\nPIN_I_SCENE ################################################\n\n")
        self.dummy.on_input_value(self.dummy.PIN_I_SCENE, self.cred["hue_scene_id"])

        """
        self.dummy.PIN_I_HUE_KEY = 2
        self.dummy.PIN_I_PORT = 3
        self.dummy.PIN_I_ITM_IDX = 4
        self.dummy.PIN_I_DIM_RAMP = 11
        """
    def test_23_non_blocking(self):
        print("\n### test_23_non_blocking")

        supp_fct.log_debug("Disconnect network")
        time.sleep(10)
        supp_fct.log_debug("continue...")

        del self.device
        del self.ip
        del self.key
        hue_bridge.set_bridge_ip(str())

        self.dummy.on_init()

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
