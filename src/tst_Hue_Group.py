# coding: utf8


import unittest
import time

# import httplib
import json
import colorsys
import threading


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
        self.PIN_I_SGROUPSTATJSON = 1
        self.PIN_I_SLIGHTSSTATJSON = 2
        self.PIN_I_BTRIGGER = 3
        self.PIN_I_SHUEIP = 4
        self.PIN_I_NHUEPORT = 5
        self.PIN_I_SUSER = 6
        self.PIN_I_NGROUP = 7
        self.PIN_I_NLIGHT = 8
        self.PIN_I_BONOFF = 9
        self.PIN_I_NBRI = 10
        self.PIN_I_NHUE = 11
        self.PIN_I_NSAT = 12
        self.PIN_I_NCT = 13
        self.PIN_I_NR = 14
        self.PIN_I_NG = 15
        self.PIN_I_NB = 16
        self.PIN_I_SSCENE = 17
        self.PIN_I_NTRANSTIME = 18
        self.PIN_I_BALERT = 19
        self.PIN_I_NEFFECT = 20
        self.PIN_I_NRELDIM = 21
        self.PIN_I_NDIMRAMP = 22
        self.PIN_O_BSTATUSONOFF = 1
        self.PIN_O_NBRI = 2
        self.PIN_O_NHUE = 3
        self.PIN_O_NSAT = 4
        self.PIN_O_NCT = 5
        self.PIN_O_NR = 6
        self.PIN_O_NG = 7
        self.PIN_O_NB = 8
        self.PIN_O_NREACHABLE = 9
        self.PIN_O_NGRPJSON = 10
        self.PIN_O_NLGHTSJSON = 11

    ########################################################################################################
    #### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
    ###################################################################################################!!!##

    g_debug = False
    g_currBri = 0
    g_intervall = 0
    g_timer = threading.Timer(1000, None)
    g_stopp = False

    # get general web request
    def get_data(self, api_url, api_port, api_user, api_cmd):
        api_path = '/api/' + api_user + '/' + api_cmd
        data = ""

        try:
            http_client = httplib.HTTPConnection(api_url, int(api_port), timeout=5)
            if not self.g_debug:
                http_client.request("GET", api_path)
                response = http_client.getresponse()
                status = response.status
                data = {'data': response.read(), 'status': status}
            else:
                data = {'data': "debug", 'status': 200}
            self.DEBUG.add_message("14100: Hue bridge response code: " + str(status))
        except Exception as e:
            self.DEBUG.add_message(str(e))
            return
        finally:
            if http_client:
                http_client.close()

        return data

    # read light data from json
    def read_lights_json(self, json_state, light):
        try:
            json_state = json.loads(json_state)

            if str(light) in json_state:
                if 'state' in json_state[str(light)]:
                    if 'reachable' in json_state[str(light)]['state']:
                        reachable = json_state[str(light)]['state']['reachable']
                        self._set_output_value(self.PIN_O_NREACHABLE, reachable)
        except:
            json_state = []

        return json.dumps(json_state)

    def read_groups_json(self, json_state, group):
        try:
            json_state = json.loads(json_state)

            if str(group) in json_state:
                if 'action' in json_state[str(group)]:
                    action_sub = json_state[str(group)]["action"]
                    on_off = action_sub['on']
                    self._set_output_value(self.PIN_O_BSTATUSONOFF, on_off)

                    if 'bri' in action_sub:
                        bri = int(action_sub['bri'])
                        self.g_currBri = bri
                        self._set_output_value(self.PIN_O_NBRI, bri / 255.0 * 100.0)
                    if 'hue' in action_sub:
                        hue = action_sub['hue']
                        self._set_output_value(self.PIN_O_NHUE, hue)
                    if 'sat' in action_sub:
                        sat = action_sub['sat']
                        self._set_output_value(self.PIN_O_NSAT, sat / 255.0 * 100)
                    if 'ct' in action_sub:
                        ct = action_sub['ct']
                        self._set_output_value(self.PIN_O_NCT, ct)

                    r, g, b = colorsys.hsv_to_rgb(hue / 360.0 / 182.04, sat / 255.0, bri / 255.0)

                    r = int(r * 100.0)
                    g = int(g * 100.0)
                    b = int(b * 100.0)

                    self._set_output_value(self.PIN_O_NR, r)
                    self._set_output_value(self.PIN_O_NG, g)
                    self._set_output_value(self.PIN_O_NB, b)
        except:
            json_state = []

        return json.dumps(json_state)

    def http_put(self, api_url, api_port, api_user, group, payload):
        http_client = None
        data = {'data': "", 'status': -1}
        try:
            trans_time = int(self._get_input_value(self.PIN_I_NTRANSTIME))
            if (trans_time > 0):
                payload = payload[:-1]
                payload = payload + ',"transitiontime":' + str(trans_time) + '}'

            api_path = '/api/' + api_user + '/groups/' + str(group) + '/action'
            headers = {"HOST": str(api_url + ":" + str(api_port)), "CONTENT-LENGTH": str(len(payload)),
                       "Content-type": 'application/json'}
            # headers = { "Content-type": 'application/json' }

            if not self.g_debug:
                http_client = httplib.HTTPConnection(api_url, int(api_port), timeout=5)

                http_client.request("PUT", api_path, payload, headers)
                response = http_client.getresponse()
                status = response.status
                data = {'data': response.read(), 'status': status}
            else:
                data = {'data': '{"success" : True}', 'status': 200}
            return data
        # except Exception as e:
        except:
            return data
        finally:
            if http_client:
                http_client.close()

    def hue_on_off(self, api_url, api_port, api_user, group, bSetOn):
        payload = ""
        if bSetOn:
            payload = '{"on":true}'
        else:
            payload = '{"on":false}'

        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_scene(self, api_url, api_port, api_user, group, sScene):
        payload = '{"scene":"' + sScene + '"}'
        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_effect(self, api_url, api_port, api_user, group, nEffect):
        payload = '{"effect":"'

        if nEffect:
            payload = payload + 'colorloop"}'
        else:
            payload = payload + 'none"}'

        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_alert(self, api_url, api_port, api_user, group, bAlert):
        payload = ""
        if bAlert:
            payload = '{"alert":"lselect"}'
        else:
            payload = '{"alert":"none"}'

        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_bri(self, api_url, api_port, api_user, group, nBri):
        if nBri > 0:
            self.hue_on_off(api_url, api_port, api_user, group, True)
        payload = '{"bri":' + str(nBri) + '}'
        ret = self.http_put(api_url, api_port, api_user, group, payload)
        if "success" in ret["data"]:
            self.g_currBri = nBri
        return "success" in ret["data"]

    def set_hue_color(self, api_url, api_port, api_user, group, nHueCol):
        payload = '{"hue":' + str(nHueCol) + '}'
        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_sat(self, api_url, api_port, api_user, group, nSat):
        payload = '{"sat":' + str(nSat) + '}'
        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_ct(self, api_url, api_port, api_user, group, nCt):
        payload = '{"ct":' + str(nCt) + '}'
        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def prep_dim(self, val):
        self.DEBUG.set_value("Dim cmd", str(val) + " " + str(type(val)))

        if (type(val) is float) or (type(val) is int):
            val = int(val)
            val = chr(val)
            val = bytearray(val)

        if val[-1] == 0x00:
            self.g_stopp = True
            self.g_timer = threading.Timer(1000, None)
            print("abort")
            return

        sgn_bte = int((val[-1] & 0x08) >> 3)
        val = int(val[-1] & 0x07)

        self.g_intervall = round(255.0 / pow(2, val - 1), 0)

        if sgn_bte == 1:
            pass
        else:
            self.g_intervall = int(-1 * self.g_intervall)

        self.g_stopp = False
        self.do_dim()

    def do_dim(self):
        if (self.g_stopp == True):
            return

        api_url = str(self._get_input_value(self.PIN_I_SHUEIP))
        api_port = int(self._get_input_value(self.PIN_I_NHUEPORT))
        api_user = str(self._get_input_value(self.PIN_I_SUSER))
        group = int(self._get_input_value(self.PIN_I_NGROUP))

        new_bri = int(self.g_currBri + self.g_intervall)
        if new_bri > 255:
            new_bri = 255
        elif new_bri < 1:
            new_bri = 1

        self.set_bri(api_url, api_port, api_user, group, new_bri)

        duration = float(self._get_input_value(self.PIN_I_NDIMRAMP))
        steps = 255 / abs(self.g_intervall)
        step = float(round(duration / steps, 4))

        self.g_timer = threading.Timer(step, self.do_dim)
        self.g_timer.start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

    def on_input_value(self, index, value):
        res = False

        # Process State
        api_url = str(self._get_input_value(self.PIN_I_SHUEIP))
        api_port = int(self._get_input_value(self.PIN_I_NHUEPORT))
        api_user = str(self._get_input_value(self.PIN_I_SUSER))
        group = int(self._get_input_value(self.PIN_I_NGROUP))
        light = int(self._get_input_value(self.PIN_I_NLIGHT))
        hue_group_state = {"data": str(self._get_input_value(self.PIN_I_SGROUPSTATJSON)), "status": 200}
        hue_light_state = {"data": str(self._get_input_value(self.PIN_I_SLIGHTSSTATJSON)), "status": 200}
        bri = int(self._get_input_value(self.PIN_I_NBRI) / 100.0 * 255.0)
        hue_ol = int(self._get_input_value(self.PIN_I_NHUE))
        sat = int(self._get_input_value(self.PIN_I_NSAT) / 100.0 * 255.0)
        ct = int(self._get_input_value(self.PIN_I_NCT))

        # If trigger == 1, get data via web request
        if (self.PIN_I_BTRIGGER == index) and (bool(value)):
            hue_group_state = self.get_data(api_url, api_port, api_user, "groups")
            hue_light_state = self.get_data(api_url, api_port, api_user, "lights")

        if ((self.PIN_I_BTRIGGER == index) or
                (self.PIN_I_SGROUPSTATJSON == index)):
            if hue_group_state["data"]:
                if group > 0:
                    self.read_groups_json(hue_group_state["data"], group)
                    self._set_output_value(self.PIN_O_NGRPJSON, hue_group_state["data"])

        if ((self.PIN_I_BTRIGGER == index) or
                (self.PIN_I_SLIGHTSSTATJSON == index)):
            if hue_light_state["data"]:
                if light > 0:
                    self.read_lights_json(hue_light_state["data"], light)
                    self._set_output_value(self.PIN_O_NLGHTSJSON, hue_light_state["data"])

        # Process set commands
        if (self._get_input_value(self.PIN_I_SUSER) == "") or (self._get_input_value(self.PIN_I_SHUEIP) == ""):
            return

        if self.PIN_I_BONOFF == index:
            res = self.hue_on_off(api_url, api_port, api_user, group, value)
            if res:
                self._set_output_value(self.PIN_O_BSTATUSONOFF, value)

        elif self.PIN_I_SSCENE == index:
            res = self.set_scene(api_url, api_port, api_user, group, value)
            if res:
                self._set_output_value(self.PIN_O_BSTATUSONOFF, True)

        elif self.PIN_I_NBRI == index:
            self.hue_on_off(api_url, api_port, api_user, group, True)
            res = self.set_bri(api_url, api_port, api_user, group, bri)
            print(res)
            if res:
                self._set_output_value(self.PIN_O_NBRI, bri / 255.0 * 100.0)

        elif self.PIN_I_NHUE == index:
            self.hue_on_off(api_url, api_port, api_user, group, True)
            res = self.set_hue_color(api_url, api_port, api_user, group, hue_ol)
            if res:
                self._set_output_value(self.PIN_O_NHUE, hue_ol)

        elif self.PIN_I_NSAT == index:
            self.hue_on_off(api_url, api_port, api_user, group, True)
            res = self.set_sat(api_url, api_port, api_user, group, sat)
            if res:
                self._set_output_value(self.PIN_O_NSAT, sat / 255.0 * 100)

        elif self.PIN_I_NCT == index:
            self.hue_on_off(api_url, api_port, api_user, group, True)
            res = self.set_ct(api_url, api_port, api_user, group, ct)
            if res:
                self._set_output_value(self.PIN_O_NCT, ct)

        elif ((self.PIN_I_NR == index) or
              (self.PIN_I_NG == index) or
              (self.PIN_I_NB == index)):
            self.hue_on_off(api_url, api_port, api_user, group, True)

            red = int(int(self._get_input_value(self.PIN_I_NR)) * 2.55)
            green = int(int(self._get_input_value(self.PIN_I_NG)) * 2.55)
            blue = int(int(self._get_input_value(self.PIN_I_NB)) * 2.55)
            # h, s, v = self.rgb2hsv(r, g, b)
            h, s, v = colorsys.rgb_to_hsv(r=(red / 255.0), g=(green / 255.0), b=(blue / 255.0))
            h = int(360.0 * 182.04 * h)
            s = int(s * 255)
            v = int(v * 255)

            ret1 = self.set_bri(api_url, api_port, api_user, group, v)
            ret2 = self.set_hue_color(api_url, api_port, api_user, group, h)
            ret3 = self.set_sat(api_url, api_port, api_user, group, s)

            if ret1 and ret2 and ret3:
                # set rgb as output
                self._set_output_value(self.PIN_O_NR, red)
                self._set_output_value(self.PIN_O_NG, green)
                self._set_output_value(self.PIN_O_NB, blue)

        elif self.PIN_I_BALERT == index:
            alert = int(self._get_input_value(self.PIN_I_BALERT))
            self.set_alert(api_url, api_port, api_user, group, alert)
            ###

        elif self.PIN_I_NEFFECT == index:
            effect = int(self._get_input_value(self.PIN_I_NEFFECT))
            self.set_effect(api_url, api_port, api_user, group, effect)

        elif self.PIN_I_NRELDIM == index:
            self.prep_dim(value)


############################################


class UnitTests(unittest.TestCase):

    def setUp(self):
        self.dummy = HueGroup_14100_14100(0)
        self.dummy.on_init()

    def tearDown(selfself):
        pass

    def test_setBri(self):
        self.dummy.g_debug = True

        api_url = "192.168.0.10"
        api_port = "80"
        api_user = "debug"
        group = "1"
        light = 3

        ret = self.dummy.set_bri(api_url, api_port, api_user, group, 100)
        self.assertTrue(ret)
        self.assertEqual(self.dummy.g_currBri, 100)

    def test_readGroupsJson(self):
        self.dummy.g_debug = True
        self.dummy.g_currBri = 204

        api_url = "192.168.0.10"
        api_port = "80"
        api_user = "debug"
        group = "1"
        light = 3

        retGroups = {
            "data": '{"1": {"name": "Wohnzimmer", "lights": ["3", "5"], "state": {"any_on": true, "all_on": true}, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "none", "xy": [0.4779, 0.3823], "bri": 204, "ct": 399, "sat": 121}, "recycle": false, "sensors": [], "type": "Room", "class": "Living room"}, "3": {"name": "Thilo", "lights": [], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "alert": "none"}, "recycle": false, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "2": {"name": "Bad OG", "lights": ["4"], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "hue": 8402, "colormode": "xy", "effect": "none", "alert": "select", "xy": [0.4575, 0.4099], "bri": 254, "ct": 366, "sat": 140}, "recycle": false, "sensors": [], "type": "Room", "class": "Bathroom"}, "5": {"name": "Nora", "lights": ["7", "8"], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "bri": 1, "alert": "select"}, "recycle": false, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "4": {"name": "Flur DG", "lights": ["6"], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "bri": 254, "alert": "select"}, "recycle": false, "sensors": [], "type": "Room", "class": "Hallway"}, "7": {"name": "TV", "lights": ["3"], "state": {"any_on": true, "all_on": true}, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "select", "xy": [0.4779, 0.3823], "bri": 204, "ct": 399, "sat": 121}, "recycle": false, "sensors": [], "type": "Zone", "class": "Downstairs"}, "6": {"name": "Garage", "lights": ["9"], "state": {"any_on": true, "all_on": true}, "action": {"on": true, "hue": 0, "colormode": "ct", "effect": "none", "alert": "select", "xy": [0.3805, 0.3769], "bri": 254, "ct": 370, "sat": 0}, "recycle": false, "sensors": [], "type": "Room", "class": "Carport"}}'}
        # retLights = dummy.getData(api_url, api_port, api_user, "lights")
        ret = self.dummy.read_groups_json(retGroups["data"], 1)
        res = '{"1": {"name": "Wohnzimmer", "lights": ["3", "5"], "state": {"any_on": true, "all_on": true}, "recycle": false, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "none", "xy": [0.4779, 0.3823], "bri": 204, "sat": 121, "ct": 399}, "sensors": [], "type": "Room", "class": "Living room"}, "3": {"name": "Thilo", "lights": [], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "alert": "none"}, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "2": {"name": "Bad OG", "lights": ["4"], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "hue": 8402, "colormode": "xy", "effect": "none", "alert": "select", "xy": [0.4575, 0.4099], "bri": 254, "sat": 140, "ct": 366}, "sensors": [], "type": "Room", "class": "Bathroom"}, "5": {"name": "Nora", "lights": ["7", "8"], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "bri": 1, "alert": "select"}, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "4": {"name": "Flur DG", "lights": ["6"], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "bri": 254, "alert": "select"}, "sensors": [], "type": "Room", "class": "Hallway"}, "7": {"name": "TV", "lights": ["3"], "state": {"any_on": true, "all_on": true}, "recycle": false, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "select", "xy": [0.4779, 0.3823], "bri": 204, "sat": 121, "ct": 399}, "sensors": [], "type": "Zone", "class": "Downstairs"}, "6": {"name": "Garage", "lights": ["9"], "state": {"any_on": true, "all_on": true}, "recycle": false, "action": {"on": true, "hue": 0, "colormode": "ct", "effect": "none", "alert": "select", "xy": [0.3805, 0.3769], "bri": 254, "sat": 0, "ct": 370}, "sensors": [], "type": "Room", "class": "Carport"}}'
        self.assertEqual(ret, res)
        # ret = dummy.readLightsJson(retLights["data"], light)

        # sScene = "mYJ1jB9LmBAG6yN"
        # sScene = "qhfcIHIJ9JuYK19"
        # nHueCol = 24381

    def test_dim(self):
        self.dummy.g_debug = True
        self.dummy.g_currBri = 255

        api_url = "192.168.0.10"
        api_port = "80"
        api_user = "debug"
        group = "1"
        light = 3

        self.dummy.prep_dim(0x85)
        self.assertEqual(-16, self.dummy.g_intervall)
        self.assertEqual(10, self.dummy.g_timer.interval)
        time.sleep(3)
        self.dummy.prep_dim(0.0)
        # self.assertEqual(dummy.g_timer.interval, 1000)
        # self.assertFalse(dummy.g_timer.is_alive())

        self.dummy.prep_dim(0x8d)
        self.assertEqual(16, self.dummy.g_intervall)
        self.assertEqual(10, self.dummy.g_timer.interval)
        time.sleep(3)
        self.dummy.prep_dim(0.0)
        # self.assertEqual(dummy.g_timer.interval, 1000)
        # self.assertFalse(dummy.g_timer.is_alive())


if __name__ == '__main__':
    unittest.main()
