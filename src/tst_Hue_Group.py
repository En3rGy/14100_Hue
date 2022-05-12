# coding: utf8


import unittest
import ssl
import urllib2
import urlparse
import socket
import time
import json
# import colorsys
import thread
# import threading


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
            print "# Out: pin " + str(pin) + " <- \t" + str(value)

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
        self.PIN_I_HUE_KEY=4
        self.PIN_I_ITM_IDX=5
        self.PIN_I_BONOFF=6
        self.PIN_I_BRI=7
        self.PIN_I_NHUE=8
        self.PIN_I_NR=9
        self.PIN_I_NG=10
        self.PIN_I_NB=11
        self.PIN_I_SSCENE=12
        self.PIN_I_NTRANSTIME=13
        self.PIN_I_BALERT=14
        self.PIN_I_NEFFECT=15
        self.PIN_I_NRELDIM=16
        self.PIN_I_NDIMRAMP=17
        self.PIN_O_BSTATUSONOFF=1
        self.PIN_O_BRI=2
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

    # get general web request
    def get_data(self, api_cmd):
        """
        {'data': str(result), 'status': str(return code)}
        :rtype: {string, string}
        """
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
                if data["status"] != str(200):
                    print data["data"]
            else:
                data = {'data': "debug", 'status': str(200)}

            self.log_msg("In get_data, Hue bridge response code for '" + api_cmd + "' is " + data["status"])

        except Exception as e:
            self.log_msg("in get_data, " + str(e))
            data = {'data': str(e), 'status': str(0)}
            print(data)

        self.process_json(json.loads(data["data"]))
        return data

    def http_put(self, device_rid, api_path, payload):
        # type: (str, str, str) -> {str, int}

        api_path = "https://" + self.bridge_ip + '/clip/v2/resource/' + api_path + "/" + device_rid
        # todo add szene, zone, etc.

        url_parsed = urlparse.urlparse(api_path)
        headers = {"Host": url_parsed.hostname,
                   "Content-type": 'application/json',
                   "hue-application-key": str(self._get_input_value(self.PIN_I_HUE_KEY))}

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
                    print (str(data["data"]["error"]))
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
        item_types = {"device", "room", "scene", "zone", "grouped_light"}  # "light" is intentionally missing

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

                    if device_id not in self.devices:
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
                self.log_msg("Exception in register_devices " + str(e) + " for " + item_type)
                return False

        self.log_data("Items", json.dumps(self.devices, sort_keys=True, indent=4))
        return True

    def register_eventstream(self):
        if not self.eventstream_is_connected:
            self.eventstream_thread = thread.start_new_thread(self.eventstream, ())

    def eventstream(self):
        # type: () -> None
        self.eventstream_is_connected = True
        self.log_msg("Entering eventstream.")

        while True:
            self.log_msg("Connecting to eventstream.")
            while not self.bridge_ip:
                self.log_msg("Waiting for Hue discovery to connect to eventstream.")
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
                self.log_data("Error", "In eventstream, " + str(e))
                self.log_msg("In eventstream, disconnecting due to " + str(e))
                sock.close()
                time.sleep(5)
                continue

            while True:
                # todo check / handle "normal" disconnects
                try:
                    if self.eventstream_stop:
                        sock.close()
                        self.log_msg("Stopping eventstream on request")
                        self.eventstream_is_connected = False
                        return

                    data = sock.recv(1024)
                    if "data: " not in data:
                        continue

                    data = data[data.find("data: ") + 6:]
                    #data = str(data).replace("\r", '').replace("\n", '')
                    data = json.loads(data)
                    self.process_json(data)

                except socket.error as e:
                    self.log_msg("In 'eventstream', socket error '" + str(e) + "'.")
                    continue

                except Exception as e:
                    self.log_msg("In 'eventstream', '" + str(e) + "'.")
                    continue

            # gently disconnect and wait for re-connection
            sock.close()
            self.log_msg("Disconnected from hue eventstream, waiting to reconnect.")
            time.sleep(4)

        self.log_msg("Exit eventstream. No further processing.")
        self.eventstream_is_connected = False

    def process_json(self, msg):
        # type: (json) -> None
        # eventstream: /List/ [{"data": [{"owner": {"rid": "c0c1325d-4678-482b-9d39-831687b486ce", "rtype": "device"}, "on": {"on": false}, "id_v1": "/lights/12", "id": "5e6771a6-7f28-4856-85fa-5025a42b050e", "type": "light"}], "creationtime": "2022-05-12T19:16:34Z", "id": "8fe327d3-53d3-4d2c-8175-2f4711daad4f", "type": "update"}]
        # get_data: /Dict/ {"errors": [], "data": [{"product_data": {"model_id": "LCT015", "manufacturer_name": "Signify Netherlands B.V.", "hardware_platform_type": "100b-10c", "software_version": "1.88.1", "product_archetype": "sultan_bulb", "product_name": "Hue color lamp", "certified": true}, "identify": {}, "services": [{"rid": "5c459c5c-d5d1-485b-990e-c45e8bff0b64", "rtype": "light"}, {"rid": "2c2a7201-3786-47e7-a538-31c4b6859f44", "rtype": "zigbee_connectivity"}, {"rid": "97e106a0-1480-48ef-98a4-3731ed9a635d", "rtype": "entertainment"}], "id_v1": "/lights/4", "type": "device", "id": "65fb9063-edd8-470d-8341-70400264f819", "metadata": {"archetype": "ceiling_round", "name": "Deckenleuchte Bad"}}, {"product_data": {"model_id": "LCA001", "manufacturer_name": "Signify Netherlands B.V.", "hardware_platform_type": "100b-112", "software_version": "1.53.3", "product_archetype": "sultan_bulb", "product_name": "Hue color lamp", "certified": true}, "identify": {}, "services": [{"rid": "3ed36098-061b-479c-acd5-81074954f367", "rtype": "light"}, {"rid": "2c50844b-2040-435a-810b-f68b2e3396b9", "rtype": "zigbee_connectivity"}, {"rid": "7c194f14-9f84-4514-8925-09d16d7a7a0e", "rtype": "entertainment"}], "id_v1": "/lights/13", "type": "device", "id": "84646230-4f47-4665-99fb-b84d910b5763", "metadata": {"archetype": "sultan_bulb", "name": "DG Leselampe"}}, {"product_data": {"model_id": "LOM007", "manufacturer_name": "Signify Netherlands B.V.", "hardware_platform_type": "100b-11a", "software_version": "1.93.6", "product_archetype": "plug", "product_name": "Hue smart plug", "certified": true}, "identify": {}, "services": [{"rid": "15e36641-5e81-4049-9e71-1df5060c86c8", "rtype": "light"}, {"rid": "41a5cb30-066a-42a3-aa31-e54d2362d3a7", "rtype": "zigbee_connectivity"}], "id_v1": "/lights/14", "type": "device", "id": "2f0a1e62-e078-49d6-83fb-db817aeb50ff", "metadata": {"archetype": "plug", "name": "Weihnachtsbaum"}}, {"product_data": {"model_id": "LCT015", "manufacturer_name": "Signify Netherlands B.V.", "hardware_platform_type": "100b-10c", "software_version": "1.88.1", "product_archetype": "sultan_bulb", "product_name": "Hue color lamp", "certified": true}, "identify": {}, "services": [{"rid": "ec86940a-ce69-414d-9b6c-81e50793f8c4", "rtype": "light"}, {"rid": "5c25a1dd-83f5-4b31-9d24-ec7c0392fcf2", "rtype": "zigbee_connectivity"}, {"rid": "39eb5629-bb01-461b-80b0-90e571eea072", "rtype": "entertainment"}], "id_v1": "/lights/5", "type": "device", "id": "549af4ad-9f99-49bf-8f6f-d299f3a31b1c", "metadata": {"archetype": "table_shade", "name": "Kugelleuchte"}}, {"product_data": {"model_id": "BSB002", "manufacturer_name": "Signify Netherlands B.V.", "software_version": "1.51.1951086030", "product_archetype": "bridge_v2", "product_name": "Philips hue", "certified": true}, "identify": {}, "services": [{"rid": "f54227ea-1ca1-4840-86d8-de3dab043837", "rtype": "bridge"}, {"rid": "3610a049-1025-4a11-a7e9-bcf0a02da06b", "rtype": "zigbee_connectivity"}, {"rid": "04d2d748-95d2-41aa-9cad-6af5d0fae3a7", "rtype": "entertainment"}], "id_v1": "", "type": "device", "id": "c75e9cf7-e368-4847-af14-d7b1ee99ee28", "metadata": {"archetype": "bridge_v2", "name": "Philips hue"}}, {"product_data": {"model_id": "LWB010", "manufacturer_name": "Signify Netherlands B.V.", "hardware_platform_type": "100b-10c", "software_version": "1.88.1", "product_archetype": "classic_bulb", "product_name": "Hue white lamp", "certified": true}, "identify": {}, "services": [{"rid": "67bfc31f-e4df-43f1-989e-5a58570a04e8", "rtype": "light"}, {"rid": "06d833ba-4de9-46d7-92ac-3ea11c2dd9bf", "rtype": "zigbee_connectivity"}], "id_v1": "/lights/8", "type": "device", "id": "ee53baf2-d2da-4a59-b4b3-2a6e8d97d049", "metadata": {"archetype": "classic_bulb", "name": "P1077-002"}}, {"product_data": {"model_id": "LIGHTIFY Outdoor Flex RGBW", "manufacturer_name": "OSRAM", "hardware_platform_type": "110c-5b", "software_version": "0.0.0", "product_archetype": "classic_bulb", "product_name": "Extended color light", "certified": false}, "identify": {}, "services": [{"rid": "842f7de5-c5d6-4619-92e5-1a819cb97a36", "rtype": "light"}, {"rid": "ee7566dd-936e-4289-b750-117d2f49a73c", "rtype": "zigbee_connectivity"}], "id_v1": "/lights/9", "type": "device", "id": "c4875244-fe10-422a-a839-e1a6c116c65d", "metadata": {"archetype": "hue_lightstrip", "name": "LED Stripe"}}, {"product_data": {"model_id": "LCA001", "manufacturer_name": "Signify Netherlands B.V.", "hardware_platform_type": "100b-112", "software_version": "1.93.7", "product_archetype": "sultan_bulb", "product_name": "Hue color lamp", "certified": true}, "identify": {}, "services": [{"rid": "5e6771a6-7f28-4856-85fa-5025a42b050e", "rtype": "light"}, {"rid": "a5c79f8c-0b94-40f7-a42d-25ab7b21d58e", "rtype": "zigbee_connectivity"}, {"rid": "928bf428-671e-4fdd-ab8e-3ce0f989e230", "rtype": "entertainment"}], "id_v1": "/lights/12", "type": "device", "id": "c0c1325d-4678-482b-9d39-831687b486ce", "metadata": {"archetype": "table_shade", "name": "Kugelleuchte Esszimmer P1075-007"}}, {"product_data": {"model_id": "LWB010", "manufacturer_name": "Signify Netherlands B.V.", "hardware_platform_type": "100b-10c", "software_version": "1.88.1", "product_archetype": "classic_bulb", "product_name": "Hue white lamp", "certified": true}, "identify": {}, "services": [{"rid": "ab1bbd5c-6a04-436c-9036-067ecd17959e", "rtype": "light"}, {"rid": "785d145a-a568-4c90-9c03-7eac1b347e50", "rtype": "zigbee_connectivity"}], "id_v1": "/lights/7", "type": "device", "id": "47308e2f-217e-4179-983a-e39184133144", "metadata": {"archetype": "classic_bulb", "name": "P1077-003"}}, {"product_data": {"model_id": "LWU001", "manufacturer_name": "Signify Netherlands B.V.", "hardware_platform_type": "100b-114", "software_version": "1.93.3", "product_archetype": "luster_bulb", "product_name": "Hue white lamp", "certified": true}, "identify": {}, "services": [{"rid": "3d4e6297-a8ef-4c62-aad0-9c43af7fc945", "rtype": "light"}, {"rid": "57d33cd9-e37e-4963-9349-7eee7b36172e", "rtype": "zigbee_connectivity"}], "id_v1": "/lights/11", "type": "device", "id": "36987ec2-13dd-4f5a-b82c-9681b33ea656", "metadata": {"archetype": "luster_bulb", "name": "Garten Ecke"}}, {"product_data": {"model_id": "LWU001", "manufacturer_name": "Signify Netherlands B.V.", "hardware_platform_type": "100b-114", "software_version": "1.93.3", "product_archetype": "luster_bulb", "product_name": "Hue white lamp", "certified": true}, "identify": {}, "services": [{"rid": "9a8aaf65-822b-4593-863e-4676e99bfe0f", "rtype": "light"}, {"rid": "c8de3902-b51c-4f3c-824e-4aeb9bbff667", "rtype": "zigbee_connectivity"}], "id_v1": "/lights/10", "type": "device", "id": "0846971e-d1b8-4110-8b09-3cfd54262d97", "metadata": {"archetype": "luster_bulb", "name": "Garten Terrasse"}}, {"product_data": {"model_id": "LCT015", "manufacturer_name": "Signify Netherlands B.V.", "hardware_platform_type": "100b-10c", "software_version": "1.88.1", "product_archetype": "sultan_bulb", "product_name": "Hue color lamp", "certified": true}, "identify": {}, "services": [{"rid": "fbbd07de-5bf0-4dd6-b819-db3d9ee9a429", "rtype": "light"}, {"rid": "f15ebeef-8f47-40d7-b64b-382f19f520d2", "rtype": "zigbee_connectivity"}, {"rid": "0753a25b-e481-4fa1-9176-a393161a3586", "rtype": "entertainment"}], "id_v1": "/lights/3", "type": "device", "id": "3603093d-b456-4d02-a6ab-6a23aad1f6ba", "metadata": {"archetype": "floor_shade", "name": "Leselampe"}}, {"product_data": {"model_id": "LWB010", "manufacturer_name": "Signify Netherlands B.V.", "hardware_platform_type": "100b-10c", "software_version": "1.88.1", "product_archetype": "classic_bulb", "product_name": "Hue white lamp", "certified": true}, "identify": {}, "services": [{"rid": "f6197905-f63f-40d1-a53c-0e1b5dce08c1", "rtype": "light"}, {"rid": "d9c69a6a-42c8-4ddc-a56c-64e152072b20", "rtype": "zigbee_connectivity"}], "id_v1": "/lights/6", "type": "device", "id": "90dc33a1-f26f-492a-a952-ee96d57b42cc", "metadata": {"archetype": "pendant_round", "name": "Deckenleuchte"}}]}
        out = json.dumps(msg)
        self.set_output_value_sbc(self.PIN_O_JSON, out)

        if type(msg) == dict:
            msg = [msg]

        device_ids = [self._get_input_value(self.PIN_I_ITM_IDX)]
        if device_ids[0] in self.devices:

            for type_id in self.devices[device_ids[0]]:
                curr_id = self.devices[device_ids[0]][type_id]
                if len(curr_id) > 20:  # go for ids only, not for name or type.
                    device_ids.append(curr_id)

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
                        if "on" in data:
                            is_on = bool(data["on"]["on"])
                            self.set_output_value_sbc(self.PIN_O_BSTATUSONOFF, is_on)

                        if "color" in data:
                            color = data["color"]
                            # todo calculate rgb

                        if "dimming" in data:
                            dimming = data["dimming"]
                            self.set_output_value_sbc(self.PIN_O_BRI, int(dimming["brightness"]))

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

        rid = str(self._get_input_value(self.PIN_I_ITM_IDX))
        if not rid:
            self.log_msg("In set_on, rid for type 'light' not found.")
            return False

        if rid not in self.devices:
            self.log_msg("In set_on, rid not registered.")
            return False

        if "light" not in self.devices[rid]:
            self.log_msg("In set_on, type 'light' not registered for " + rid + ".")
            return False

        if set_on:
            payload = '{"on":{"on":true}}'
        else:
            payload = '{"on":{"on":false}}'

        ret = self.http_put(self.devices[rid]["light"], "light", payload)
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
        ret = self.http_put(rid, "light", payload)
        return ret["status"] == 200

    # def set_scene(self, scene):
    #     payload = '{"scene":"' + scene + '"}'
    #     ret = self.http_put(payload, scene)
    #     return "success" in ret["data"]
    #
    # def set_effect(self, effect):
    #     payload = '{"effect":"'
    #
    #     if effect:
    #         payload = payload + 'colorloop"}'
    #     else:
    #         payload = payload + 'none"}'
    #
    #     rid = self.get_rig("light")
    #     ret = self.http_put(payload, rid)
    #     return "success" in ret["data"]
    #
    # def set_alert(self, alert):
    #     payload = ""
    #     if alert:
    #         payload = '{"alert":"lselect"}'
    #     else:
    #         payload = '{"alert":"none"}'
    #
    #     rid = self.get_rig("light")
    #     ret = self.http_put(payload, rid)
    #     return "success" in ret["data"]
    #
    # def set_hue_color(self, hue_col):
    #     payload = '{"hue":' + str(hue_col) + '}'
    #     rid = self.get_rig("light")
    #     ret = self.http_put(payload, rid)
    #     return "success" in ret["data"]
    #
    # def set_sat(self, sat):
    #     payload = '{"sat":' + str(sat) + '}'
    #     rid = self.get_rig("light")
    #     ret = self.http_put(payload, rid)
    #     return "success" in ret["data"]
    #
    # def set_ct(self, ct):
    #     payload = '{"ct":' + str(ct) + '}'
    #     rid = self.get_rig("light")
    #     ret = self.http_put(payload, rid)
    #     return "success" in ret["data"]
    #
    # def prep_dim(self, val):
    #     self.DEBUG.set_value("Dim cmd", str(val) + " " + str(type(val)))
    #
    #     if (type(val) is float) or (type(val) is int):
    #         val = int(val)
    #         val = chr(val)
    #         val = bytearray(val)
    #
    #     if val[-1] == 0x00:
    #         self.stop = True
    #         self.timer = threading.Timer(1000, None)
    #         print("abort")
    #         return
    #
    #     sgn_bte = int((val[-1] & 0x08) >> 3)
    #     val = int(val[-1] & 0x07)
    #
    #     self.interval = round(255.0 / pow(2, val - 1), 0)
    #
    #     if sgn_bte == 1:
    #         pass
    #     else:
    #         self.interval = int(-1 * self.interval)
    #
    #     self.stop = False
    #     self.do_dim()
    #
    # def do_dim(self):
    #     if self.stop:
    #         return
    #
    #     new_bri = int(self.curr_bri + self.interval)
    #     if new_bri > 255:
    #         new_bri = 255
    #     elif new_bri < 1:
    #         new_bri = 1
    #
    #     self.set_bri(new_bri)
    #
    #     duration = float(self._get_input_value(self.PIN_I_NDIMRAMP))
    #     steps = 255 / abs(self.interval)
    #     step = float(round(duration / steps, 4))
    #
    #     self.timer = threading.Timer(step, self.do_dim)
    #     self.timer.start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.g_out_sbc = {}  # type: {int, object}
        self.debug = False  # type: bool
        self.eventstream_thread = 0  # type: int

        if str(self._get_input_value(self.PIN_I_SHUEIP)):
            self.bridge_ip = str(self._get_input_value(self.PIN_I_SHUEIP))
            self.log_msg("Bridge IP (manual) is " + self.bridge_ip)

        self.eventstream_stop = False  # type: bool
        self.devices = {}  # type: {str: {str: str}}

        self.discover_hue()
        self.register_devices()
        self.register_eventstream()

    def on_input_value(self, index, value):

        # Process State
        itm_idx = str(self._get_input_value(self.PIN_I_ITM_IDX))
        hue_state = {"data": str(self._get_input_value(self.PIN_I_STAT_JSON)), "status": 200}
#        hue_ol = int(self._get_input_value(self.PIN_I_NHUE))
#        sat = int(self._get_input_value(self.PIN_I_NSAT) / 100.0 * 255.0)
#        ct = int(self._get_input_value(self.PIN_I_NCT))

        if self._get_input_value(self.PIN_I_HUE_KEY) == "":
            self.log_msg("Hue key not set. Abort processing.")
            return

        # If trigger == 1, get data via web request
        if (self.PIN_I_BTRIGGER == index) and (bool(value)):
            item_types = {"device", "light", "room", "scene", "zone", "grouped_light"}

            for item_type in item_types:
                self.get_data(item_type)

        if self.PIN_I_STAT_JSON == index:
            # todo implement
            if hue_state["data"]:
                if itm_idx:
                    self.process_json(hue_state["data"])
                    self.set_output_value_sbc(self.PIN_O_JSON, hue_state["data"])

        # Process set commands
        if self.PIN_I_BONOFF == index:
            self.set_on(bool(value))

        elif self.PIN_I_BRI == index:
            self.set_on(True)
            self.set_dimming(int(value))

        # # todo set scene
        # elif self.PIN_I_SSCENE == index:
        #     res = self.set_scene(value)
        #     if res:
        #         self.set_output_value_sbc(self.PIN_O_BSTATUSONOFF, True)
        #
        # # todo set hue
        # elif self.PIN_I_NHUE == index:
        #     self.set_on(True)
        #     res = self.set_hue_color(hue_ol)
        #     if res:
        #         self.set_output_value_sbc(self.PIN_O_NHUE, hue_ol)
        #
        # # todo set sat
        # elif self.PIN_I_NSAT == index:
        #     self.set_on(True)
        #     res = self.set_sat(sat)
        #     if res:
        #         self.set_output_value_sbc(self.PIN_O_NSAT, sat / 255.0 * 100)
        #
        # # todo set nct
        # elif self.PIN_I_NCT == index:
        #     self.set_on(True)
        #     res = self.set_ct(ct)
        #     if res:
        #         self.set_output_value_sbc(self.PIN_O_NCT, ct)
        #
        # # todo set rgb
        # elif ((self.PIN_I_NR == index) or
        #       (self.PIN_I_NG == index) or
        #       (self.PIN_I_NB == index)):
        #     self.set_on(True)
        #
        #     red = int(int(self._get_input_value(self.PIN_I_NR)) * 2.55)
        #     green = int(int(self._get_input_value(self.PIN_I_NG)) * 2.55)
        #     blue = int(int(self._get_input_value(self.PIN_I_NB)) * 2.55)
        #     # h, s, v = self.rgb2hsv(r, g, b)
        #     h, s, v = colorsys.rgb_to_hsv(r=(red / 255.0), g=(green / 255.0), b=(blue / 255.0))
        #     h = int(360.0 * 182.04 * h)
        #     s = int(s * 255)
        #     v = int(v * 255)
        #
        #     ret1 = self.set_bri(v)
        #     ret2 = self.set_hue_color(h)
        #     ret3 = self.set_sat(s)
        #
        #     if ret1 and ret2 and ret3:
        #         # set rgb as output
        #         self.set_output_value_sbc(self.PIN_O_NR, red)
        #         self.set_output_value_sbc(self.PIN_O_NG, green)
        #         self.set_output_value_sbc(self.PIN_O_NB, blue)
        #
        # # todo set alert
        # elif self.PIN_I_BALERT == index:
        #     alert = int(self._get_input_value(self.PIN_I_BALERT))
        #     self.set_alert(alert)
        #     ###
        #
        # # todo set effect
        # elif self.PIN_I_NEFFECT == index:
        #     effect = int(self._get_input_value(self.PIN_I_NEFFECT))
        #     self.set_effect(effect)
        #
        # # todo do relative dim
        # elif self.PIN_I_NRELDIM == index:
        #     self.prep_dim(value)


############################################


class UnitTests(unittest.TestCase):

    def setUp(self):
        print("\n### setUp")
        with open("credentials.txt") as f:
            self.cred = json.load(f)

        self.dummy = HueGroup_14100_14100(0)

        self.dummy.debug_input_value[self.dummy.PIN_I_HUE_KEY] = self.cred["PIN_I_SUSER"]
        self.dummy.debug_input_value[self.dummy.PIN_I_ITM_IDX] = self.cred["hue_device_id"]
        self.dummy.debug_rid = self.cred["hue_light_id"]

        self.dummy.eventstream_stop = True
        self.dummy.on_init()

    def tearDown(self):
        print("\n### tearDown")

    def test_get_rig(self):
        print("\n### test_get_rig")
        ret = self.dummy.get_rig("light")
        self.assertEqual(ret, self.dummy.debug_rid)
        ret = self.dummy.get_rig("dummy")
        self.assertEqual(ret, str())

    # def test_08_print_devices(self):
    #     print("\n### ###test_08_print_devices")
    #     res = self.dummy.register_devices()
    #     self.assertTrue(res)
    #
    # def test_09_singleton_eventstream(self):
    #     print("test_09_singleton_eventstream")
    #     self.assertTrue(False, "Test not implemented")
    #
    # def test_10_eventstream_reconnect(self):
    #     print("\n### test_10_eventstream_reconnect")
    #     self.assertTrue(False, "Test not implemented")

    def test_11_discover(self):
        print("\n###test_11_discover")
        self.dummy.bridge_ip = None
        self.dummy.discover_hue()
        self.assertTrue("192" in self.dummy.bridge_ip)

        self.dummy.bridge_ip = None

    def test_12_set_on(self):
        print("\n### test_12_set_on")
        self.assertTrue(self.dummy.set_on(False))
        time.sleep(2)

        self.dummy.debug_output_value[self.dummy.PIN_O_BSTATUSONOFF] = False
        self.dummy.on_input_value(self.dummy.PIN_I_BONOFF, True)
        time.sleep(2)

        self.dummy.stop_eventstream = True
        self.assertTrue(self.dummy.debug_output_value[self.dummy.PIN_O_BSTATUSONOFF])

    # def test_13_on_off_group(self):
    #     print("\n### test_13_on_off_group")
    #     self.assertTrue(False, "Test not implemented")
    #
    # def test_14_on_off_zone(self):
    #     print("\n### test_14_on_off_zone")
    #     self.assertTrue(False, "Test not implemented")
    #
    # def test_15_on_off_room(self):
    #     print("\n### test_15_on_off_room")
    #     self.assertTrue(False, "Test not implemented")

    def test_16_eventstream_on_off(self):
        print("\n### test_16_eventstream_on_off")
        self.dummy.eventstream_stop = False
        self.dummy.register_eventstream()
        self.dummy.on_input_value(self.dummy.PIN_I_BONOFF, False)
        time.sleep(3)
        self.dummy.on_input_value(self.dummy.PIN_I_BONOFF, True)
        time.sleep(3)
        self.dummy.stop_eventstream = True
        self.assertTrue(self.dummy.debug_output_value[self.dummy.PIN_O_BSTATUSONOFF])

    def test_17_dimming(self):
        print("\n### test_17_dimming")

        self.dummy.eventstream_stop = False
        time.sleep(2)
        print("------ On")
        self.dummy.set_on(True)
        time.sleep(2)
        print("------ 70%")
        res = self.dummy.set_dimming(70)
        self.assertTrue(res)
        time.sleep(2)
        print("------ 30%")
        self.dummy.on_input_value(self.dummy.PIN_I_BRI, 30)
        time.sleep(2)
        res = abs(30 - float(self.dummy.debug_output_value[self.dummy.PIN_O_BRI]))
        self.assertTrue( res <= 1, res)
        print("------ off")
        self.dummy.eventstream_stop = True
        self.dummy.set_on(False)
        time.sleep(2)

    def test_18_get_data(self):
        print("\n### test_get_data")
        self.dummy.eventstream_stop = True
        self.dummy.debug_output_value[self.dummy.PIN_O_BSTATUSONOFF] = None
        self.dummy.g_out_sbc = {}

        self.dummy.on_input_value(self.dummy.PIN_I_BTRIGGER, 1)
        res = self.dummy.debug_output_value[self.dummy.PIN_O_BSTATUSONOFF]

        self.assertTrue(bool == type(res))

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
