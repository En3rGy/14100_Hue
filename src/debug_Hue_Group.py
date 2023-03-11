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
import select
import logging


class hsl20_4:
    LOGGING_NONE = 0

    def __init__(self):
        self.module_id = random.randint(1, 1000)
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
            pass

        def _set_input_value(self, pin, value):
            # type: (int, any) -> None
            self.debug_input_value[int(pin)] = value
            print "# IN: Pin " + str(pin) + " -> \t" + str(value)

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
            curr_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print("{time}\t# SET VAL # {caption} -> {data}".format(time=curr_time, caption=cap, data=text))

        def add_message(self, msg):
            curr_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print("{time}\t# ADD MSG # {msg}".format(time=curr_time, msg=msg))

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
        self.PIN_I_SCENE = 5
        self.PIN_I_DYN_SCENE = 6
        self.PIN_I_DYN_SC_SPEED = 7
        self.PIN_I_ON_OFF = 8
        self.PIN_I_BRI = 9
        self.PIN_I_R = 10
        self.PIN_I_G = 11
        self.PIN_I_B = 12
        self.PIN_I_REL_DIM = 13
        self.PIN_I_DIM_RAMP = 14
        self.PIN_O_STATUS_ON_OFF = 1
        self.PIN_O_BRI = 2
        self.PIN_O_R = 3
        self.PIN_O_G = 4
        self.PIN_O_B = 5
        self.PIN_O_REACHABLE = 6

        ########################################################################################################
        #### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
        ###################################################################################################!!!##

        self.logger = logging.getLogger("{}".format(random.randint(0, 9999999)))

        # Create a custom logging level TRACE
        logging.addLevelName(TRACE, "TRACE")

        def trace(self, message, *args, **kws):
            if self.isEnabledFor(TRACE):
                self._log(TRACE, message, args, **kws)

        logging.Logger.trace = trace

        self.bridge = hue_bridge.HueBridge(self.logger)
        self.server = html_server.HtmlServer(self.logger)
        self.singleton = None
        self.eventstream_thread = threading.Thread()  # type: threading.Thread
        self.eventstream_keep_running = threading.Event()
        self.event_list = []
        self.msg_last = str()
        self.curr_bri = 0
        self.g_out_sbc = {}  # type: {int, object}
        self.debug = False  # type: bool

    global eventstream_is_connected  # type: bool
    sbc_data_lock = threading.Lock()

    class FunctionHandler(logging.Handler):
        def __init__(self, framework_debug, module_id):
            self.framework_debug = framework_debug
            self.module_id = module_id
            super(HueGroup_14100_14100.FunctionHandler, self).__init__()

        def emit(self, record):
            self.framework_debug.add_message("{level}:Module {id}:{msg}".format(id=self.module_id,
                                                                                msg=record.getMessage(),
                                                                                level=record.levelname))

    def log_data(self, key, value):
        # type: (str, any) -> None
        device = self.bridge.get_own_device(self._get_input_value(self.PIN_I_ITM_IDX))
        intro = "Module {}:{}/{}:{}".format(self._get_module_id(), device.room_name, device.name, key)
        self.DEBUG.set_value(intro, str(value))

    def set_output_value_sbc(self, pin, val):
        # type:  (int, any) -> None
        with supp_fct.TraceLog(self.logger):
            self.sbc_data_lock.acquire()
            if pin in self.g_out_sbc:
                if self.g_out_sbc[pin] == val:
                    self.logger.debug("SBC: Pin {} <- data not send ({})".format(pin, str(val).decode("utf-8")))
                    self.sbc_data_lock.release()
                    return

            self._set_output_value(pin, val)
            self.logger.debug("OUT: Pin {} <-\t{}".format(pin, val))
            self.g_out_sbc[pin] = val
            self.sbc_data_lock.release()

    def process_json(self, msg):
        # type: (json) -> bool
        with supp_fct.TraceLog(self.logger):
            try:
                out = json.dumps(msg)
            except Exception as e:
                self.logger.error("In process_json #620, " + str(e))
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
                        self.log_data("In process_json #183, no 'data' field", msg_entry)
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
                                gamut_type = supp_fct.get_val(color, "gamut_type")
                                hue_device.gamut_type = gamut_type
                                xy = supp_fct.get_val(color, "xy")
                                x = supp_fct.get_val(xy, "x")
                                y = supp_fct.get_val(xy, "y")
                                [r, g, b] = supp_fct.xy_bri_to_rgb(x, y, self.curr_bri, hue_device.gamut_type)
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
                self.log_data("Error in process_json #239", "'{}' with:\n'{}'\n\n".format(str(e), str(out)))

    def eventstream_start(self, key):
        """
        Method to start the eventstream functionality in a thread

        :type key: str
        :param key:
        """
        with supp_fct.TraceLog(self.logger):
            self.eventstream_keep_running.set()
            set_eventstream_is_connected(True)
            self.eventstream_thread = threading.Thread(target=self.eventstream,
                                                       args=(self.eventstream_keep_running, key,))
            self.eventstream_thread.start()

    def handle_connection(self, conn):
        """
        Handle the connection to the socket.

        :param conn: A socket object representing the connection.
        :type conn: socket.socket
        :return: A list of valid messages received from the connection.
        :rtype: list of str
        """
        with supp_fct.TraceLog(self.logger):
            data = self.msg_last
            start_time = time.time()  # todo: Gently disconnect for reconnection
            while self.eventstream_keep_running.is_set() and get_eventstream_is_connected():

                if time.time() - start_time > EVENTSTREAM_RECONNECT_ELAPSE:
                    self.logger.debug("Gently disconnecting from eventstream for a planned re-connect.")
                    conn.close()
                    set_eventstream_is_connected(False)
                    return []

                ready = select.select([conn], [], [], EVENTSTREAM_TIMEOUT)
                if ready[0]:
                    new_data = conn.recv(4096)  # read data

                    if not new_data:  # Connection closed
                        self.logger.warning("Eventstream closed.")
                        set_eventstream_is_connected(False)
                        return []

                    self.logger.debug("Received {} bytes via eventstream.".format(len(new_data)))
                    data += new_data
                    msgs = data.split(MSG_SEP)  # is ending with seperator, an empty element will be attached
                    self.msg_last = msgs[-1]  # store last( incomplete or empty) msg for later usage

                    valid_msgs = [msg[6:] for msg in msgs[:-1] if len(msg) > 6 and msg[:6] == "data: "]
                    return valid_msgs  # return all complete messages
                else:
                    pass
                    # self.logger.debug("No data available on socket.")

            set_eventstream_is_connected(False)

    def process_eventstream_msgs(self, msgs):
        """
        Process the messages received from the eventstream.

        :param msgs: A list of messages received from the eventstream.
        :type msgs: list of str
        :return: None
        """
        with supp_fct.TraceLog(self.logger):
            if not msgs:
                return
            for msg in msgs:
                try:
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
                            self.logger.warning("In eventstream #336, calling remote modules, '" + str(e) + "'.")

                    self.process_json(msg)

                except Exception as e:
                    self.logger.error("Eventstream #342, error with '" + e.message[:len(e.message)] + "'.")
                    self.log_data("Eventstream #342 error msg", str(e))
                    self.log_data("Eventstream #342 erroneous str", msg)

    def eventstream(self, running, key):
        """
        Method exclusively called by *register_eventstream* only

        :type key: str
        :param key:
        :type running: threading.Event
        :param running:
        """
        with supp_fct.TraceLog(self.logger):

            # get  connection loop
            while self.eventstream_keep_running.is_set():
                host_ip = self.FRAMEWORK.get_homeserver_private_ip()

                sock_unsecured = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock = ssl.wrap_socket(sock_unsecured, cert_reqs=ssl.CERT_NONE)

                # connect to bridge
                if self.bridge.connect_to_eventstream(sock, host_ip, key):
                    set_eventstream_is_connected(True)
                else:
                    time.sleep(5)
                    continue

                # receive data loop
                while get_eventstream_is_connected():
                    try:
                        msgs = self.handle_connection(sock)  # check if data is available to read
                        self.process_eventstream_msgs(msgs)  # process received msg
                    except socket.error as e:
                        self.logger.error("Eventstream disconnected due to socket error {} '{}'.".format(e.errno, e))
                        set_eventstream_is_connected(False)

                # gently disconnect and wait for re-connection
                sock.close()
                self.logger.warning("Trying to reconnect to eventstream soon.")
                time.sleep(4)

            set_eventstream_is_connected(False)

    def stop_eventstream(self):
        """
        Stops the eventstream thread

        :return:
        """
        tracelog = supp_fct.TraceLog(self.logger)
        try:
            while self.eventstream_thread.is_alive():
                self.logger.debug("Eventstream still living...")
                self.eventstream_keep_running.clear()
                time.sleep(3)
        except AttributeError as e:
            self.logger.error("Error in stop_eventstream #342 (no worries), " + e.message)
        finally:
            pass

    def do_init(self):
        """

        :return: False if errors occur
        :rtype: bool
        """
        with supp_fct.TraceLog(self.logger):
            key = self._get_input_value(self.PIN_I_HUE_KEY)
            device_id = self._get_input_value(self.PIN_I_ITM_IDX)
            self.singleton = singlet.Singleton(self._get_module_id())

            # Connections
            ip = self.bridge.get_bridge_ip(self.FRAMEWORK.get_homeserver_private_ip())

            if not ip:
                return False

            if self.singleton.is_master():
                amount = self.bridge.register_devices(key, device_id, self.FRAMEWORK.get_homeserver_private_ip())
                self.logger.info("Found {} Hue devices.".format(amount))

                # server
                server_port = self._get_input_value(self.PIN_I_PORT)
                self.server.run_server(self.FRAMEWORK.get_homeserver_private_ip(), server_port)
                self.server.set_html_content(self.bridge.get_html_device_list())
                link = self.FRAMEWORK.get_homeserver_private_ip() + ":" + str(server_port)
                self.logger.info("Info-Server at http://{}".format(link))

            # get own lamp data if already registered
            device = self.bridge.get_own_device(device_id)
            data = supp_fct.get_data(ip, key, "light/" + device.light_id, self.logger)

            if int(data["status"]) is 200:
                self.process_json(data)
            else:
                self.logger.warning("Could not retrieve data for master light id in on_init")

            data = supp_fct.get_data(ip, key, "zigbee_connectivity/" + device.zigbee_connectivity_id, self.logger)
            if int(data["status"]) is 200:
                self.process_json(data)
            else:
                self.logger.warning("Could not retrieve zigbee connectivity data for master light")

            if self.singleton.is_master():
                # eventstream init & start
                self.eventstream_thread = threading.Thread()  # type: threading.Thread
                self.eventstream_keep_running = threading.Event()
                self.event_list = []
                self.eventstream_start(key)

            self.log_data("Hue {} ID".format(device.rtype), device.id)
            return True

    def on_init(self):
        # debug
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        handler = self.FunctionHandler(self.DEBUG, self._get_module_id())
        self.logger.addHandler(handler)
        # self.logger.setLevel(TRACE)  # @todo Set loglevel Info for production
        self.logger.name = "Module {}".format(self._get_module_id())
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug("Ready to log with log level {}".format(self.logger.level))

        self.do_init()

    def on_input_value(self, index, value):
        # Process State
        # itm_idx = str(self._get_input_value(self.PIN_I_ITM_IDX))
        tracelog = supp_fct.TraceLog(self.logger)
        ip = self.bridge.get_bridge_ip(self.FRAMEWORK.get_homeserver_private_ip())
        if ip == str():
            if not self.do_init():
                self.logger.error("Received new input but could not establish connection to bridge.")
                return

        device = self.bridge.get_own_device(self._get_input_value(self.PIN_I_ITM_IDX))
        key = self._get_input_value(self.PIN_I_HUE_KEY)

        if self._get_input_value(self.PIN_I_HUE_KEY) == "":
            self.logger.error("Hue key not set. Abort processing updated input.")
            return

        if not get_eventstream_is_connected():
            self.eventstream_start(key)

        # If trigger == 1, get data via web request
        if (self.PIN_I_TRIGGER == index) and (bool(value)):
            self.logger.debug("Received Trigger input.")
            item_types = {"device", "light", "room", "scene", "zone", "grouped_light"}

            for item_type in item_types:
                data = supp_fct.get_data(ip, key, item_type, self.logger)
                self.process_json(data)

        # Process set commands
        if self.PIN_I_ON_OFF == index:
            self.logger.debug("Received on/off command.")
            device.set_on(ip, key, bool(value))

        elif self.PIN_I_SCENE == index:
            self.logger.debug("Received scene input.")
            scene = hue_item.HueDevice(self.logger)
            scene.id = value
            scene.rtype = "scene"
            scene.set_scene(ip, key, value)

        elif index == self.PIN_I_DYN_SCENE and bool(value):
            dynamic_scene = self._get_input_value(self.PIN_I_SCENE)  # type: str
            speed = self._get_input_value(self.PIN_I_DYN_SC_SPEED)
            if not dynamic_scene:
                return

            if speed <= 0 or speed > 1:
                self.logger.error("Call of dynamic scene erroneous, speed shall be 0-1")
                return

            device.set_dynamic_scene(ip, key, dynamic_scene, speed)

        elif self.PIN_I_BRI == index:
            self.logger.debug("Received Bri input.")
            device.set_on(ip, key, True)
            device.set_bri(ip, key, int(value))

        elif self.PIN_I_ITM_IDX == index:
            self.logger.debug("Received Item Index input.")
            self.bridge.register_devices(key, value, self.FRAMEWORK.get_homeserver_private_ip())
            device = self.bridge.get_own_device(value)

            # get own lamp data if registered
            data = supp_fct.get_data(ip, key, "light/" + device.light_id, self.logger)

            if data["status"] == 200:
                self.process_json(data)
            else:
                self.logger.warning("Could not retrieve data for master light id in on_init")

        elif ((self.PIN_I_R == index) or
              (self.PIN_I_G == index) or
              (self.PIN_I_B == index)):
            self.logger.debug("Received r/g/b input.")

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


TRACE = 5
MSG_SEP = "\n"
EVENTSTREAM_TIMEOUT = 300  # time to block the process waiting for data on the eventstream
EVENTSTREAM_RECONNECT_ELAPSE = 60 * 60 * 25  # duration for a gentle disconnect for eventstream re-connection in sec


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