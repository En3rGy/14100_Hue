# coding: utf8


import unittest
import ssl
import urllib2
import urlparse
import socket
import time
import httplib
import json
import colorsys
import threading

import re
import struct
import hashlib


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
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_STAT_JSON=1
        self.PIN_I_BTRIGGER=2
        self.PIN_I_SHUEIP=3
        self.PIN_I_NHUEPORT=4
        self.PIN_I_SUSER=5
        self.PIN_I_CTRL_GRP=6
        self.PIN_I_ITM_IDX=7
        self.PIN_I_BONOFF=8
        self.PIN_I_NBRI=9
        self.PIN_I_NHUE=10
        self.PIN_I_NSAT=11
        self.PIN_I_NCT=12
        self.PIN_I_NR=13
        self.PIN_I_NG=14
        self.PIN_I_NB=15
        self.PIN_I_SSCENE=16
        self.PIN_I_NTRANSTIME=17
        self.PIN_I_BALERT=18
        self.PIN_I_NEFFECT=19
        self.PIN_I_NRELDIM=20
        self.PIN_I_NDIMRAMP=21
        self.PIN_O_BSTATUSONOFF=1
        self.PIN_O_NBRI=2
        self.PIN_O_NHUE=3
        self.PIN_O_NSAT=4
        self.PIN_O_NCT=5
        self.PIN_O_NR=6
        self.PIN_O_NG=7
        self.PIN_O_NB=8
        self.PIN_O_NREACHABLE=9
        self.PIN_O_JSON=10

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

                    if ar_type == "\x00\x01": # Type A, get IP & Port
                        ar_ip = add_records[ar_offset + 12:ar_offset + 12 + ar_length]
                        ip1 = self.hex2int(ar_ip[0])
                        ip2 = self.hex2int(ar_ip[1])
                        ip3 = self.hex2int(ar_ip[2])
                        ip4 = self.hex2int(ar_ip[3])

                        ip = str(ip1) + "." + str(ip2) + "." + str(ip3) + "." + str(ip4)
                        self.log_data("Discovered IP", ip)
                        return ip

                    ar_offset = ar_offset + 12 + ar_length

                return str()

            except socket.timeout:
                self.log_msg("Discovery timeout")
                break

        sock.close()
        return str()

    # get general web request
    def get_data(self, api_url, api_user, api_cmd):
        api_path = 'https://' + api_url + '/clip/v2/resource/' + api_cmd
        data = ""
        url_parsed = urlparse.urlparse(api_path)
        headers = {'Host': url_parsed.hostname, "hue-application-key": api_user}

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
            self.DEBUG.add_message("14100: Hue bridge response code: " + data["status"])

        except Exception as e:
            self.log_data("Error", "getData: " + str(e))
            data = {'data': str(e), 'status': 0}

        return data

    def http_put(self, api_url, api_user, group, payload):
        ctrl_grp = bool(self._get_input_value(self.PIN_I_CTRL_GRP))
        api_path = "https://" + api_url

        if ctrl_grp:
            api_path = api_path + '/clip/v2/resource/grouped_light/' + str(group)
        else:
            api_path = api_path + '/clip/v2/resource/light/' + str(group)

        url_parsed = urlparse.urlparse(api_path)
        headers = {"Host": url_parsed.hostname,
                   "Content-type": 'application/json',
                   "hue-application-key": api_user}

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()

        try:
            if not self.debug:
                # Build a http request and overwrite host header with the original hostname.
                request = urllib2.Request(api_path, headers=headers)
                request.get_method = lambda: 'PUT'
                # Open the URL and read the response.
                response = urllib2.urlopen(request, data=payload, timeout=5, context=ctx)
                data = {'data': response.read(), 'status': str(response.getcode())}
            else:
                data = {'data': '{"success" : True}', 'status': str(200)}

            self.DEBUG.add_message("14100: Hue bridge response code: " + data["status"])

        except Exception as e:
            self.log_data("Error", "http_put, " + str(e))
            data = {'data': str(e), 'status': 0}

        return data

    def eventstream(self, api_url, api_user):
        # curl --insecure -N -H 'hue-application-key: <appkey>' -H 'Accept: text/event-stream' https://<ipaddress>/eventstream/clip/v2
        api_path = 'https://' + api_url + '/eventstream/clip/v2'
        url_parsed = urlparse.urlparse(api_path)
        headers = {'Host': url_parsed.hostname, "hue-application-key": api_user, "Accept": "text/event-stream"}

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()

        try:
            if not self.debug:
                # Build a http request and overwrite host header with the original hostname.
                request = urllib2.Request(api_path, headers=headers)
                # Open the URL and read the response.
                response = urllib2.urlopen(request, data=None, timeout=30, context=ctx)
                data = {'data': response.read(), 'status': str(response.getcode())}
            else:
                data = {'data': "debug", 'status': str(200)}
            self.DEBUG.add_message("14100: Hue bridge response code: " + data["status"])

        except Exception as e:
            self.log_data("Error", "getData: " + str(e))
            data = {'data': str(e), 'status': 0}

        return data

    def read_json(self, json_state, hue_id):
        try:
            json_state = json.loads(json_state)
            ctrl_grp = bool(self._get_input_value(self.PIN_I_CTRL_GRP))
            mode = 'state'

            if ctrl_grp:
                mode = 'action'

            if str(idx) in json_state:
                json_device = json_state[str(idx)]
            else:
                print("Device not found in json in  read_groups_json")
                return ""

            if mode in json_device:
                action_sub = json_device[mode]
                on_off = action_sub['on']
                self.set_output_value_sbc(self.PIN_O_BSTATUSONOFF, on_off)

                if 'reachable' in action_sub:
                    reachable = int(action_sub['reachable'])
                    self.set_output_value_sbc(self.PIN_O_NREACHABLE, reachable)
                if 'bri' in action_sub:
                    bri = int(action_sub['bri'])
                    self.curr_bri = bri
                    self.set_output_value_sbc(self.PIN_O_NBRI, bri / 255.0 * 100.0)
                if 'hue' in action_sub:
                    hue = action_sub['hue']
                    self.set_output_value_sbc(self.PIN_O_NHUE, hue)
                if 'sat' in action_sub:
                    sat = action_sub['sat']
                    self.set_output_value_sbc(self.PIN_O_NSAT, sat / 255.0 * 100)
                if 'ct' in action_sub:
                    ct = action_sub['ct']
                    self.set_output_value_sbc(self.PIN_O_NCT, ct)

                r, g, b = colorsys.hsv_to_rgb(hue / 360.0 / 182.04, sat / 255.0, bri / 255.0)

                r = int(r * 100.0)
                g = int(g * 100.0)
                b = int(b * 100.0)

                self.set_output_value_sbc(self.PIN_O_NR, r)
                self.set_output_value_sbc(self.PIN_O_NG, g)
                self.set_output_value_sbc(self.PIN_O_NB, b)
        except:
            json_state = []

        return json.dumps(json_state)

    def hue_on_off(self, api_url, api_port, api_user, group, set_on):
        payload = ""
        if set_on:
            payload = '{"on":{"on":true}}'
        else:
            payload = '{"on":{"on":false}}'

        ret = self.http_put(api_url, api_user, group, payload)
        return ret["status"] == '200'

    def set_scene(self, api_url, api_port, api_user, group, scene):
        payload = '{"scene":"' + scene + '"}'
        ret = self.http_put(api_url, api_user, group, payload)
        return "success" in ret["data"]

    def set_effect(self, api_url, api_port, api_user, group, effect):
        payload = '{"effect":"'

        if effect:
            payload = payload + 'colorloop"}'
        else:
            payload = payload + 'none"}'

        ret = self.http_put(api_url, api_user, group, payload)
        return "success" in ret["data"]

    def set_alert(self, api_url, api_port, api_user, group, alert):
        payload = ""
        if alert:
            payload = '{"alert":"lselect"}'
        else:
            payload = '{"alert":"none"}'

        ret = self.http_put(api_url, api_user, group, payload)
        return "success" in ret["data"]

    def set_bri(self, api_url, api_port, api_user, group, bri):
        if bri > 0:
            self.hue_on_off(api_url, api_port, api_user, group, True)
        payload = '{"bri":' + str(bri) + '}'
        ret = self.http_put(api_url, api_user, group, payload)
        if "success" in ret["data"]:
            self.curr_bri = bri
        return "success" in ret["data"]

    def set_hue_color(self, api_url, api_port, api_user, group, hue_col):
        payload = '{"hue":' + str(hue_col) + '}'
        ret = self.http_put(api_url, api_user, group, payload)
        return "success" in ret["data"]

    def set_sat(self, api_url, api_port, api_user, group, sat):
        payload = '{"sat":' + str(sat) + '}'
        ret = self.http_put(api_url, api_user, group, payload)
        return "success" in ret["data"]

    def set_ct(self, api_url, api_port, api_user, group, ct):
        payload = '{"ct":' + str(ct) + '}'
        ret = self.http_put(api_url, api_user, group, payload)
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

        self.set_bri(api_url, api_port, api_user, itm_idx, new_bri)

        duration = float(self._get_input_value(self.PIN_I_NDIMRAMP))
        steps = 255 / abs(self.interval)
        step = float(round(duration / steps, 4))

        self.timer = threading.Timer(step, self.do_dim)
        self.timer.start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.g_out_sbc = {}
        self.debug = False
        self.curr_bri = 0
        self.interval = 0
        self.timer = threading.Timer(1000, None)
        self.stop = False

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
                hue_state = self.get_data(api_url, api_user, "group")
            else:
                hue_state = self.get_data(api_url, api_user, "light")

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
            res = self.hue_on_off(api_url, api_port, api_user, itm_idx, value)
            if res:
                self.set_output_value_sbc(self.PIN_O_BSTATUSONOFF, value)

        elif self.PIN_I_SSCENE == index:
            res = self.set_scene(api_url, api_port, api_user, itm_idx, value)
            if res:
                self.set_output_value_sbc(self.PIN_O_BSTATUSONOFF, True)

        elif self.PIN_I_NBRI == index:
            self.hue_on_off(api_url, api_port, api_user, itm_idx, True)
            res = self.set_bri(api_url, api_port, api_user, itm_idx, bri)
            print(res)
            if res:
                self.set_output_value_sbc(self.PIN_O_NBRI, bri / 255.0 * 100.0)

        elif self.PIN_I_NHUE == index:
            self.hue_on_off(api_url, api_port, api_user, itm_idx, True)
            res = self.set_hue_color(api_url, api_port, api_user, itm_idx, hue_ol)
            if res:
                self.set_output_value_sbc(self.PIN_O_NHUE, hue_ol)

        elif self.PIN_I_NSAT == index:
            self.hue_on_off(api_url, api_port, api_user, itm_idx, True)
            res = self.set_sat(api_url, api_port, api_user, itm_idx, sat)
            if res:
                self.set_output_value_sbc(self.PIN_O_NSAT, sat / 255.0 * 100)

        elif self.PIN_I_NCT == index:
            self.hue_on_off(api_url, api_port, api_user, itm_idx, True)
            res = self.set_ct(api_url, api_port, api_user, itm_idx, ct)
            if res:
                self.set_output_value_sbc(self.PIN_O_NCT, ct)

        elif ((self.PIN_I_NR == index) or
              (self.PIN_I_NG == index) or
              (self.PIN_I_NB == index)):
            self.hue_on_off(api_url, api_port, api_user, itm_idx, True)

            red = int(int(self._get_input_value(self.PIN_I_NR)) * 2.55)
            green = int(int(self._get_input_value(self.PIN_I_NG)) * 2.55)
            blue = int(int(self._get_input_value(self.PIN_I_NB)) * 2.55)
            # h, s, v = self.rgb2hsv(r, g, b)
            h, s, v = colorsys.rgb_to_hsv(r=(red / 255.0), g=(green / 255.0), b=(blue / 255.0))
            h = int(360.0 * 182.04 * h)
            s = int(s * 255)
            v = int(v * 255)

            ret1 = self.set_bri(api_url, api_port, api_user, itm_idx, v)
            ret2 = self.set_hue_color(api_url, api_port, api_user, itm_idx, h)
            ret3 = self.set_sat(api_url, api_port, api_user, itm_idx, s)

            if ret1 and ret2 and ret3:
                # set rgb as output
                self.set_output_value_sbc(self.PIN_O_NR, red)
                self.set_output_value_sbc(self.PIN_O_NG, green)
                self.set_output_value_sbc(self.PIN_O_NB, blue)

        elif self.PIN_I_BALERT == index:
            alert = int(self._get_input_value(self.PIN_I_BALERT))
            self.set_alert(api_url, api_port, api_user, itm_idx, alert)
            ###

        elif self.PIN_I_NEFFECT == index:
            effect = int(self._get_input_value(self.PIN_I_NEFFECT))
            self.set_effect(api_url, api_port, api_user, itm_idx, effect)

        elif self.PIN_I_NRELDIM == index:
            self.prep_dim(value)


############################################


class UnitTests(unittest.TestCase):

    def setUp(self):
        print("\n ##setUp")
        with open("credentials.txt") as f:
            self.cred = json.load(f)

        self.dummy = HueGroup_14100_14100(0)
        self.dummy.on_init()

        self.dummy.debug_input_value[self.dummy.PIN_I_SHUEIP] = self.cred["PIN_I_SHUEIP"]
        self.dummy.debug_input_value[self.dummy.PIN_I_SUSER] = self.cred["PIN_I_SUSER"]
        self.dummy.debug_input_value[self.dummy.PIN_I_NHUEPORT] = self.cred["PIN_I_NHUEPORT"]

        self.dummy.debug_input_value[self.dummy.PIN_I_CTRL_GRP] = 0
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["Hue_id"]

    def tearDown(selfself):
        print("\n ##tearDown")
        pass

    def test_discover(self):
        print("\n###test_discover")
        data = self.dummy.discover_hue()
        self.assertTrue("192" in data)

    def test_get_data(self):
        print("\n###test_get_data")
        data = self.dummy.get_data(str(self.dummy._get_input_value(self.dummy.PIN_I_SHUEIP)),
                                   str(self.dummy._get_input_value(self.dummy.PIN_I_SUSER)),
                                   'device')
        print(data["data"])
        self.assertTrue("id" in data["data"])

    def test_on_off_light(self):
        print("###test_on_off_light")
        self.dummy.on_input_value(self.dummy.PIN_I_BONOFF, 0)
        self.assertEqual(0, self.dummy.debug_output_value[self.dummy.PIN_O_BSTATUSONOFF])
        time.sleep(3)
        self.dummy.on_input_value(self.dummy.PIN_I_BONOFF, 1)
        self.assertEqual(1, self.dummy.debug_output_value[self.dummy.PIN_O_BSTATUSONOFF])
        time.sleep(3)
        self.dummy.on_input_value(self.dummy.PIN_I_BONOFF, 0)
        self.assertEqual(0, self.dummy.debug_output_value[self.dummy.PIN_O_BSTATUSONOFF])

    # todo: curl --insecure -N -H 'hue-application-key: <appkey>' -H 'Accept: text/event-stream' https://<ipaddress>/eventstream/clip/v2

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
