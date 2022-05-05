# coding: utf8


import unittest
import ssl
import urllib2
import urlparse
import socket
import time
import json
import colorsys
import thread
import threading


# import httplib
# import re
# import struct
# import hashlib


class hsl20_4:
    LOGGING_NONE = 0

    def __init__(self):
        pass

    class BaseModule:
        debug_output_value = {}  # type: float
        debug_set_remanent = {}  # type: float
        debug_input_value = {}

        def __init__(self, a, b):
            pass

        def _get_framework(self):
            f = hsl20_4.Framework()
            return f

        def _get_logger(self, a, b):
            return 0

        def _get_remanent(self, key):
            return 0

        def _set_remanent(self, key, val):
            self.debug_set_remanent = val

        def _set_output_value(self, pin, value):
            self.debug_output_value[int(pin)] = value
            print "# Out: " + str(value) + " @ pin " + str(pin)

        def _set_input_value(self, pin, value):
            self.debug_input_value[int(pin)] = value
            print "# In: " + str(value) + " @ pin " + str(pin)

        def _get_input_value(self, pin):
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
            return "127.0.0.1"

        def get_instance_by_id(self, id):
            return ""

    class DebugHelper:
        def __init__(self):
            pass

        def set_value(self, cap, text):
            print("DEBUG value\t'" + str(cap) + "': " + str(text))

        def add_message(self, msg):
            print("Debug Msg\t" + str(msg))

    ############################################


class HueGroup_14100_14100(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "hsl20_3_Hue")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE, ())
        self.PIN_I_STAT_JSON = 1
        self.PIN_I_BTRIGGER = 2
        self.PIN_I_SHUEIP = 3
        self.PIN_I_NHUEPORT = 4
        self.PIN_I_SUSER = 5
        self.PIN_I_CTRL_GRP = 6
        self.PIN_I_ITM_IDX = 7
        self.PIN_I_BONOFF = 8
        self.PIN_I_NBRI = 9
        self.PIN_I_NHUE = 10
        self.PIN_I_NSAT = 11
        self.PIN_I_NCT = 12
        self.PIN_I_NR = 13
        self.PIN_I_NG = 14
        self.PIN_I_NB = 15
        self.PIN_I_SSCENE = 16
        self.PIN_I_NTRANSTIME = 17
        self.PIN_I_BALERT = 18
        self.PIN_I_NEFFECT = 19
        self.PIN_I_NRELDIM = 20
        self.PIN_I_NDIMRAMP = 21
        self.PIN_O_BSTATUSONOFF = 1
        self.PIN_O_NBRI = 2
        self.PIN_O_NHUE = 3
        self.PIN_O_NSAT = 4
        self.PIN_O_NCT = 5
        self.PIN_O_NR = 6
        self.PIN_O_NG = 7
        self.PIN_O_NB = 8
        self.PIN_O_NREACHABLE = 9
        self.PIN_O_JSON = 10

    ########################################################################################################
    #### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
    ###################################################################################################!!!##

    def log_msg(self, text):
        self.DEBUG.add_message("14100: " + str(text))

    def log_data(self, key, value):
        self.DEBUG.set_value("14100: " + str(key), str(value))

    def set_output_value_sbc(self, pin, val):
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                print ("# SBC: pin " + str(pin) + " <- data not send / " + str(val).decode("utf-8"))
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val

    def hex2int(self, msg):
        msg = bytearray(msg)
        val = 0
        val = val | msg[0]
        for byte in msg[1:]:
            val = val << 8
            val = val | byte

        return int(val)

    def discover_hue(self):
        """

        :rtype: urlparse
        """
        # mDNS query request msg from application
        MCAST_PORT = 5353
        MCAST_GRP = '224.0.0.251'

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
            sock.sendto(query_msg, (MCAST_GRP, MCAST_PORT))
        except socket.error as e:
            self.log_data("Error", "discover: " + str(e))
            sock.close()

        while True:
            try:
                data = sock.recv(1024)
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

                # print('\nHeader: ')
                # print(":".join("{:02x}".format(ord(c)) for c in header))
                # print('\nQuery: ')
                # print(":".join("{:02x}".format(ord(c)) for c in data[12:12+len(search)]))
                # print('\nAnswer: ')
                # print(":".join("{:02x}".format(ord(c)) for c in answers))
                # print("\nAdd records:")
                # print(":".join("{:02x}".format(ord(c)) for c in add_records))

                # process additional records
                ar_offset = 0
                for i in range(ar_count):
                    # get record type (= A) and extrakt ip
                    ar_type = add_records[ar_offset + 2:ar_offset + 4]
                    # print(":".join("{:02x}".format(ord(c)) for c in ar_type))
                    ar_length = add_records[ar_offset + 10: ar_offset + 12]
                    ar_length = self.hex2int(ar_length)
                    # self.log_data("Addition record no. " + str(i), (":".join("{:02x}".format(ord(c)) for c in add_records[ar_offset:ar_offset + 12 + ar_length])))

                    if ar_type == "\x00\x01":  # Type A, get IP & Port
                        ar_ip = add_records[ar_offset + 12:ar_offset + 12 + ar_length]
                        ip1 = self.hex2int(ar_ip[0])
                        ip2 = self.hex2int(ar_ip[1])
                        ip3 = self.hex2int(ar_ip[2])
                        ip4 = self.hex2int(ar_ip[3])

                        ip = str(ip1) + "." + str(ip2) + "." + str(ip3) + "." + str(ip4)
                        self.log_data("Discovered IP", ip)
                        self.bridge_ip = ip

                    ar_offset = ar_offset + 12 + ar_length

                return

            except socket.timeout:
                self.log_msg("Discovery timeout")
                break

        sock.close()

    # get general web request
    def get_data(self, api_cmd):
        """
        {'data': str(result), 'status': str(return code)}
        :rtype: {string, string}
        """
        api_path = 'https://' + self.bridge_ip + '/clip/v2/resource/' + api_cmd
        data = ""
        url_parsed = urlparse.urlparse(api_path)
        headers = {'Host': url_parsed.hostname, "hue-application-key": self._get_input_value(self.PIN_I_SUSER)}

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()

        try:
            if not self.debug:
                # Build a http request and overwrite host header with the original hostname.
                request = urllib2.Request(api_path, headers=headers)
                # Open the URL and read the response.
                response = urllib2.urlopen(request, data=None, timeout=5, context=ctx)
                data = {'data': response.read(), 'status': str(response.getcode())}
                if data["status"] != str(200):
                    print data["data"]
            else:
                data = {'data': "debug", 'status': str(200)}
            self.DEBUG.add_message("14100: Hue bridge response code: " + data["status"])

        except Exception as e:
            self.log_data("Error", "getData: " + str(e))
            data = {'data': str(e), 'status': str(0)}
            print(data)

        return data

    def http_put(self, payload, device_rid):
        # type: (str) -> {str, int}
        """
        {"data": str, "status": int}

        :rtype: {string, int}
        """
        ctrl_grp = bool(self._get_input_value(self.PIN_I_CTRL_GRP))

        api_path = "https://" + self.bridge_ip
        if ctrl_grp:
            api_path = api_path + '/clip/v2/resource/grouped_light/'
        else:
            api_path = api_path + '/clip/v2/resource/light/'

        api_path = api_path + device_rid
        url_parsed = urlparse.urlparse(api_path)
        headers = {"Host": url_parsed.hostname,
                   "Content-type": 'application/json',
                   "hue-application-key": self._get_input_value(self.PIN_I_SUSER)}

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()

        try:
            if not self.debug:
                # Build a http request and overwrite host header with the original hostname.
                request = urllib2.Request(api_path, headers=headers)
                request.get_method = lambda: 'PUT'
                # Open the URL and read the response.
                response = urllib2.urlopen(request, data=payload, timeout=5, context=ctx)
                data = {'data': response.read(), 'status': response.getcode()}
                if data["status"] != 200:
                    print data["data"]["error"]
                    data["status"] = 200
            else:
                data = {'data': '{"success" : True}', 'status': 200}

            self.DEBUG.add_message("14100: Hue bridge response code: " + str(data["status"]))

        except Exception as e:
            self.log_data("Error", "http_put, " + str(e))
            data = {'data': str(e), 'status': 0}

        return data

    # todo dynamic scene
    # PUT 'https://<ipaddress>/clip/v2/resource/scene/<v2-id>'
    # -H 'hue-application-key: <appkey>' -H 'Content-Type: application/json'
    # --data-raw '{"recall": {"action": "dynamic_palette"}}'

    def register_devices(self):
        # type: () -> bool
        item_types = {"device", "room", "scene", "zone", "grouped_light"}

        for item_type in item_types:
            data = self.get_data(item_type)["data"]

            try:
                data = json.loads(data)
                if "data" not in data:
                    self.log_msg("In register_devices, no data field in '" + item_type + "' reply")
                    continue

                data = data["data"]

                for data_set in data:
                    device_id = data_set["id"]
                    self.devices[device_id] = {}
                    self.devices[device_id]["type"] = item_type
                    if item_type == "light" or item_type == "scene" or item_type == "room" or item_type == "zone":
                        self.devices[device_id]["name"] = data_set["metadata"]["name"]
                    else:
                        self.devices[device_id]["name"] = str()

                    if item_type == "scene":
                        self.devices[device_id]["associated group"] = data_set["group"]["rid"]

                    if item_type == "grouped_light" or item_type == "scene":
                        self.devices[device_id]["light"] = data_set["id"]
                    else:
                        device_services = data_set["services"]
                        for service in device_services:
                            service_type = service["rtype"]
                            self.devices[device_id][service_type] = service["rid"]

            except Exception as e:
                self.log_msg("In register_devices '" + str(e) + "' for " + item_type)
                return False

        self.log_data("Items", json.dumps(self.devices, sort_keys=True, indent=4))
        return True

    def register_eventstream(self):
        thread.start_new_thread(self.eventstream, ())

    def eventstream(self):
        while True:
            self.log_msg("Connecting to eventstream...")
            api_path = 'https://' + self.bridge_ip + '/eventstream/clip/v2'
            url_parsed = urlparse.urlparse(api_path)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_NONE)
            # sock.settimeout(5)

            try:
                sock.bind(('', 0))
                sock.connect((self.bridge_ip, 443))
                sock.send("GET /eventstream/clip/v2 HTTP/1.1\r\n")
                sock.send("Host: " + url_parsed.hostname + "\r\n")
                sock.send("hue-application-key: " + self._get_input_value(self.PIN_I_SUSER) + "\r\n")
                sock.send("Accept: text/event-stream\r\n\r\n")

            except socket.error as e:
                self.log_data("Error", "discover: " + str(e))
                sock.close()

            while True:
                try:
                    data = sock.recv(1024)
                    data = data[data.find("data: ") + 6:]
                    data = str(data).replace("\r", '').replace("\n", '')
                    self.process_json(data)

                    if self.stop_eventstream:
                        return

                except socket.timeout:
                    self.log_msg("Eventstream timeout")
                    break

                except Exception as e:
                    self.log_msg(str(e))
                    break

            print("Exit thread")
            sock.close()
            return str()

    def process_json(self, msg):
        # type: (str) -> None
        # --
        # [{"creationtime":"2022-05-02T21:25:32Z","data":
        # [
        #   {
        #     "id":"fbbd07de-5bf0-4dd6-b819-db3d9ee9a429", ### service id of device
        #     "id_v1":"/lights/3",
        #     "on":{"on":false},
        #     "owner":
        #       {
        #         "rid":"3603093d-b456-4d02-a6ab-6a23aad1f6ba", ### device id
        #         "rtype":"device"
        #       },"type":"light"
        #   }
        # ],
        # "id":"9a3e1580-4fc3-40fb-b280-73c1bb45f0d3","type":"update"}]

        out = json.dumps(msg)
        self.set_output_value_sbc(self.PIN_O_JSON, out)

        try:
            json_obj = json.loads(msg)
            for data_set in json_obj:
                device_id = data_set["data"]["owner"]["rid"]

                if device_id == self._get_input_value(self.PIN_I_ITM_IDX):
                    if "on" in data_set["data"]:
                        on = data_set["data"]["on"]["on"]
                        self.set_output_value_sbc(self.PIN_O_BSTATUSONOFF, on)

                    if "color" in data_set["data"]:
                        color = data_set["data"]["color"]
                        # todo calculate rgb

                    if "dimming" in data_set["data"]:
                        dimming = data_set["data"]["dimming"]
                        self.set_output_value_sbc(self.PIN_O_NBRI, data_set["data"]["dimming"]["brightness"])

        except Exception as e:
            self.log_msg("Error in 'process_json', '" + str(e) + "', with message '" + str(out) + "'")

    def get_rig(self, service):
        # type: (str) -> str
        device_id = self._get_input_value(self.PIN_I_ITM_IDX)
        if device_id not in self.devices:
            self.log_msg("In 'get_rid', device id not yet registered in self.devices.")
            return str()

        if service not in self.devices[device_id]:
            self.log_msg("In 'get_rid', service '" + service + "' not registered for device in self.devices.")
            return str()

        return self.devices[device_id][service]

    def set_on(self, set_on):
        # type: (bool) -> bool

        rid = self.get_rig("light")
        if not rid:
            return False

        if set_on:
            payload = '{"on":{"on":true}}'
        else:
            payload = '{"on":{"on":false}}'

        ret = self.http_put(payload, rid)
        return ret["status"] == 200

    def set_dimming(self, brightness):
        # type: (int) -> bool
        """
        Brightness percentage. value cannot be 0, writing 0 changes it to the lowest possible brightness

        :param brightness: number – maximum: 100
        :return: True if successful, otherwise False
        """
        rid = self.get_rig("light")
        if not rid:
            return False

        payload = '{"dimming":{"brightness":' + str(brightness) + '}}'
        ret = self.http_put(payload, rid)
        return ret["status"] == 200

    def set_scene(self, scene):
        payload = '{"scene":"' + scene + '"}'
        ret = self.http_put(payload)
        return "success" in ret["data"]

    def set_effect(self, effect):
        payload = '{"effect":"'

        if effect:
            payload = payload + 'colorloop"}'
        else:
            payload = payload + 'none"}'

        ret = self.http_put(payload)
        return "success" in ret["data"]

    def set_alert(self, alert):
        payload = ""
        if alert:
            payload = '{"alert":"lselect"}'
        else:
            payload = '{"alert":"none"}'

        ret = self.http_put(payload)
        return "success" in ret["data"]

    def set_hue_color(self, hue_col):
        payload = '{"hue":' + str(hue_col) + '}'
        ret = self.http_put(payload)
        return "success" in ret["data"]

    def set_sat(self, sat):
        payload = '{"sat":' + str(sat) + '}'
        ret = self.http_put(payload)
        return "success" in ret["data"]

    def set_ct(self, ct):
        payload = '{"ct":' + str(ct) + '}'
        ret = self.http_put(payload)
        return "success" in ret["data"]

    def prep_dim(self, val):
        self.DEBUG.set_value("Dim cmd", str(val) + " " + str(type(val)))

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
        if self.stop:
            return

        api_url = str(self._get_input_value(self.PIN_I_SHUEIP))
        api_port = int(self._get_input_value(self.PIN_I_NHUEPORT))
        api_user = str(self._get_input_value(self.PIN_I_SUSER))
        itm_idx = int(self._get_input_value(self.PIN_I_ITM_IDX))

        new_bri = int(self.curr_bri + self.interval)
        if new_bri > 255:
            new_bri = 255
        elif new_bri < 1:
            new_bri = 1

        self.set_bri(new_bri)

        duration = float(self._get_input_value(self.PIN_I_NDIMRAMP))
        steps = 255 / abs(self.interval)
        step = float(round(duration / steps, 4))

        self.timer = threading.Timer(step, self.do_dim)
        self.timer.start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.g_out_sbc = {}
        self.debug = False # type: bool
        self.bridge_ip = self._get_input_value(self.PIN_I_SHUEIP)
        self.stop_eventstream = False  # type: bool
        self.devices = {}  # type: Dict[device_id, [service_type, rid]]

    def on_input_value(self, index, value):
        res = False

        # Process State
        api_url = str(self._get_input_value(self.PIN_I_SHUEIP))
        api_port = int(self._get_input_value(self.PIN_I_NHUEPORT))
        api_user = str(self._get_input_value(self.PIN_I_SUSER))
        itm_idx = str(self._get_input_value(self.PIN_I_ITM_IDX))
        hue_state = {"data": str(self._get_input_value(self.PIN_I_STAT_JSON)), "status": 200}
        bri = int(self._get_input_value(self.PIN_I_NBRI) / 100.0 * 255.0)
        hue_ol = int(self._get_input_value(self.PIN_I_NHUE))
        sat = int(self._get_input_value(self.PIN_I_NSAT) / 100.0 * 255.0)
        ct = int(self._get_input_value(self.PIN_I_NCT))
        ctrl_group = self._get_input_value(self.PIN_I_CTRL_GRP)

        # If trigger == 1, get data via web request
        if (self.PIN_I_BTRIGGER == index) and (bool(value)):
            if ctrl_group:
                hue_state = self.get_data("group")
            else:
                hue_state = self.get_data("light")

        if ((self.PIN_I_BTRIGGER == index) or
                (self.PIN_I_STAT_JSON == index)):
            if hue_state["data"]:
                if itm_idx > 0:
                    self.read_json(hue_state["data"], itm_idx)
                    self.set_output_value_sbc(self.PIN_O_JSON, hue_state["data"])

        # Process set commands
        if (self._get_input_value(self.PIN_I_SUSER) == "") or (self._get_input_value(self.PIN_I_SHUEIP) == ""):
            return

        if self.PIN_I_BONOFF == index:
            res = self.set_on(value)
            if res:
                self.set_output_value_sbc(self.PIN_O_BSTATUSONOFF, value)

        elif self.PIN_I_SSCENE == index:
            res = self.set_scene(value)
            if res:
                self.set_output_value_sbc(self.PIN_O_BSTATUSONOFF, True)

        elif self.PIN_I_NBRI == index:
            self.set_on(True)
            res = self.set_bri(bri)
            print(res)
            if res:
                self.set_output_value_sbc(self.PIN_O_NBRI, bri / 255.0 * 100.0)

        elif self.PIN_I_NHUE == index:
            self.set_on(True)
            res = self.set_hue_color(hue_ol)
            if res:
                self.set_output_value_sbc(self.PIN_O_NHUE, hue_ol)

        elif self.PIN_I_NSAT == index:
            self.set_on(True)
            res = self.set_sat(sat)
            if res:
                self.set_output_value_sbc(self.PIN_O_NSAT, sat / 255.0 * 100)

        elif self.PIN_I_NCT == index:
            self.set_on(True)
            res = self.set_ct(ct)
            if res:
                self.set_output_value_sbc(self.PIN_O_NCT, ct)

        elif ((self.PIN_I_NR == index) or
              (self.PIN_I_NG == index) or
              (self.PIN_I_NB == index)):
            self.set_on(True)

            red = int(int(self._get_input_value(self.PIN_I_NR)) * 2.55)
            green = int(int(self._get_input_value(self.PIN_I_NG)) * 2.55)
            blue = int(int(self._get_input_value(self.PIN_I_NB)) * 2.55)
            # h, s, v = self.rgb2hsv(r, g, b)
            h, s, v = colorsys.rgb_to_hsv(r=(red / 255.0), g=(green / 255.0), b=(blue / 255.0))
            h = int(360.0 * 182.04 * h)
            s = int(s * 255)
            v = int(v * 255)

            ret1 = self.set_bri(v)
            ret2 = self.set_hue_color(h)
            ret3 = self.set_sat(s)

            if ret1 and ret2 and ret3:
                # set rgb as output
                self.set_output_value_sbc(self.PIN_O_NR, red)
                self.set_output_value_sbc(self.PIN_O_NG, green)
                self.set_output_value_sbc(self.PIN_O_NB, blue)

        elif self.PIN_I_BALERT == index:
            alert = int(self._get_input_value(self.PIN_I_BALERT))
            self.set_alert(alert)
            ###

        elif self.PIN_I_NEFFECT == index:
            effect = int(self._get_input_value(self.PIN_I_NEFFECT))
            self.set_effect(effect)

        elif self.PIN_I_NRELDIM == index:
            self.prep_dim(value)


############################################


class UnitTests(unittest.TestCase):

    def setUp(self):
        print("\n###setUp")
        with open("credentials.txt") as f:
            self.cred = json.load(f)

        self.dummy = HueGroup_14100_14100(0)
        self.dummy.on_init()

        self.dummy.debug_input_value[self.dummy.PIN_I_SHUEIP] = self.cred["PIN_I_SHUEIP"]
        self.dummy.debug_input_value[self.dummy.PIN_I_SUSER] = self.cred["PIN_I_SUSER"]

        self.dummy.debug_input_value[self.dummy.PIN_I_CTRL_GRP] = 0
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_device_id"]
        self.dummy.devices[self.cred["hue_device_id"]] = {}
        self.dummy.devices[self.cred["hue_device_id"]]["light"] = self.cred["hue_light_id"]
        self.dummy.debug_rid = self.cred["hue_light_id"]

        self.dummy.bridge_ip = self.cred["PIN_I_SHUEIP"]
        self.dummy.stop_eventstream = True

    def tearDown(selfself):
        print("\n###tearDown")
        pass

    def test_get_rig(self):
        print("\n###test_get_rig")
        ret = self.dummy.get_rig("light")
        self.assertEqual(ret, self.dummy.debug_rid)
        ret = self.dummy.get_rig("dummy")
        self.assertEqual(ret, str())

    def test_discover(self):
        print("\n###test_discover")
        self.dummy.bridge_ip = None
        self.dummy.discover_hue()
        self.assertTrue("192" in self.dummy.bridge_ip)

    def test_get_data(self):
        print("\n###test_get_data")
        data = self.dummy.get_data('device')
        print(data["data"])
        self.assertTrue("id" in data["data"])

    def test_set_on(self):
        print("###test_set_on")
        self.assertTrue(self.dummy.set_on(0))
        time.sleep(3)
        self.assertTrue(self.dummy.set_on(1))
        time.sleep(3)
        self.assertTrue(self.dummy.set_on(0))

#    def test_eventstream(self):
#        self.dummy.stop_eventstream = False
#        self.dummy.register_eventstream()

    def test_print_devices(self):
        print("###test_print_devices")
        res = self.dummy.register_devices()
        self.assertTrue(res)

    def test_dimming(self):
        self.dummy.set_on(True)
        time.sleep(2)
        res = self.dummy.set_dimming(70)
        self.assertTrue(res)
        time.sleep(2)
        res = self.dummy.set_dimming(50)
        self.assertTrue(res)
        time.sleep(2)
        res = self.dummy.set_dimming(30)
        self.assertTrue(res)
        time.sleep(2)
        self.dummy.set_on(False)



#     def test_setBri(self):
#         self.dummy.debug = True
#
#         api_url = "192.168.0.10"
#         api_port = "80"
#         api_user = "debug"
#         group = "1"
#         light = 3
#
#         ret = self.dummy.set_bri(api_url, api_port, api_user, group, 100)
#         self.assertTrue(ret)
#         self.assertEqual(self.dummy.curr_bri, 100)
#
#     def test_trigger(self):
#         self.dummy.on_input_value(self.dummy.PIN_I_BTRIGGER, 1)
#         self.assertNotEqual("", self.dummy.debug_output_value[self.dummy.PIN_O_JSON])
#
#     def test_on_off_group(self):
#         print("###test_on_off_group")
#         self.dummy.debug_input_value[self.dummy.PIN_I_CTRL_GRP] = 1
#         self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = 1
#
#         self.dummy.on_input_value(self.dummy.PIN_I_BONOFF, 0)
#         self.assertEqual(0, self.dummy.debug_output_value[self.dummy.PIN_O_BSTATUSONOFF])
#         time.sleep(3)
#         self.dummy.on_input_value(self.dummy.PIN_I_BONOFF, 1)
#         self.assertEqual(1, self.dummy.debug_output_value[self.dummy.PIN_O_BSTATUSONOFF])
#         time.sleep(3)
#         self.dummy.on_input_value(self.dummy.PIN_I_BONOFF, 0)
#         self.assertEqual(0, self.dummy.debug_output_value[self.dummy.PIN_O_BSTATUSONOFF])
#
#     def test_read_json(self):
#         self.dummy.debug = True
#         self.dummy.curr_bri = 204
#
#         api_url = "192.168.0.10"
#         api_port = "80"
#         api_user = "debug"
#         group = "1"
#         light = 3
#
#         retGroups = {
#             "data": '{"1": {"name": "Wohnzimmer", "lights": ["3", "5"], "state": {"any_on": true, "all_on": true}, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "none", "xy": [0.4779, 0.3823], "bri": 204, "ct": 399, "sat": 121}, "recycle": false, "sensors": [], "type": "Room", "class": "Living room"}, "3": {"name": "Thilo", "lights": [], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "alert": "none"}, "recycle": false, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "2": {"name": "Bad OG", "lights": ["4"], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "hue": 8402, "colormode": "xy", "effect": "none", "alert": "select", "xy": [0.4575, 0.4099], "bri": 254, "ct": 366, "sat": 140}, "recycle": false, "sensors": [], "type": "Room", "class": "Bathroom"}, "5": {"name": "Nora", "lights": ["7", "8"], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "bri": 1, "alert": "select"}, "recycle": false, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "4": {"name": "Flur DG", "lights": ["6"], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "bri": 254, "alert": "select"}, "recycle": false, "sensors": [], "type": "Room", "class": "Hallway"}, "7": {"name": "TV", "lights": ["3"], "state": {"any_on": true, "all_on": true}, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "select", "xy": [0.4779, 0.3823], "bri": 204, "ct": 399, "sat": 121}, "recycle": false, "sensors": [], "type": "Zone", "class": "Downstairs"}, "6": {"name": "Garage", "lights": ["9"], "state": {"any_on": true, "all_on": true}, "action": {"on": true, "hue": 0, "colormode": "ct", "effect": "none", "alert": "select", "xy": [0.3805, 0.3769], "bri": 254, "ct": 370, "sat": 0}, "recycle": false, "sensors": [], "type": "Room", "class": "Carport"}}'}
#         # retLights = dummy.getData(api_url, api_port, api_user, "lights")
#         ret = self.dummy.read_json(retGroups["data"], light)
#         res = '{"1": {"name": "Wohnzimmer", "lights": ["3", "5"], "state": {"any_on": true, "all_on": true}, "recycle": false, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "none", "xy": [0.4779, 0.3823], "bri": 204, "sat": 121, "ct": 399}, "sensors": [], "type": "Room", "class": "Living room"}, "3": {"name": "Thilo", "lights": [], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "alert": "none"}, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "2": {"name": "Bad OG", "lights": ["4"], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "hue": 8402, "colormode": "xy", "effect": "none", "alert": "select", "xy": [0.4575, 0.4099], "bri": 254, "sat": 140, "ct": 366}, "sensors": [], "type": "Room", "class": "Bathroom"}, "5": {"name": "Nora", "lights": ["7", "8"], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "bri": 1, "alert": "select"}, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "4": {"name": "Flur DG", "lights": ["6"], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "bri": 254, "alert": "select"}, "sensors": [], "type": "Room", "class": "Hallway"}, "7": {"name": "TV", "lights": ["3"], "state": {"any_on": true, "all_on": true}, "recycle": false, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "select", "xy": [0.4779, 0.3823], "bri": 204, "sat": 121, "ct": 399}, "sensors": [], "type": "Zone", "class": "Downstairs"}, "6": {"name": "Garage", "lights": ["9"], "state": {"any_on": true, "all_on": true}, "recycle": false, "action": {"on": true, "hue": 0, "colormode": "ct", "effect": "none", "alert": "select", "xy": [0.3805, 0.3769], "bri": 254, "sat": 0, "ct": 370}, "sensors": [], "type": "Room", "class": "Carport"}}'
#         self.assertEqual(res, ret)
#         # ret = dummy.readLightsJson(retLights["data"], light)
#
#         # sScene = "mYJ1jB9LmBAG6yN"
#         # sScene = "qhfcIHIJ9JuYK19"
#         # nHueCol = 24381
#
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
