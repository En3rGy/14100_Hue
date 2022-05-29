# coding: utf8


import unittest
import ssl
import urllib2
import urlparse
import socket
import time
import json
# import colorsys
# import thread
import threading
import BaseHTTPServer
import SocketServer


class hsl20_4:
    LOGGING_NONE = 0

    def __init__(self):
        pass

    class BaseModule:
        debug_output_value = {}  # type: {int, any}
        debug_set_remanent = {}  # type: {int, any}
        debug_input_value = {}  # type: {int: any}

        def __init__(self, a, b):
            pass

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
            print (str(time.time()) + "# Out: pin " + str(pin) + " <- \t" + str(value))

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

    class Framework:
        def __init__(self):
            pass

        def _run_in_context_thread(self, a):
            pass

        def create_debug_section(self):
            d = hsl20_4.DebugHelper()
            return d

        def get_homeserver_private_ip(self):
            # type: () -> str
            return "127.0.0.1"

        def get_instance_by_id(self, id):
            # type: (int) -> str
            return ""

    class DebugHelper:
        def __init__(self):
            pass

        def set_value(self, cap, text):
            print(str(time.time()) + " DEBUG value\t'" + str(cap) + "': " + str(text))

        def add_message(self, msg):
            print(str(time.time()) + " Debug Msg\t" + str(msg))

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

    sbc_data_lock = threading.Lock()
    eventstream_is_connected_lock = threading.Lock()
    eventstream_is_connected = False  # type: bool
    bridge_ip = str()  # type: str

    def log_msg(self, text):
        # type: (str) -> None
        self.DEBUG.add_message("14100: " + str(text))

    def log_data(self, key, value):
        # type: (str, any) -> None
        self.DEBUG.set_value("14100: " + str(key), str(value))

    def log_debug(self, msg):
        pass
        # print(str(time.time()) + " --- " + str(msg) + " ---")

    def set_output_value_sbc(self, pin, val):
        # type:  (int, any) -> None
        self.sbc_data_lock.acquire()
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                print (str(time.time()) + " # SBC: pin " + str(pin) + " <- data not send / " + str(val).decode("utf-8"))
                self.sbc_data_lock.release()
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val
        self.sbc_data_lock.release()

    def hex2int(self, msg):
        msg = bytearray(msg)
        val = 0
        val = val | msg[0]
        for byte in msg[1:]:
            val = val << 8
            val = val | byte

        return int(val)

    class HueDevice:
        def __init__(self):
            self.id = str()  # type: str
            self.type = str()  # type: str
            self.name = str()  # type: str
            self.linked_device = str()  # type: str
            self.light_id = str()  # type: str
            self.service_id_dict = {}  # type {str: str}

        def __str__(self):
            return ("<tr>" +
                    "<td>" + self.id.encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + self.type.encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + self.name.encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + self.light_id.encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + self.get_light_type().encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + self.linked_device.encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + str(self.service_id_dict).encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "</tr>\n")

        def get_device_ids(self):
            ret = [self.id, self.light_id, self.linked_device]  # type: [str]
            for service_id in self.service_id_dict.keys():
                ret.append(self.service_id_dict[service_id])

            return ret

        def get_light_type(self):
            if self.type == "room" or self.type == "zone":
                return "grouped_light"
            elif "light" in self.service_id_dict.keys():
                return "light"
            else:
                return self.type

    def discover_hue(self):
        # type: () -> str

        mcast_port = 5353
        mcast_grp = '224.0.0.251'

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        sock.settimeout(1)

        # best definition https://courses.cs.duke.edu/fall16/compsci356/DNS/DNS-primer.pdf
        msg_id = '\x00\x01'
        query = "\x01\x00"
        questions = "\x00\x01"
        answers = "\x00\x00"
        authority = '\x00\x00'
        additional = '\x00\x00'
        # search = '\x14Philips Hue - 7DE70D\x04_hue\x04_tcp\x05local\x00'
        search = '\x04_hue\x04_tcp\x05local\x00'
        # query_type = '\x00\x01'  # A = a host address, https://www.rfc-editor.org/rfc/rfc1035
        query_type = '\x00\xff'  # * = All data available
        query_class = '\x00\x01'  # IN = the Internet, https://www.rfc-editor.org/rfc/rfc1035
        query_header = msg_id + query + questions + answers + authority + additional
        search = search + query_type + query_class
        query_msg = query_header + search

        try:
            sock.sendto(query_msg, (mcast_grp, mcast_port))
        except socket.error as e:
            self.log_data("Error", "discover: " + str(e))
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

        while True:
            try:
                data = sock.recv(1024)
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()

                # check reply for "additional records", Type A, class IN contains IP4 address
                # header = data[:12]
                # qd_count = self.hex2int(data[4:6])
                # an_count = self.hex2int(data[6:8])
                # ns_count = self.hex2int(data[8:10])
                ar_count = self.hex2int(data[10:12])

                ans_idx = 12 + len(search)
                # ans_name = data[ans_idx:ans_idx + 2]
                # ans_type = data[ans_idx + 2:ans_idx + 4]
                # ans_class = data[ans_idx + 4:ans_idx + 6]
                # ans_ttl = data[ans_idx + 6:ans_idx + 10]
                ans_rd_length = data[ans_idx + 10:ans_idx + 12]
                ans_rd_length = self.hex2int(ans_rd_length)
                # ans_r_dara = data[ans_idx + 12:ans_idx + 12 + ans_rd_length]

                # answers = data[ans_idx:ans_idx + 12 + ans_rd_length]

                add_rec_idx = ans_idx + 12 + ans_rd_length
                add_records = data[add_rec_idx:]

                # process additional records
                ar_offset = 0
                for i in range(ar_count):
                    # get record type (= A) and extrakt ip
                    ar_type = add_records[ar_offset + 2:ar_offset + 4]
                    # print(":".join("{:02x}".format(ord(c)) for c in ar_type))
                    ar_length = add_records[ar_offset + 10: ar_offset + 12]
                    ar_length = self.hex2int(ar_length)

                    if ar_type == "\x00\x01":  # Type A, get IP & Port
                        ar_ip = add_records[ar_offset + 12:ar_offset + 12 + ar_length]
                        ip1 = self.hex2int(ar_ip[0])
                        ip2 = self.hex2int(ar_ip[1])
                        ip3 = self.hex2int(ar_ip[2])
                        ip4 = self.hex2int(ar_ip[3])

                        ip = str(ip1) + "." + str(ip2) + "." + str(ip3) + "." + str(ip4)
                        self.log_msg("Bridge IP (auto) is " + ip)
                        self.bridge_ip = ip
                        return ip

                    ar_offset = ar_offset + 12 + ar_length

            except socket.timeout:
                self.log_msg("Discovery timeout")
                break

        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        return str()

    def get_data(self, api_cmd):
        """
        {'data': str(result), 'status': str(return code)}
        :rtype: {string, string}
        """
        self.log_debug("entering get_data")
        api_path = 'https://' + self.bridge_ip + '/clip/v2/resource/' + api_cmd
        url_parsed = urlparse.urlparse(api_path)
        headers = {'Host': url_parsed.hostname, "hue-application-key": self._get_input_value(self.PIN_I_HUE_KEY)}

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()

        try:
            if not self.debug:
                # Build a http request and overwrite host header with the original hostname.
                request = urllib2.Request(api_path, headers=headers)
                # Open the URL and read the response.
                response = urllib2.urlopen(request, data=None, timeout=5, context=ctx)
                data = {'data': response.read(), 'status': str(response.getcode())}
            else:
                data = {'data': "debug", 'status': str(200)}

            self.log_msg("In get_data, Hue bridge response code for '" + api_cmd + "' is " + data["status"])

        except Exception as e:
            self.log_msg("In get_data, " + str(e))
            data = {'data': str(e), 'status': str(0)}
            print(data)

        return data

    def http_put(self, device_rid, api_path, payload):
        # type: (str, str, str) -> {str, int}

        self.log_debug("entering http_put with device_rid=" + device_rid +
                       "; api_path=" + api_path +
                       "; payload=" + str(payload))

        api_path = "https://" + self.bridge_ip + '/clip/v2/resource/' + api_path + "/" + device_rid
        url_parsed = urlparse.urlparse(api_path)
        headers = {"Host": url_parsed.hostname,
                   "Content-type": 'application/json',
                   "hue-application-key": str(self._get_input_value(self.PIN_I_HUE_KEY))}

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()

        try:
            # Build a http request and overwrite host header with the original hostname.
            request = urllib2.Request(api_path, headers=headers)
            request.get_method = lambda: 'PUT'
            # Open the URL and read the response.
            response = urllib2.urlopen(request, data=payload, timeout=5, context=ctx)
            data = {'data': response.read(), 'status': response.getcode()}
        except Exception as e:
            self.log_msg("In http_put, " + str(e) + " with " +
                         "device_rid=" + device_rid +
                         "; api_path=" + api_path +
                         "; payload=" + str(payload))
            data = {'data': str(e), 'status': 0}

        self.log_msg("In http_put, hue bridge response code: " + str(data["status"]))
        if data["status"] != 200:
            try:
                json_data = json.loads(data["data"])
                if "errors" in json_data:
                    for msg_error in json_data["errors"]:
                        self.log_msg("In http_put, " + self.get_val(msg_error, "description"))
            except Exception as e:
                self.log_msg("In http_put, got an error from hue bridge but don't know which.")

        if data["status"] == 207:
            data["status"] = 200

        return data

    # todo dynamic scene
    # PUT 'https://<ipaddress>/clip/v2/resource/scene/<v2-id>'
    # -H 'hue-application-key: <appkey>' -H 'Content-Type: application/json'
    # --data-raw '{"recall": {"action": "dynamic_palette"}}'

    def get_val(self, json_data, key, do_xmlcharrefreplace=True):
        # type : (json, str, bool) -> Any

        val = str()

        if type(json_data) != dict:
            return val

        if key in json_data:
            val = json_data[key]
        if (type(val) == unicode) and do_xmlcharrefreplace:
            val = val.encode("ascii", "xmlcharrefreplace")
        return val

    def register_devices(self):
        # type: () -> bool
        self.log_debug("entering register_devices")
        item_types = {"light", "device", "room", "scene", "zone", "grouped_light"}  # "light" is intentionally missing

        info_data = "<html>"
        info_data = (info_data + '<table border="1">' +
                     "<tr>" +
                     "<th>id</th>" +
                     "<th>type</th>" +
                     "<th>name</th>" +
                     "<th>light_id</th>" +
                     "<th>light_type</th>" +
                     "<th>linked_device</th>" +
                     "<th>service_id_dict</th>" +
                     "</tr>\n")

        # start to store info of devices
        self.devices = {}

        for item_type in item_types:
            # get data from bridge
            data = self.get_val(self.get_data(item_type), "data")

            # convert received data to json
            try:
                data = json.loads(data)
            except Exception as e:
                self.log_msg("In register_devices, " + str(e))
                continue

            # get data filed in json
            data = self.get_val(data, "data")  # type: {}
            if not data:
                self.log_msg("In register_devices, no data field in '" + item_type + "' reply")
                continue

            for data_set in data:
                device = self.HueDevice()
                device.id = self.get_val(data_set, "id")
                device.light_id = device.id
                device.type = item_type

                if item_type == "light" or item_type == "scene" or item_type == "room" or item_type == "zone":
                    device.name = data_set["metadata"]["name"]
                else:
                    device.name = str()

                if item_type == "scene":
                    device.linked_device = data_set["group"]["rid"]

                if item_type == "grouped_light" or item_type == "scene":
                    device.light_id = self.get_val(data_set, "id")
                else:
                    device_services = self.get_val(data_set, "services")
                    for service in device_services:
                        rtype = str(self.get_val(service, "rtype"))
                        rid = str(self.get_val(service, "rid"))
                        if rtype == "light" or rtype == "grouped_light":
                            device.light_id = rid
                        device.service_id_dict[rtype] = rid

                self.devices[device.id] = device
                info_data = info_data + str(device).encode("ascii", "xmlcharrefreplace")

                # self.process_json(data)

        self.log_msg("In register_devices, registered " + str(len(self.devices)) + " devices")
        info_data = info_data + "</table>"
        info_data = info_data + "</html>"
        # print(info_data)  # todo remove
        self.set_html_content(info_data)
        return True

    def set_html_content(self, content):
        with self.http_request_handler.data_lock:
            self.http_request_handler.response_content_type = "text"
            self.http_request_handler.response_data = content

    def get_eventstream_is_connected(self):
        # type: () -> bool
        self.eventstream_is_connected_lock.acquire()
        ret = self.eventstream_is_connected  # tpye: bool
        self.eventstream_is_connected_lock.release()
        return ret

    def set_eventstream_is_connected(self, is_connected):
        # type: (bool) -> bool
        self.eventstream_is_connected_lock.acquire()
        self.eventstream_is_connected = is_connected
        self.eventstream_is_connected_lock.release()
        return is_connected

    def register_eventstream(self):
        self.log_debug("entering register_eventstream")
        if not self.get_eventstream_is_connected():
            self.eventstream_thread = threading.Thread(target=self.eventstream, args=(self.eventstream_running,))
            self.eventstream_thread.start()

    def eventstream(self, running):
        # type: (threading.Event) -> None
        self.log_debug("Entering eventstream")
        self.set_eventstream_is_connected(True)

        msg_sep = "\n\n\r\n"

        sock = socket.socket()

        while running.is_set():
            self.log_msg("In eventstream, connecting...")

            while not self.bridge_ip:
                self.log_msg("Waiting for Hue discovery to connect to eventstream.")
                time.sleep(5)

            api_path = 'https://' + str(self.bridge_ip) + '/eventstream/clip/v2'
            url_parsed = urlparse.urlparse(api_path)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_NONE)
            # sock.settimeout(3)

            try:
                sock.bind(('', 0))
                sock.connect((self.bridge_ip, 443))
                sock.send("GET /eventstream/clip/v2 HTTP/1.1\r\n")
                sock.send("Host: " + url_parsed.hostname + "\r\n")
                sock.send("hue-application-key: " + str(self._get_input_value(self.PIN_I_HUE_KEY)) + "\r\n")
                sock.send("Accept: text/event-stream\r\n\r\n")

            except Exception as e:
                self.log_msg("In eventstream, disconnecting due to " + str(e))
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
                    self.log_msg("In eventstream, socket error " + str(e.errno) + " '" + str(e.message) + "'")

                msgs = data.split(msg_sep)

                self.log_debug("In eventstream, " + str(len(msgs)) + " messages received.")
                for i in range(len(msgs)):
                    if "data: " not in msgs[i]:
                        continue

                    msg = msgs[i][msgs[i].find("data: ") + 6:]
                    try:
                        msg = json.loads(msg)
                        self.process_json(msg)
                    except Exception as e:
                        self.log_msg("In eventstream, '" + str(e) + "'.")
                        continue
                    else:
                        msgs[i] = str()  # remove successful processed msg

                last_msg = msgs[-1]
                if msg_sep in last_msg:
                    index = last_msg.rfind(msg_sep)
                    data = last_msg[index:]  # keep not yet finished messages

        # gently disconnect and wait for re-connection
        sock.close()
        self.log_msg("Disconnected from hue eventstream.")
        time.sleep(4)

        self.log_msg("Exit eventstream. No further processing.")
        self.set_eventstream_is_connected(False)

    def process_json(self, msg):
        # type: (json) -> bool
        self.log_debug("Entering process_json")
        try:
            out = json.dumps(msg)
        except Exception as e:
            self.log_msg("In process_json, " + str(e))
            return False

        if type(msg) == dict:
            msg = [msg]

        own_id = self._get_input_value(self.PIN_I_ITM_IDX)
        device = self.get_val(self.devices, own_id)  # type: HueGroup_14100_14100.HueDevice
        if not device:
            self.log_debug("In process_json device not yet registered in global dictionary")
            return False

        device_ids = device.get_device_ids()

        try:
            for msg_entry in msg:
                if "data" not in msg_entry:
                    continue

                for data in msg_entry["data"]:
                    if "owner" in data:
                        device_id = data["owner"]["rid"]
                    else:
                        device_id = data["id"]

                    if device_id in device_ids:
                        self.log_debug("In process_json, found data for own ID.")

                        if "on" in data:
                            is_on = bool(data["on"]["on"])
                            self.set_output_value_sbc(self.PIN_O_STATUS_ON_OFF, is_on)

                        bri = 0
                        if "dimming" in data:
                            dimming = data["dimming"]
                            bri = dimming["brightness"]
                            self.set_output_value_sbc(self.PIN_O_BRI, int(bri))

                        color = self.get_val(data, color)
                        xy = self.get_val(color, "xy")
                        x = self.get_val(xy, "x")
                        y = self.get_val(xy, "y")
                        [r, g, b] = self.xy_bri_to_rgb(x, y, bri)
                        self.set_output_value_sbc(self.PIN_O_R, r)
                        self.set_output_value_sbc(self.PIN_O_G, g)
                        self.set_output_value_sbc(self.PIN_O_B, b)

        except Exception as e:
            self.log_msg("In process_json, '" + str(e) + "', with message '" + str(out) + "'")

    def get_rid(self):
        # type: () -> HueGroup_14100_14100.HueDevice
        # self.log_debug("entering get_rid")
        rid = str(self._get_input_value(self.PIN_I_ITM_IDX))
        if not rid:
            self.log_msg("In set_on, rid for type 'light' not found.")
            return None

        if rid not in self.devices.keys():
            self.log_msg("In get_rid, rid not registered.")
            return None

        return self.devices[rid]

    def set_on(self, set_on):
        # type: (bool) -> bool
        """
        on / off
        :param set_on: True / False
        :return:
        """
        self.log_debug("entering set_on")
        device = self.get_rid()
        if not device:
            self.log_msg("In set_on, device invalid")
            return False

        if set_on:
            payload = '{"on":{"on":true}}'
        else:
            payload = '{"on":{"on":false}}'

        ret = self.http_put(device.light_id, device.get_light_type(), payload)
        self.log_msg("In set_on, return code is " + str(ret["status"]))
        return ret["status"] == 200

    def set_bri(self, brightness):
        # type: (float) -> bool
        """
        Brightness percentage. value cannot be 0, writing 0 changes it to the lowest possible brightness

        :return:
        :param brightness: number – maximum: 100
        :return: True if successful, otherwise False
        """
        self.log_debug("entering set_bri")
        device = self.get_rid()
        if not device:
            return False

        payload = '{"dimming":{"brightness":' + str(brightness) + '}}'
        ret = self.http_put(device.light_id, device.get_light_type(), payload)
        return ret["status"] == 200

    def set_color_rgb(self, r, g, b):
        # type: (int, int, int) -> bool
        """

        :param r: 0-255
        :param g: 0-255
        :param b: 0-255
        :return:
        """

        r = r / 100.0 * 255  # type: float
        g = g / 100.0 * 255  # type: float
        b = b / 100.0 * 255  # type: float

        self.log_debug("entering set_color")
        [x, y, bri] = self.rgb_to_xy_bri(r, g, b)
        return self.set_color_xy_bri(x, y, bri)

    def rgb_to_xy_bri(self, red, green, blue):
        # type: (int, int, int) -> [float]
        """
        Convert rgb to xy
        :param red: 0-255
        :param green: 0-255
        :param blue: 0-255
        :return: [x (0.0-1.0), y (0.0-1.0), brightness (0-100%)]
        """

        # https://github.com/PhilipsHue/PhilipsHueSDK-iOS-OSX/blob/00187a3db88dedd640f5ddfa8a474458dff4e1db/ApplicationDesignNotes/RGB%20to%20xy%20Color%20conversion.md
        # Get the RGB values from your color object and convert them to be between 0 and 1. So the RGB
        # color(255, 0, 100)  becomes(1.0, 0.0, 0.39)

        red = red / 255.0
        green = green / 255.0
        blue = blue / 255.0

        # Apply a gamma correction to the RGB values, which makes the color more vivid and more the like the color
        # displayed on the screen of your device. This gamma correction is also applied to the screen of your
        # computer or phone, thus we need this to create the same color on the light as on screen.This is done
        # by  the following formulas:
        # float  red = (red > 0.04045f) ? pow((red + 0.055f) / (1.0f + 0.055f), 2.4f): (red / 12.92f)
        # float green = (green > 0.04045f) ? pow((green + 0.055f) / (1.0f + 0.055f), 2.4f): (green / 12.92f)
        # float blue = (blue > 0.04045f) ? pow((blue + 0.055f) / (1.0f + 0.055f), 2.4f): (blue / 12.92f)
        #
        # Convert the RGB values to XYZ using the Wide RGB D65 conversion formula
        # The formulas used:

        X = red * 0.649926 + green * 0.103455 + blue * 0.197109
        Y = red * 0.234327 + green * 0.743075 + blue * 0.022598
        Z = red * 0.0000000 + green * 0.053077 + blue * 1.035763

        # Calculate the xy values from the XYZ values

        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)

        # Check if the found xy value is within the color gamut of the light, if not continue with step 6, otherwise
        # step 7 When we sent a value which the light is not capable of, the resulting color might not be optimal.
        # Therefor we try to only sent values which are inside the color gamut of the selected light.
        #
        # Calculate the closest point on the color gamut triangle and use that as xy value The closest
        # value is calculated by making a perpendicular line to one of the lines the triangle consists of and when
        # it is then still not inside the triangle, we choose the closest corner point of the triangle.
        #
        # Use the Y value of XYZ as brightness The Y value indicates the brightness of the converted color.

        return [x, y, Y]

    def set_color_xy_bri(self, x, y, bri):
        # type: (float, float, float) -> bool
        """
        CIE XY gamut position
        :param x: number – minimum: 0 – maximum: 1
        :param y: number – minimum: 0 – maximum: 1
        :param bri: 0-100%
        :return:
        """

        payload = '{"color":{"xy":{"x":' + str(x) + ', "y":' + str(y) + '}}'
        device = self.get_rid()
        if not device:
            return False
        ret = self.http_put(device.light_id, device.get_light_type(), payload)
        return (ret["status"] == 200) & self.set_bri(bri)

    def xy_bri_to_rgb(self, x, y, bri):
        """
        Convert CIE XY gamut position to rgb
        :param x: number – minimum: 0 – maximum: 1
        :param y: number – minimum: 0 – maximum: 1
        :param bri: 0-100%
        :return: [r, g, b] each 0-100%
        """
        z = 1.0 - x - y
        Y = bri / 255.0  # Brightness of lamp
        X = (Y / y) * x
        Z = (Y / y) * z
        r = X * 1.612 - Y * 0.203 - Z * 0.302
        g = -X * 0.509 + Y * 1.412 + Z * 0.066
        b = X * 0.026 - Y * 0.072 + Z * 0.962

        if r <= 0.0031308:
            r = 12.92 * r
        else:
            r = (1.0 + 0.055) * pow(r, (1.0 / 2.4)) - 0.055

        if g <= 0.0031308:
            g = 12.92 * g
        else:
            g = (1.0 + 0.055) * pow(g, (1.0 / 2.4)) - 0.055

        if b <= 0.0031308:
            b = 12.92 * b
        else:
            b = (1.0 + 0.055) * pow(b, (1.0 / 2.4)) - 0.055

        max_value = max(r, g, b)
        r /= max_value
        g /= max_value
        b /= max_value
        r = r * 255
        if r < 0:
            r = 255
        g = g * 255
        if g < 0:
            g = 255
        b = b * 255
        if b < 0:
            b = 255

        r = r / 255.0 * 100
        g = g / 255.0 * 100
        b = b / 255.0 * 100

        return [int(round(r)), int(round(g)), int(round(b))]

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
            self.timer = threading.Timer(1000, None)
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

    def stop_server(self):
        """
        Stop server which provides info page
        """
        if self.server:
            try:
                self.log_msg("Shutting down running server")
                self.server.shutdown()
                self.server.server_close()
            except Exception as e:
                self.log_msg(str(e))

    def run_server(self, port):
        # type: (int) -> None
        """
        Start the server providing the info page with Hue IDs.
        :param port: Port used to provide the info page
        :return: None
        """
        self.log_debug("entering run_server")
        self.log_msg("Trying to start server")
        server_address = ('', port)

        self.stop_server()

        try:
            self.server = ThreadedTCPServer(server_address, self.http_request_handler, bind_and_activate=False)
            self.server.allow_reuse_address = True
            self.server.server_bind()
            self.server.server_activate()
        except Exception as e:
            self.log_msg(str(e))
            return

        ip, port = self.server.server_address
        self.t = threading.Thread(target=self.server.serve_forever)
        self.t.setDaemon(True)
        self.t.start()
        self.log_msg("Server running on " + str(ip) + ":" + str(port))

    def on_init(self):
        self.log_debug("entering on_init")
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.g_out_sbc = {}  # type: {int, object}
        self.debug = False  # type: bool

        # server
        self.server = ""
        self.t = ""
        self.http_request_handler = MyHttpRequestHandler
        self.run_server(8080)
        # self.run_server(self._get_input_value(self.PIN_I_SHUEIP))

        self.eventstream_thread = threading.Thread()  # type: threading.Thread
        self.eventstream_running = threading.Event()
        self.eventstream_running.set()

        self.devices = {}  # type: {str, HueGroup_14100_14100.HueDevice}

        self.discover_hue()
        self.register_devices()
        self.register_eventstream()

    def on_input_value(self, index, value):

        # Process State
        itm_idx = str(self._get_input_value(self.PIN_I_ITM_IDX))

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


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


# class MyHttpRequestHandler(SocketServer.BaseRequestHandler):
class MyHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    data_lock = threading.RLock()

    def on_init(self):
        self.response_content_type = ""
        self.response_data = ""

    def do_GET(self):
        with self.data_lock:
            self.send_response(200)
            self.send_header('Content-type', self.response_content_type)
            self.end_headers()

            self.wfile.write(self.response_data)


############################################


class UnitTests(unittest.TestCase):

    def setUp(self):
        print("\n### setUp")
        with open("credentials.json") as f:
            self.cred = json.load(f)

        self.dummy = HueGroup_14100_14100(0)

        self.dummy.debug_input_value[self.dummy.PIN_I_HUE_KEY] = self.cred["PIN_I_SUSER"]
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_device_id"]
        self.dummy.debug_rid = self.cred["hue_light_id"]

        self.dummy.on_init()
        self.dummy.debug = True

    def tearDown(self):
        print("\n### tearDown")

    def test_get_rig(self):
        print("\n### test_get_rig")
        self.assertTrue(False)

    def test_08_print_devices(self):
        print("\n### ###test_08_print_devices")
        res = self.dummy.register_devices()
        self.assertTrue(res)

    def test_09_singleton_eventstream(self):
        print("test_09_singleton_eventstream")
        self.assertTrue(False, "Test not implemented")

    def test_10_eventstream_reconnect(self):
        print("\n### test_10_eventstream_reconnect")
        self.assertTrue(False, "Test not implemented")

    def test_11_discover(self):
        print("\n###test_11_discover")
        self.dummy.bridge_ip = None
        self.dummy.discover_hue()
        self.assertTrue("192" in self.dummy.bridge_ip)

        self.dummy.bridge_ip = None

    def generic_on_off(self):
        self.assertTrue(self.dummy.set_on(False))
        time.sleep(2)

        self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF] = False
        self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, True)
        time.sleep(2)

        self.dummy.stop_eventstream = True
        self.assertTrue(self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF])

    def test_12_set_on(self):
        print("\n### test_12_set_on")
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_light_id"]
        self.generic_on_off()

    # def test_13_on_off_group(self):
    # print("\n### test_13_on_off_group")
    # self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_zone_id"]
    # self.generic_on_off()

    def test_14_on_off_zone(self):
        print("\n### test_14_on_off_zone")
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_zone_id"]
        self.generic_on_off()

    def test_15_on_off_room(self):
        print("\n### test_15_on_off_room")
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_room_id"]
        self.generic_on_off()

    def test_16_eventstream_on_off(self):
        print("\n### test_16_eventstream_on_off")
        self.dummy.eventstream_running.set()
        self.dummy.register_eventstream()
        time.sleep(2)
        self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, False)
        time.sleep(3)
        self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, True)
        time.sleep(3)
        self.dummy.eventstream_running.clear()
        self.assertTrue(self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF])
        time.sleep(5)
        print(str(time.time()) + " +++ End +++")

    def test_17_dimming(self):
        print("\n### test_17_dimming")

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
        self.assertTrue(res <= 1, res)
        print("------ off")
        self.dummy.eventstream_running.set()
        self.dummy.set_on(False)
        time.sleep(2)

    def test_18_get_data(self):
        print("\n### test_get_data")
        self.dummy.eventstream_running.set()
        self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF] = None
        self.dummy.g_out_sbc = {}

        self.dummy.on_input_value(self.dummy.PIN_I_TRIGGER, 1)
        res = self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF]

        self.assertTrue(bool == type(res))

    def test_19_xy_to_rgb(self):
        self.dummy.eventstream_running.set()
        print("\n### test_19_xy_to_rgb")
        [r, g, b] = self.dummy.xy_bri_to_rgb(0.640, 0.330, 1)
        print([r, g, b])
        self.assertEqual([255, 0, 0], [r, g, b])
        [r, g, b] = self.dummy.xy_bri_to_rgb(0.640, 0.330, 0.1043)
        print([r, g, b])
        self.assertEqual([125, 0, 0], [r, g, b])

    def test_19_set_color(self):
        print("\n### test_19_set_color")
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_light_id"]
        self.dummy.debug_input_value[self.dummy.PIN_I_R] = 255
        self.dummy.debug_input_value[self.dummy.PIN_I_G] = 0
        self.dummy.debug_input_value[self.dummy.PIN_I_B] = 0

        self.dummy.eventstream_running.set()
        time.sleep(3)

        self.dummy.on_input_value(self.dummy.PIN_I_R, 255)
        time.sleep(3)
        r = self.dummy.debug_output_value[self.dummy.PIN_O_R]
        g = self.dummy.debug_output_value[self.dummy.PIN_O_G]
        b = self.dummy.debug_output_value[self.dummy.PIN_O_B]
        self.assertTrue((r == 255) and (g == 0) and (b == 0))

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
