# coding: utf8


import unittest
import time

import httplib
import json
import colorsys
import threading


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class HueGroup_14100_14100():

    def _set_output_value(self, pin, value):
        print("### Out \tPin " + str(pin) + ", Value: " + str(value))

        if (pin == self.PIN_O_NBRI):
            self.g_currBri = value

        return ("### Out \tPin " + str(pin) + ", Value: " + str(value))

    def _get_input_value(self, pin):
        if (pin == self.PIN_I_NTRANSTIME):
            return 0
        elif (pin == self.PIN_I_NDIMRAMP):
            return 10
        elif (pin == self.PIN_I_SHUEIP):
            return "192.168.143.16"
        elif (pin == self.PIN_I_NHUEPORT):
            return "80"
        elif (pin == self.PIN_I_SUSER):
            return "yzOkvX6Of2JjUeZCRXDCqAJXYJzmofgilCi1d5Ti"
        elif (pin == self.PIN_I_NGROUP):
            return "1"
        elif (pin == self.PIN_I_NLIGHT):
            return 3
        elif (pin == self.PIN_I_NBRI):
            return 250
        else:
            return "0"

    ################################################
    class DebugHelper():
        def set_value(self, p_sCap, p_sText):
            print ("DEBUG value\t" + str(p_sCap) + ": " + str(p_sText))

        def add_message(self, p_sMsg):
            print ("Debug Msg\t" + str(p_sMsg))

    DEBUG = DebugHelper()

    class FrameworkHelper():
        def get_homeserver_private_ip(self):
            return "192.168.143.30"

        def create_debug_section(self):
            pass

    FRAMEWORK = FrameworkHelper()

    ############################################

    # def __init__(self, homeserver_context):
    # hsl20_3.BaseModule.__init__(self, homeserver_context, "hsl20_3_Hue")
    # self.FRAMEWORK = self._get_framework()
    # self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
    PIN_I_SGROUPSTATJSON = 1
    PIN_I_SLIGHTSSTATJSON = 2
    PIN_I_BTRIGGER = 3
    PIN_I_SHUEIP = 4
    PIN_I_NHUEPORT = 5
    PIN_I_SUSER = 6
    PIN_I_NGROUP = 7
    PIN_I_NLIGHT = 8
    PIN_I_BONOFF = 9
    PIN_I_NBRI = 10
    PIN_I_NHUE = 11
    PIN_I_NSAT = 12
    PIN_I_NCT = 13
    PIN_I_NR = 14
    PIN_I_NG = 15
    PIN_I_NB = 16
    PIN_I_SSCENE = 17
    PIN_I_NTRANSTIME = 18
    PIN_I_BALERT = 19
    PIN_I_NEFFECT = 20
    PIN_I_NRELDIM = 21
    PIN_I_NDIMRAMP = 22
    PIN_O_BSTATUSONOFF = 1
    PIN_O_NBRI = 2
    PIN_O_NHUE = 3
    PIN_O_NSAT = 4
    PIN_O_NCT = 5
    PIN_O_NR = 6
    PIN_O_NG = 7
    PIN_O_NB = 8
    PIN_O_NREACHABLE = 9
    PIN_O_NGRPJSON = 10
    PIN_O_NLGHTSJSON = 11
    # FRAMEWORK._run_in_context_thread(on_init)

    ########################################################################################################
    #### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
    ###################################################################################################!!!##

    g_debug = False
    g_currBri = 0
    g_curr_on = False
    g_interval = 0
    g_timer = threading.Timer(1000, None)
    g_stop = False
    g_sbc = {}

    def set_output_value_sbc(self, pin, value):
        if pin in self.g_sbc.keys():
            if self.g_sbc[pin] != value:
                self._set_output_value(pin, value)

        self.g_sbc.update({pin: value})

    # get general web request
    def get_data(self, api_url, api_port, api_user, api_cmd):
        api_path = '/api/' + api_user + '/' + api_cmd
        data = ""

        try:
            httpclient = httplib.HTTPConnection(api_url, int(api_port), timeout=5)
            if not self.g_debug:
                httpclient.request("GET", api_path)
                response = httpclient.getresponse()
                status = response.status
                data = {'data': response.read(), 'status': status}
            else:
                data = {'data': "debug", 'status': 200}
            self.DEBUG.add_message("14100: Hue bridge response code: " + str(status))
        except Exception as e:
            self.DEBUG.add_message(str(e))
            return
        finally:
            if httpclient:
                httpclient.close()

        return data

    # read light data from json
    def read_lights_json(self, json_state, light):
        try:
            json_state = json.loads(json_state)

            if str(light) in json_state:
                if 'state' in json_state[str(light)]:
                    if 'reachable' in json_state[str(light)]['state']:
                        bReachable = json_state[str(light)]['state']['reachable']
                        self._set_output_value(self.PIN_O_NREACHABLE, bReachable)
        except:
            json_state = []

        return json.dumps(json_state)

    def readGroupsJson(self, jsonState, group):
        try:
            jsonState = json.loads(jsonState)

            if str(group) in jsonState:
                if 'action' in jsonState[str(group)]:
                    actionSub = jsonState[str(group)]["action"]
                    bOnOff = actionSub['on']
                    self.g_curr_on = bOnOff
                    self._set_output_value(self.PIN_O_BSTATUSONOFF, bOnOff)

                    if 'bri' in actionSub:
                        nBri = int(actionSub['bri'])
                        self.g_currBri = nBri
                        self._set_output_value(self.PIN_O_NBRI, nBri / 255.0 * 100.0)
                    if 'hue' in actionSub:
                        nHue = actionSub['hue']
                        self._set_output_value(self.PIN_O_NHUE, nHue)
                    if 'sat' in actionSub:
                        nSat = actionSub['sat']
                        self._set_output_value(self.PIN_O_NSAT, nSat / 255.0 * 100)
                    if 'ct' in actionSub:
                        nCt = actionSub['ct']
                        self._set_output_value(self.PIN_O_NCT, nCt)

                    r, g, b = colorsys.hsv_to_rgb(nHue / 360.0 / 182.04, nSat / 255.0, nBri / 255.0)

                    r = int(r * 100.0)
                    g = int(g * 100.0)
                    b = int(b * 100.0)

                    self._set_output_value(self.PIN_O_NR, r)
                    self._set_output_value(self.PIN_O_NG, g)
                    self._set_output_value(self.PIN_O_NB, b)
        except:
            jsonState = []

        return json.dumps(jsonState)

    def httpPut(self, api_url, api_port, api_user, group, payload):
        httpClient = None
        data = {'data': "", 'status': -1}
        try:
            nTransTime = int(self._get_input_value(self.PIN_I_NTRANSTIME))
            if (nTransTime > 0):
                payload = payload[:-1]
                payload = payload + ',"transitiontime":' + str(nTransTime) + '}'

            api_path = '/api/' + api_user + '/groups/' + str(group) + '/action'
            headers = {"HOST": str(api_url + ":" + str(api_port)), "CONTENT-LENGTH": str(len(payload)),
                       "Content-type": 'application/json'}
            # headers = { "Content-type": 'application/json' }

            if not self.g_debug:
                httpClient = httplib.HTTPConnection(api_url, int(api_port), timeout=5)

                httpClient.request("PUT", api_path, payload, headers)
                response = httpClient.getresponse()
                status = response.status
                data = {'data': response.read(), 'status': status}
            else:
                data = {'data': '{"success" : True}', 'status': 200}
            return data
        # except Exception as e:
        except:
            return data
        finally:
            if httpClient:
                httpClient.close()

    def hueOnOff(self, api_url, api_port, api_user, group, bSetOn):
        payload = ""
        if bSetOn:
            payload = '{"on":true}'
        else:
            payload = '{"on":false}'

        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ("success" in ret["data"])

    def setScene(self, api_url, api_port, api_user, group, sScene):
        payload = '{"scene":"' + sScene + '"}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ("success" in ret["data"])

    def setEffect(self, api_url, api_port, api_user, group, nEffect):
        payload = '{"effect":"'

        if (nEffect == True):
            payload = payload + 'colorloop"}'
        else:
            payload = payload + 'none"}'

        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ("success" in ret["data"])

    def setAlert(self, api_url, api_port, api_user, group, bAlert):
        payload = ""
        if (bAlert == True):
            payload = '{"alert":"lselect"}'
        else:
            payload = '{"alert":"none"}'

        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    # @brief Sets the brightness of the hue group
    # @return True if successful
    # @param api_url
    # @param api_port
    # @param api_user
    # @param group
    # @param bri Brightness to be set [0-255]
    def set_bri(self, api_url, api_port, api_user, group, bri):
        if bri > 0 and not self.g_curr_on:
            self.hueOnOff(api_url, api_port, api_user, group, True)
        payload = '{"bri":' + str(bri) + '}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        if "success" in ret["data"]:
            self.g_currBri = bri
        return "success" in ret["data"]

    def set_hue_color(self, api_url, api_port, api_user, group, hue_col):
        payload = '{"hue":' + str(hue_col) + '}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_sat(self, api_url, api_port, api_user, group, sat):
        payload = '{"sat":' + str(sat) + '}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_ct(self, api_url, api_port, api_user, group, nCt):
        payload = '{"ct":' + str(nCt) + '}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def prep_dim(self, val):
        self.DEBUG.set_value("Dim cmd", str(val) + " " + str(type(val)))

        if (type(val) is float) or (type(val) is int):
            val = int(val)
            val = chr(val)
            val = bytearray(val)

        if val[-1] == 0x00:
            self.g_stop = True
            if self.g_timer.isAlive():
                self.g_timer.cancel()
            print("abort")
            return

        sgn_bte = int((val[-1] & 0x08) >> 3)
        val = int(val[-1] & 0x07)

        self.g_interval = round(255.0 / pow(2, val - 1), 0)

        if sgn_bte == 1:
            pass
        else:
            self.g_interval = int(-1 * self.g_interval)

        self.g_stop = False
        self.do_dim()

    def do_dim(self):
        if self.g_stop:
            return

        api_url = str(self._get_input_value(self.PIN_I_SHUEIP))
        api_port = int(self._get_input_value(self.PIN_I_NHUEPORT))
        api_user = str(self._get_input_value(self.PIN_I_SUSER))
        group = int(self._get_input_value(self.PIN_I_NGROUP))

        new_bri = int(self.g_currBri + self.g_interval)
        if new_bri > 255:
            new_bri = 255
        elif new_bri < 1:
            new_bri = 1

        self.set_bri(api_url, api_port, api_user, group, new_bri)

        duration = float(self._get_input_value(self.PIN_I_NDIMRAMP))

        self.g_timer = threading.Timer(duration, self.do_dim)
        self.g_timer.start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

    def on_input_value(self, index, value):
        res = False

        # Process State
        sApi_url = str(self._get_input_value(self.PIN_I_SHUEIP))
        nApi_port = int(self._get_input_value(self.PIN_I_NHUEPORT))
        sApi_user = str(self._get_input_value(self.PIN_I_SUSER))
        group = int(self._get_input_value(self.PIN_I_NGROUP))
        light = int(self._get_input_value(self.PIN_I_NLIGHT))
        hueGroupState = {"data": str(self._get_input_value(self.PIN_I_SGROUPSTATJSON)), "status": 200}
        hueLightState = {"data": str(self._get_input_value(self.PIN_I_SLIGHTSSTATJSON)), "status": 200}
        nBri = int(self._get_input_value(self.PIN_I_NBRI) / 100.0 * 255.0)
        nHueCol = int(self._get_input_value(self.PIN_I_NHUE))
        nSat = int(self._get_input_value(self.PIN_I_NSAT) / 100.0 * 255.0)
        nCt = int(self._get_input_value(self.PIN_I_NCT))

        # If trigger == 1, get data via web request
        if (self.PIN_I_BTRIGGER == index) and (bool(value)):
            hueGroupState = self.get_data(sApi_url, nApi_port, sApi_user, "groups")
            hueLightState = self.get_data(sApi_url, nApi_port, sApi_user, "lights")

        if ((self.PIN_I_BTRIGGER == index) or
                (self.PIN_I_SGROUPSTATJSON == index)):
            if (hueGroupState["data"]):
                if (group > 0):
                    self.readGroupsJson(hueGroupState["data"], group)
                    self._set_output_value(self.PIN_O_NGRPJSON, hueGroupState["data"])

        if ((self.PIN_I_BTRIGGER == index) or
                (self.PIN_I_SLIGHTSSTATJSON == index)):
            if (hueLightState["data"]):
                if (light > 0):
                    self.read_lights_json(hueLightState["data"], light)
                    self._set_output_value(self.PIN_O_NLGHTSJSON, hueLightState["data"])

        #### Process set commands
        if (self._get_input_value(self.PIN_I_SUSER) == "") or (self._get_input_value(self.PIN_I_SHUEIP) == ""):
            return

        if self.PIN_I_BONOFF == index:
            res = self.hueOnOff(sApi_url, nApi_port, sApi_user, group, value)
            if (res):
                self._set_output_value(self.PIN_O_BSTATUSONOFF, value)

        elif self.PIN_I_SSCENE == index:
            res = self.setScene(sApi_url, nApi_port, sApi_user, group, value)
            if (res):
                self._set_output_value(self.PIN_O_BSTATUSONOFF, True)

        elif self.PIN_I_NBRI == index:
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.set_bri(sApi_url, nApi_port, sApi_user, group, nBri)
            print(res)
            if (res):
                self._set_output_value(self.PIN_O_NBRI, nBri / 255.0 * 100.0)

        elif self.PIN_I_NHUE == index:
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.set_hue_color(sApi_url, nApi_port, sApi_user, group, nHueCol)
            if (res):
                self._set_output_value(self.PIN_O_NHUE, nHueCol)

        elif self.PIN_I_NSAT == index:
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.set_sat(sApi_url, nApi_port, sApi_user, group, nSat)
            if (res):
                self._set_output_value(self.PIN_O_NSAT, nSat / 255.0 * 100)

        elif self.PIN_I_NCT == index:
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.set_ct(sApi_url, nApi_port, sApi_user, group, nCt)
            if (res):
                self._set_output_value(self.PIN_O_NCT, nCt)

        elif ((self.PIN_I_NR == index) or
              (self.PIN_I_NG == index) or
              (self.PIN_I_NB == index)):
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)

            nR = int(int(self._get_input_value(self.PIN_I_NR)) * 2.55)
            nG = int(int(self._get_input_value(self.PIN_I_NG)) * 2.55)
            nB = int(int(self._get_input_value(self.PIN_I_NB)) * 2.55)
            # h, s, v = self.rgb2hsv(r, g, b)
            h, s, v = colorsys.rgb_to_hsv(r=(nR / 255.0), g=(nG / 255.0), b=(nB / 255.0))
            h = int(360.0 * 182.04 * h)
            s = int(s * 255)
            v = int(v * 255)

            ret1 = self.set_bri(sApi_url, nApi_port, sApi_user, group, v)
            ret2 = self.set_hue_color(sApi_url, nApi_port, sApi_user, group, h)
            ret3 = self.set_sat(sApi_url, nApi_port, sApi_user, group, s)

            if ret1 and ret2 and ret3:
                # set rgb as output
                self._set_output_value(self.PIN_O_NR, nR)
                self._set_output_value(self.PIN_O_NG, nG)
                self._set_output_value(self.PIN_O_NB, nB)

        elif self.PIN_I_BALERT == index:
            bAlert = int(self._get_input_value(self.PIN_I_BALERT))
            self.setAlert(sApi_url, nApi_port, sApi_user, group, bAlert)
            ###

        elif self.PIN_I_NEFFECT == index:
            nEffect = int(self._get_input_value(self.PIN_I_NEFFECT))
            self.setEffect(sApi_url, nApi_port, sApi_user, group, nEffect)

        elif self.PIN_I_NRELDIM == index:
            self.prep_dim(value)


############################################


class UnitTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_setBri(self):
        dummy = HueGroup_14100_14100()
        dummy.g_debug = True

        api_url = "192.168.0.10"
        api_port = "80"
        api_user = "debug"
        group = "1"
        light = 3

        ret = dummy.set_bri(api_url, api_port, api_user, group, 100)
        self.assertTrue(ret)
        self.assertEqual(dummy.g_currBri, 100)

    def test_readGroupsJson(self):
        dummy = HueGroup_14100_14100()
        dummy.g_debug = True
        dummy.g_currBri = 204

        api_url = "192.168.0.10"
        api_port = "80"
        api_user = "debug"
        group = "1"
        light = 3

        retGroups = {
            "data": '{"1": {"name": "Wohnzimmer", "lights": ["3", "5"], "state": {"any_on": true, "all_on": true}, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "none", "xy": [0.4779, 0.3823], "bri": 204, "ct": 399, "sat": 121}, "recycle": false, "sensors": [], "type": "Room", "class": "Living room"}, "3": {"name": "Thilo", "lights": [], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "alert": "none"}, "recycle": false, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "2": {"name": "Bad OG", "lights": ["4"], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "hue": 8402, "colormode": "xy", "effect": "none", "alert": "select", "xy": [0.4575, 0.4099], "bri": 254, "ct": 366, "sat": 140}, "recycle": false, "sensors": [], "type": "Room", "class": "Bathroom"}, "5": {"name": "Nora", "lights": ["7", "8"], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "bri": 1, "alert": "select"}, "recycle": false, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "4": {"name": "Flur DG", "lights": ["6"], "state": {"any_on": false, "all_on": false}, "action": {"on": false, "bri": 254, "alert": "select"}, "recycle": false, "sensors": [], "type": "Room", "class": "Hallway"}, "7": {"name": "TV", "lights": ["3"], "state": {"any_on": true, "all_on": true}, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "select", "xy": [0.4779, 0.3823], "bri": 204, "ct": 399, "sat": 121}, "recycle": false, "sensors": [], "type": "Zone", "class": "Downstairs"}, "6": {"name": "Garage", "lights": ["9"], "state": {"any_on": true, "all_on": true}, "action": {"on": true, "hue": 0, "colormode": "ct", "effect": "none", "alert": "select", "xy": [0.3805, 0.3769], "bri": 254, "ct": 370, "sat": 0}, "recycle": false, "sensors": [], "type": "Room", "class": "Carport"}}'}
        # retLights = dummy.getData(api_url, api_port, api_user, "lights")
        ret = dummy.readGroupsJson(retGroups["data"], 1)
        res = '{"1": {"name": "Wohnzimmer", "lights": ["3", "5"], "state": {"any_on": true, "all_on": true}, "recycle": false, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "none", "xy": [0.4779, 0.3823], "bri": 204, "sat": 121, "ct": 399}, "sensors": [], "type": "Room", "class": "Living room"}, "3": {"name": "Thilo", "lights": [], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "alert": "none"}, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "2": {"name": "Bad OG", "lights": ["4"], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "hue": 8402, "colormode": "xy", "effect": "none", "alert": "select", "xy": [0.4575, 0.4099], "bri": 254, "sat": 140, "ct": 366}, "sensors": [], "type": "Room", "class": "Bathroom"}, "5": {"name": "Nora", "lights": ["7", "8"], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "bri": 1, "alert": "select"}, "sensors": [], "type": "Room", "class": "Kids bedroom"}, "4": {"name": "Flur DG", "lights": ["6"], "state": {"any_on": false, "all_on": false}, "recycle": false, "action": {"on": false, "bri": 254, "alert": "select"}, "sensors": [], "type": "Room", "class": "Hallway"}, "7": {"name": "TV", "lights": ["3"], "state": {"any_on": true, "all_on": true}, "recycle": false, "action": {"on": true, "hue": 5226, "colormode": "hs", "effect": "none", "alert": "select", "xy": [0.4779, 0.3823], "bri": 204, "sat": 121, "ct": 399}, "sensors": [], "type": "Zone", "class": "Downstairs"}, "6": {"name": "Garage", "lights": ["9"], "state": {"any_on": true, "all_on": true}, "recycle": false, "action": {"on": true, "hue": 0, "colormode": "ct", "effect": "none", "alert": "select", "xy": [0.3805, 0.3769], "bri": 254, "sat": 0, "ct": 370}, "sensors": [], "type": "Room", "class": "Carport"}}'
        self.assertEqual(ret, res)
        # ret = dummy.readLightsJson(retLights["data"], light)

        # sScene = "mYJ1jB9LmBAG6yN"
        # sScene = "qhfcIHIJ9JuYK19"
        # nHueCol = 24381

    def test_dim(self):
        dummy = HueGroup_14100_14100()
        dummy.g_debug = True
        dummy.g_currBri = 255

        api_url = "192.168.0.10"
        api_port = "80"
        api_user = "debug"
        group = "1"
        light = 3

        ret = dummy.prep_dim(0x85)
        self.assertEqual(-16, dummy.g_interval)
        self.assertEqual(10, dummy.g_timer.interval)
        time.sleep(3)
        ret = dummy.prep_dim(0.0)
        # self.assertEqual(dummy.g_timer.interval, 1000)
        # self.assertFalse(dummy.g_timer.is_alive())

        ret = dummy.prep_dim(0x8d)
        self.assertEqual(16, dummy.g_interval)
        self.assertEqual(10, dummy.g_timer.interval)
        time.sleep(3)
        ret = dummy.prep_dim(0.0)
        # self.assertEqual(dummy.g_timer.interval, 1000)
        # self.assertFalse(dummy.g_timer.is_alive())


if __name__ == '__main__':
    unittest.main()
