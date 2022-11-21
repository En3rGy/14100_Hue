# coding: UTF-8

import hue_lib.hue_item as hue_item
import hue_lib.hue_bridge as hue_bridge
import hue_lib.supp_fct as supp_fct
import hue_lib.html_server as html_server
import hue_lib.singleton as singlet

import ssl
import urlparse
import socket
import time
import json
import threading


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class HueGroup_14100_14100(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "14100_Hue")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_TRIGGER=1
        self.PIN_I_HUE_KEY=2
        self.PIN_I_PORT=3
        self.PIN_I_ITM_IDX=4
        self.PIN_I_SCENE=5
        self.PIN_I_ON_OFF=6
        self.PIN_I_BRI=7
        self.PIN_I_R=8
        self.PIN_I_G=9
        self.PIN_I_B=10
        self.PIN_I_REL_DIM=11
        self.PIN_I_DIM_RAMP=12
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

        msg_sep = "\n\n\r\n"

        sock = socket.socket()

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

            data = str()  # type: str
            self.log_msg("Connected to eventstream")

            # receive data loop
            while self.eventstream_keep_running.is_set():
                try:
                    while self.eventstream_keep_running.is_set():
                        data = data + sock.recv()
                        if msg_sep in data:
                            break

                except socket.error as e:
                    self.log_msg(
                        "In eventstream #291, socket error " + str(e.errno) + " '" + str(e.message) + "'")
                    set_eventstream_is_connected(False)
                    break

                msgs = data.split(msg_sep)

                supp_fct.log_debug("In eventstream #297, " + str(len(msgs)) + " messages received.")
                for i in range(len(msgs)):
                    if "data" not in msgs[i]:
                        continue

                    msg = msgs[i][msgs[i].find("data: ") + 6:]
                    try:
                        msg = json.loads(msg)
                        # supp_fct.log_debug("In eventstream #306, processing msg '" + json.dumps(msg) + "'.")

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
                        e_msg = "'Unterminated string starting"
                        if e.message[:len(e_msg)] == e_msg:
                            self.log_msg("Eventstream #342, '" + e.message[:len(e_msg)] + "'.")
                        else:
                            self.log_msg("Eventstream #342, '" + str(e) + "'.")
                        self.log_data("Eventstream #342 error msg", str(e))
                        self.log_data("Eventstream #342 erroneous str", msg)

                        continue
                    else:
                        msgs[i] = str()  # remove successful processed msg

                last_msg = msgs[-1]
                if msg_sep in last_msg:
                    index = last_msg.rfind(msg_sep)
                    data = last_msg[index:]  # keep not yet finished messages

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
