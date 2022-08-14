# coding: utf8
# import struct
import unittest
import ssl
import urllib2
import urlparse
import socket
import time
import json
import colorconvert
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

    def set_output_value_sbc(self, pin, val):
        # type:  (int, any) -> None
        self.sbc_data_lock.acquire()
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                print (str(time.time()) + "\t# SBC: pin " + str(pin) + " <- data not send / " + str(val).decode("utf-8"))
                self.sbc_data_lock.release()
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val
        self.sbc_data_lock.release()

    class HueDevice:
        def __init__(self):
            self.id = str()  # type: str
            self.name = str()  # type: str
            self.light_id = str()  # type: str
            self.zigbee_connectivity_id = str()  # type: str
            self.room = str()  # type: str
            self.zone = str()  # type: str
            self.scenes = []  # type: [str]
            self.grouped_lights = []  # type: [str]

        def __str__(self):
            return ("<tr>" +
                    "<td>" + self.name.encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + self.id.encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + self.light_id.encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + self.zigbee_connectivity_id.encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + self.room.encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + self.zone.encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + str(self.scenes).encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "<td>" + str(self.grouped_lights).encode("ascii", "xmlcharrefreplace") + "</td>" +
                    "</tr>\n")

        def get_device_ids(self):
            ret = [self.id, self.light_id, self.zigbee_connectivity_id,
                   self.room, self.zone, self.scenes, self.grouped_lights]  # type: [str]

            return ret

    def discover_hue(self):
        # type: () -> str

        # best definition https://courses.cs.duke.edu/fall16/compsci356/DNS/DNS-primer.pdf
        msg_id = '\x00\x01'
        query = "\x01\x00"
        questions = "\x00\x01"
        answers = "\x00\x00"
        authority = '\x00\x00'
        additional = '\x00\x00'
        search = '\x04_hue\x04_tcp\x05local\x00'
        # query_type = '\x00\x01'  # A = a host address, https://www.rfc-editor.org/rfc/rfc1035
        query_type = '\x00\xff'  # * = All data available
        query_class = '\x00\x01'  # IN = the Internet, https://www.rfc-editor.org/rfc/rfc1035
        query_header = msg_id + query + questions + answers + authority + additional
        search = search + query_type + query_class
        query_msg = query_header + search

        # configure socket
        mcast_port = 5353
        mcast_grp = ('224.0.0.251', mcast_port)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 8)

        # try:
        #     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # except AttributeError:
        #     pass

        # sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

        sock.settimeout(8)

        sock.bind((self.FRAMEWORK.get_homeserver_private_ip(), 0))

        # send data
        try:
            bytes_send = sock.sendto(query_msg, mcast_grp)
            if bytes_send != len(query_msg):
                print("Something wrong here")
        except socket.error as e:
            self.log_data("Socket Error", "discover: " + str(e))
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except Exception as e:
            self.log_data("Error", "discover: " + str(e))
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

        while True:
            try:
                data = sock.recv(1024)
                sock.shutdown(socket.SHUT_RDWR)

                # check reply for "additional records", Type A, class IN contains IP4 address
                # header = data[:12]
                # qd_count = hex2int(data[4:6])
                # an_count = hex2int(data[6:8])
                # ns_count = hex2int(data[8:10])
                ar_count = hex2int(data[10:12])

                ans_idx = 12 + len(search)
                # ans_name = data[ans_idx:ans_idx + 2]
                # ans_type = data[ans_idx + 2:ans_idx + 4]
                # ans_class = data[ans_idx + 4:ans_idx + 6]
                # ans_ttl = data[ans_idx + 6:ans_idx + 10]
                ans_rd_length = data[ans_idx + 10:ans_idx + 12]
                ans_rd_length = hex2int(ans_rd_length)
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
                    ar_length = hex2int(ar_length)

                    if ar_type == "\x00\x01":  # Type A, get IP & Port
                        ar_ip = add_records[ar_offset + 12:ar_offset + 12 + ar_length]
                        ip1 = hex2int(ar_ip[0])
                        ip2 = hex2int(ar_ip[1])
                        ip3 = hex2int(ar_ip[2])
                        ip4 = hex2int(ar_ip[3])

                        ip = str(ip1) + "." + str(ip2) + "." + str(ip3) + "." + str(ip4)
                        self.log_msg("Bridge IP (auto) is " + ip)
                        self.bridge_ip = ip
                        return ip

                    ar_offset = ar_offset + 12 + ar_length

            except socket.timeout:
                self.log_msg("Discovery timeout")
                break

        sock.close()
        return str()

    def get_data(self, api_cmd):
        """
        {'data': str(result), 'status': str(return code)}
        :rtype: {string, string}
        """
        # log_debug("entering get_data")
        api_path = 'https://' + self.bridge_ip + '/clip/v2/resource/' + api_cmd
        url_parsed = urlparse.urlparse(api_path)
        headers = {'Host': url_parsed.hostname, "hue-application-key": self._get_input_value(self.PIN_I_HUE_KEY)}

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()

        try:
            # Build a http request and overwrite host header with the original hostname.
            request = urllib2.Request(api_path, headers=headers)
            # Open the URL and read the response.
            response = urllib2.urlopen(request, data=None, timeout=5, context=ctx)
            data = {'data': response.read(), 'status': str(response.getcode())}

            self.log_msg("In get_data #288, Hue bridge response code for '" + api_cmd + "' is " + data["status"])

        except Exception as e:
            self.log_msg("In get_data #291, " + str(e))
            data = {'data': str(e), 'status': str(0)}
            print(data)

        return data

    def http_put(self, device_rid, api_path, payload):
        # type: (str, str, str) -> {str, int}

        log_debug("entering http_put with device_rid=" + device_rid +
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
        except urllib2.HTTPError as e:
            self.log_msg("In http_put #322, " + str(e) + " with " +
                         "device_rid=" + device_rid +
                         "; api_path=" + api_path +
                         "; payload=" + str(payload))
            data = {'data': str(e), 'status': 0}
        except urllib2.URLError as e:
            self.log_msg("In http_put #328, " + str(e) + " with " +
                         "device_rid=" + device_rid +
                         "; api_path=" + api_path +
                         "; payload=" + str(payload))
            data = {'data': str(e), 'status': 0}
        except Exception as e:
            self.log_msg("In http_put #334, " + str(e) + " with " +
                         "device_rid=" + device_rid +
                         "; api_path=" + api_path +
                         "; payload=" + str(payload))
            data = {'data': str(e), 'status': 0}

        self.log_msg("In http_put #341, hue bridge response code: " + str(data["status"]))
        if data["status"] != 200:
            try:
                json_data = json.loads(data["data"])
                if "errors" in json_data:
                    for msg_error in json_data["errors"]:
                        self.log_msg("In http_put, " + get_val(msg_error, "description"))
            except Exception as e:
                self.log_msg("In http_put:357, " + str(e))

        if data["status"] == 207:
            data["status"] = 200

        return data

    # todo dynamic scene
    # PUT 'https://<ipaddress>/clip/v2/resource/scene/<v2-id>'
    # -H 'hue-application-key: <appkey>' -H 'Content-Type: application/json'
    # --data-raw '{"recall": {"action": "dynamic_palette"}}'

    def register_devices(self):
        # type: () -> bool
        # log_debug("entering register_devices")
        # item_types = {"device", "light", "scene", "room", "grouped_light", "zone"}
        item_types = ["device", "room", "zone", "scene", "grouped_light"]

        info_data = "<html>\n"
        info_data = (info_data + '<table border="1">\n' +
                     "<tr>" +
                     "<th>Name</th>" +
                     "<th>Device</th>" +
                     "<th>Light</th>" +
                     "<th>Zigbee Connectivity</th>" +
                     "<th>Room</th>" +
                     "<th>Zone</th>" +
                     "<th>Scenes</th>" +
                     "<th>Grouped Lights</th>" +
                     "</tr>\n")

        # start to store info of devices
        self.devices = {}
        self.associated_rids = []
        self.rid = str(self._get_input_value(self.PIN_I_ITM_IDX))  # type: str

        for item_type in item_types:
            # get data from bridge
            data_raw = self.get_data(item_type)  # type: str

            # convert received data to json
            try:
                data = json.loads(data_raw["data"])  # type: {}
            except Exception as e:
                self.log_msg("In register_devices #377, " + str(e))
                continue

            data = get_val(data, "data")

            self.associated_rids.append(self.rid)

            if item_type == "device":
                for item in data:
                    item_id = get_val(item, "id")
                    if self.rid == item_id:
                        self.rtype = item_type

                    services = get_val(item, "services")
                    device = self.HueDevice()
                    device.id = item_id
                    metadata = get_val(item, "metadata")
                    device.name = get_val(metadata, "name")

                    for service in services:
                        rid = get_val(service, "rid")

                        if self.rid == item_id:
                            self.associated_rids.append(rid)

                        rtype = get_val(service, "rtype")
                        if rtype == "light":
                            device.light_id = rid
                            if self.rid == device.light_id:
                                self.rtype = rtype
                        elif rtype == "zigbee_connectivity":
                            device.zigbee_connectivity_id = rid

                    self.devices[device.id] = device

            elif item_type == "room":
                for item in data:
                    item_id = get_val(item, "id")
                    if self.rid == item_id:
                        self.rtype = item_type
                    children = get_val(item, "children")
                    for i in range(len(children)):
                        rid = get_val(children[i], "rid")
                        rtype = get_val(children[i], "rtype")

                        if self.rid == item_id:
                            self.associated_rids.append(rid)

                        if rtype == "device":
                            if rid in self.devices:
                                device = self.devices[rid]
                                device.room = item_id
                                self.devices[device.id] = device
                            else:
                                self.log_msg(
                                    "In register_devices #414, device not registered as device but requested by "
                                    "'room': '" + rid + "'")

            elif item_type == "zone":
                for item in data:
                    item_id = get_val(item, "id")
                    if self.rid == item_id:
                        self.rtype = item_type
                    children = get_val(item, "children")
                    for i in range(len(children)):
                        rid = get_val(children[i], "rid")
                        rtype = get_val(children[i], "rtype")

                        if self.rid == item_id:
                            self.associated_rids.append(rid)

                        if rtype == "light":
                            for device in self.devices.values():
                                if device.light_id == rid:
                                    device.zone = item_id
                                    self.devices[device.id] = device

            elif item_type == "scene":
                for item in data:
                    item_id = get_val(item, "id")
                    if self.rid == item_id:
                        self.rtype = item_type
                    group = get_val(item, "group")
                    rid = get_val(group, "rid")
                    rtype = get_val(group, "rtype")

                    if self.rid == item_id:
                        self.associated_rids.append(rid)

                    if rtype == "zone":
                        for device in self.devices.values():
                            if device.zone == rid:
                                device.scenes.append(item_id)
                                self.devices[device.id] = device

                    elif rtype == "room":
                        for device in self.devices.values():
                            if device.room == rid:
                                device.scenes.append(item_id)
                                self.devices[device.id] = device

            elif item_type == "grouped_light":
                for item in data:
                    item_id = get_val(item, "id")
                    if self.rid == item_id:
                        self.rtype = item_type
                    owner = get_val(item, "owner")
                    rid = get_val(owner, "rid")
                    rtype = get_val(owner, "rtype")

                    if self.rid == item_id:
                        self.associated_rids.append(rid)

                    for device in self.devices.values():
                        if rtype == "room":
                            if device.room == rid:
                                device.grouped_lights.append(item_id)
                                self.devices[device.id] = device
                        elif rtype == "zone":
                            if device.zone == rid:
                                device.grouped_lights.append(item_id)
                                self.devices[device.id] = device

        self.log_msg("In register_devices #466, registered " + str(len(self.devices)) + " devices")
        for device in self.devices.values():
            info_data = info_data + str(device)

        info_data = info_data + "</table>\n</html>\n"
        self.set_html_content(info_data)

        # pick own device
        for device in self.devices.values():
            if self.rid in device.get_device_ids():
                self.device = device
                break

        return True

    def set_html_content(self, content):
        with self.http_request_handler.data_lock:
            self.http_request_handler.response_content_type = "text"
            self.http_request_handler.response_data = content

    def get_eventstream_is_connected(self):
        # type: () -> bool
        self.eventstream_is_connected_lock.acquire()
        ret = self.eventstream_is_connected  # type: bool
        self.eventstream_is_connected_lock.release()
        return ret

    def set_eventstream_is_connected(self, is_connected):
        # type: (bool) -> bool
        self.eventstream_is_connected_lock.acquire()
        self.eventstream_is_connected = is_connected
        self.eventstream_is_connected_lock.release()
        return is_connected

    def register_eventstream(self):
        log_debug("Entering register_eventstream")
        if not self.get_eventstream_is_connected():
            self.eventstream_thread = threading.Thread(target=self.eventstream, args=(self.eventstream_running,))
            self.eventstream_thread.start()

    def eventstream(self, running):
        # type: (threading.Event) -> None
        log_debug("Entering eventstream")
        self.set_eventstream_is_connected(True)

        msg_sep = "\n\n\r\n"

        sock = socket.socket()

        while running.is_set():
            self.log_msg("In eventstream #581, connecting...")

            while not self.bridge_ip:
                self.log_msg("In eventstream #584, waiting for Hue discovery to connect to eventstream.")
                time.sleep(5)

            api_path = 'https://' + str(self.bridge_ip) + '/eventstream/clip/v2'
            url_parsed = urlparse.urlparse(api_path)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_NONE)

            try:
                sock.bind(('', 0))
                sock.connect((self.bridge_ip, 443))
                sock.send("GET /eventstream/clip/v2 HTTP/1.1\r\n")
                sock.send("Host: " + url_parsed.hostname + "\r\n")
                sock.send("hue-application-key: " + str(self._get_input_value(self.PIN_I_HUE_KEY)) + "\r\n")
                sock.send("Accept: text/event-stream\r\n\r\n")

            except Exception as e:
                self.log_msg("In eventstream #602, disconnecting due to " + str(e))
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
                    self.log_msg("In eventstream #617, socket error " + str(e.errno) + " '" + str(e.message) + "'")

                msgs = data.split(msg_sep)

                log_debug("In eventstream #621, " + str(len(msgs)) + " messages received.")
                for i in range(len(msgs)):
                    if "data" not in msgs[i]:
                        continue

                    msg = msgs[i][msgs[i].find("data: ") + 6:]
                    try:
                        msg = json.loads(msg)
                        log_debug("In eventstream #629, processing msg '" + json.dumps(msg) + "'.")
                        self.process_json(msg)
                    except Exception as e:
                        self.log_msg("In eventstream #632, '" + str(e) + "'.")
                        continue
                    else:
                        msgs[i] = str()  # remove successful processed msg

                last_msg = msgs[-1]
                if msg_sep in last_msg:
                    index = last_msg.rfind(msg_sep)
                    data = last_msg[index:]  # keep not yet finished messages

        # gently disconnect and wait for re-connection
        sock.close()
        self.log_msg("In eventstream #644, Disconnected from hue eventstream.")
        time.sleep(4)

        self.log_msg("In eventstream #647, exit eventstream. No further processing.")
        self.set_eventstream_is_connected(False)

    def process_json(self, msg):
        # type: (json) -> bool
        log_debug("Entering process_json")
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
                    log_debug("In process_json #629, no 'data' field in '" + msg_entry + "'.")
                    continue

                if type(msg_entry["data"]) == str:
                    msg_entry["data"] = json.loads(msg_entry["data"])

                for data in msg_entry["data"]:
                    device_id = get_val(data, "id")

                    if device_id in self.associated_rids:
                        log_debug("In process_json #646, found data for own ID.")

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
                            color = get_val(data, "color")
                            xy = get_val(color, "xy")
                            x = get_val(xy, "x")
                            y = get_val(xy, "y")
                            [r, g, b] = self.xy_bri_to_rgb(x, y, self.curr_bri)
                            self.set_output_value_sbc(self.PIN_O_R, r)
                            self.set_output_value_sbc(self.PIN_O_G, g)
                            self.set_output_value_sbc(self.PIN_O_B, b)

                    else:
                        log_debug("In process_json #662, id " + device_id + " not found in associated ids " +
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

    def set_on(self, set_on):
        # type: (bool) -> bool
        """
        on / off
        :param set_on: True / False
        :return:
        """
        log_debug("entering set_on")
        rid = str(self._get_input_value(self.PIN_I_ITM_IDX))

        if set_on:
            payload = '{"on":{"on":true}}'
        else:
            payload = '{"on":{"on":false}}'

        ret = self.http_put(rid, self.rtype, payload)
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
        log_debug("entering set_bri")
        rid = str(self._get_input_value(self.PIN_I_ITM_IDX))

        payload = '{"dimming":{"brightness":' + str(brightness) + '}}'
        ret = self.http_put(rid, self.rtype, payload)
        self.curr_bri = brightness
        return ret["status"] == 200

    def set_color_rgb(self, r, g, b):
        # type: (int, int, int) -> bool
        """
        :param r: 0-255
        :param g: 0-255
        :param b: 0-255
        :return:
        """

        r = int(r / 255.0)  # type: int
        g = int(g / 255.0)  # type: int
        b = int(b / 255.0)  # type: int

        log_debug("entering set_color")
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

        color_conf = colorconvert.Converter()
        x, y = color_conf.rgb_to_xy(red, green, blue)
        return [x, y, 1]

    def set_color_xy_bri(self, x, y, bri):
        # type: (float, float, float) -> bool
        """
        CIE XY gamut position
        :param x: number – minimum: 0 – maximum: 1
        :param y: number – minimum: 0 – maximum: 1
        :param bri: 0-100%
        :return:
        """
        log_debug("set_color_xy_bri")

        payload = '{"color":{"xy":{"x":' + str(x) + ', "y":' + str(y) + '}}}'
        rid = str(self._get_input_value(self.PIN_I_ITM_IDX))

        ret = self.http_put(rid, self.rtype, payload)
        self.log_msg("In set_color_xy_bri #780, return code is " + str(ret["status"]))
        return (ret["status"] == 200)  # & self.set_bri(bri)

    def xy_bri_to_rgb(self, x, y, bri):
        """
        Convert CIE XY gamut position to rgb
        :param x: number – minimum: 0 – maximum: 1
        :param y: number – minimum: 0 – maximum: 1
        :param bri: 0-100%
        :return: [r, g, b] each 0-100%
        """

        color_conv = colorconvert.Converter()
        return color_conv.xy_to_rgb(x, y, bri)

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
        log_debug("entering run_server")
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

    def init_server(self):
        self.server = ""
        self.t = ""
        self.http_request_handler = MyHttpRequestHandler
        self.run_server(8080)
        # self.run_server(self._get_input_value(self.PIN_I_SHUEIP))

    def init_device_list(self):
        self.devices = {}  # type: {str, HueGroup_14100_14100.HueDevice}
        self.rid = str(self._get_input_value(self.PIN_I_ITM_IDX))  # type: str
        self.associated_rids = []  # type: [str]
        self.rtype = str()  # type: str
        self.curr_bri = 0  # type: int
        self.device = HueGroup_14100_14100.HueDevice()  # type: HueGroup_14100_14100.HueDevice

    def on_init(self):

        # debug
        log_debug("entering on_init")
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.g_out_sbc = {}  # type: {int, object}
        self.debug = False  # type: bool

        # server
        self.init_server()

        # eventstream
        self.eventstream_thread = threading.Thread()  # type: threading.Thread
        self.eventstream_running = threading.Event()
        self.eventstream_running.set()

        self.init_device_list()

        self.discover_hue()
        self.register_devices()
        self.register_eventstream()

        # get own lamp data if already registered
        data = self.get_data("light/" + self.device.light_id)

        if data["status"] == 200:
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


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


# class MyHttpRequestHandler(SocketServer.BaseRequestHandler):
class MyHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    data_lock = threading.RLock()

    def __init__(self, request, client_address, server):
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.response_content_type = ""
        self.response_data = ""

    def do_GET(self):
        with self.data_lock:
            self.send_response(200)
            self.send_header('Content-type', self.response_content_type)
            self.end_headers()

            self.wfile.write(self.response_data)


def hex2int(msg):
    msg = bytearray(msg)
    val = 0
    val = val | msg[0]
    for byte in msg[1:]:
        val = val << 8
        val = val | byte

    return int(val)


def log_debug(msg):
    print(str(time.time()) + "\tDebug:\t" + str(msg) + " ---")


def get_val(json_data, key, do_xmlcharrefreplace=True):
    # type : (json, str, bool) -> Any

    val = str()

    if type(json_data) != dict:
        return val

    if key in json_data:
        val = json_data[key]
    if (type(val) == unicode) and do_xmlcharrefreplace:
        val = val.encode("ascii", "xmlcharrefreplace")
    return val


############################################


class UnitTests(unittest.TestCase):

    def setUp(self):
        print("\n### setUp")
        with open("credentials.json") as f:
            self.cred = json.load(f)

        self.dummy = HueGroup_14100_14100(0)

        self.dummy.debug_input_value[self.dummy.PIN_I_HUE_KEY] = self.cred["PIN_I_SUSER"]
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_light_id"]
        # self.dummy.debug_rid = self.cred["hue_light_id"]

        # self.dummy.on_init()
        self.dummy.DEBUG = self.dummy.FRAMEWORK.create_debug_section()
        self.dummy.g_out_sbc = {}  # type: {int, object}
        self.dummy.debug = False  # type: bool
        self.dummy.bridge_ip = self.cred["PIN_I_SHUEIP"]

        self.dummy.FRAMEWORK.my_ip = self.cred["my_ip"]
        # self.dummy.debug = True

    def tearDown(self):
        print("\n### tearDown")
        self.dummy.stop_server()

        while self.dummy.eventstream_thread.is_alive():
            print("Eventstream still living...")
            self.dummy.eventstream_running.clear()
            time.sleep(3)

    def test_08_print_devices(self):
        print("\n### ###test_08_print_devices")
        self.dummy.server = ""
        self.dummy.t = ""
        self.dummy.http_request_handler = MyHttpRequestHandler
        # self.dummy.run_server(8080)
        res = self.dummy.register_devices()
        self.assertTrue(res)

    def test_08_server(self):
        print("\n### ###test_08_server")
        self.dummy.init_server()
        self.dummy.init_device_list()
        self.dummy.register_devices()

        time.sleep(5)

        api_path = 'http://127.0.0.1:8080'
        url_parsed = urlparse.urlparse(api_path)
        headers = {'Host': url_parsed.hostname}

        # Build a http request and overwrite host header with the original hostname.
        request = urllib2.Request(api_path, headers=headers)
        # Open the URL and read the response.
        response = urllib2.urlopen(request, data=None, timeout=5)
        data = response.read()
        self.assertEqual(response.getcode(), 200)
        self.assertGreater(len(data), 20)

        with open("../tests/debug_server_return.html", 'w') as out_file:
            out_file.write(data)


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
        self.assertTrue("192" in self.dummy.bridge_ip, "### IP not discovered")

    def generic_on_off(self):
        print("\n### switch off ###")
        self.assertTrue(self.dummy.set_on(False), "### should have been off")
        time.sleep(2)

        self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF] = False

        print("\n### switch on ###")
        self.dummy.on_input_value(self.dummy.PIN_I_ON_OFF, True)
        time.sleep(2)

        self.dummy.stop_eventstream = True
        self.assertTrue(self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF], "### should have been on")

    def test_12_set_on(self):
        print("\n### test_12_set_on")
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_light_id"]
        self.dummy.on_init()

        time.sleep(3)
        self.generic_on_off()

    # def test_13_on_off_group(self):
    # print("\n### test_13_on_off_group")
    # self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_zone_id"]
    # self.generic_on_off()

    def test_14_on_off_zone(self):
        print("\n### test_14_on_off_zone")
        self.dummy.on_init()
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_zone_id"]
        self.generic_on_off()

    def test_15_on_off_room(self):
        print("\n### test_15_on_off_room")
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_room_id"]
        self.generic_on_off()

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
        self.dummy.eventstream_running.set()
        self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF] = None
        self.dummy.g_out_sbc = {}

        self.dummy.on_input_value(self.dummy.PIN_I_TRIGGER, 1)
        res = self.dummy.debug_output_value[self.dummy.PIN_O_STATUS_ON_OFF]

        self.assertTrue(bool == type(res))

    def test_19_xy_to_rgb(self):
        print("\n### test_19_xy_to_rgb")
        [r, g, b] = self.dummy.xy_bri_to_rgb(0.4849, 0.3476, 1)
        self.assertEqual([255, 165, 135], [r, g, b], "#1217")

        [r, g, b] = self.dummy.xy_bri_to_rgb(0.640, 0.330, 0.1043)
        self.assertEqual([125, 0, 0], [r, g, b], "#1220")

    def test_19_rgb_to_xy(self):
        print("\n### test_19_rgb_to_xy")
        [x, y, bri] = self.dummy.rgb_to_xy_bri(255, 0, 0)
        self.assertEqual([0.675, 0.322, 1], [x, y, bri], "#1153")

    def test_19_set_color(self):
        print("\n### test_19_set_color")
        self.dummy.on_init()
        time.sleep(3)

        # red
        self.dummy.debug_input_value[self.dummy.PIN_I_R] = 255
        self.dummy.debug_input_value[self.dummy.PIN_I_G] = 0
        self.dummy.debug_input_value[self.dummy.PIN_I_B] = 0

        self.dummy.on_input_value(self.dummy.PIN_I_R, 255)
        time.sleep(3)

        r = self.dummy.debug_output_value[self.dummy.PIN_O_R]
        g = self.dummy.debug_output_value[self.dummy.PIN_O_G]
        b = self.dummy.debug_output_value[self.dummy.PIN_O_B]
        print(str([r, g, b]))
        self.assertEqual(255, r, "#1182")
        self.assertEqual(75, g, "#1183")
        self.assertEqual(0, b, "#1184")


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
