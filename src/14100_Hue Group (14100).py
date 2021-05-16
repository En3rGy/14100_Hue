# coding: UTF-8
import httplib
import json
import colorsys
import threading


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

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

    # get general web request
    def get_data(self, api_url, api_port, api_user, api_cmd):
        api_path = '/api/' + api_user + '/' + api_cmd
        data = ""

        try:
            http_client = httplib.HTTPConnection(api_url, int(api_port), timeout=5)
            if not self.debug:
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

        if http_client:
            http_client.close()

        return data

    def read_json(self, json_state, idx):
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
                self._set_output_value(self.PIN_O_BSTATUSONOFF, on_off)

                if 'reachable' in action_sub:
                    reachable = int(action_sub['reachable'])
                    self._set_output_value(self.PIN_O_NREACHABLE, reachable)
                if 'bri' in action_sub:
                    bri = int(action_sub['bri'])
                    self.curr_bri = bri
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
            if trans_time > 0:
                payload = payload[:-1]
                payload = payload + ',"transitiontime":' + str(trans_time) + '}'

            ctrl_grp = bool(self._get_input_value(self.PIN_I_CTRL_GRP))
            api_path = ""
            if ctrl_grp:
                api_path = '/api/' + api_user + '/groups/' + str(group) + '/action'
            else:
                api_path = '/api/' + api_user + '/lights/' + str(group) + '/state'
            headers = {"HOST": str(api_url + ":" + str(api_port)), "CONTENT-LENGTH": str(len(payload)),
                       "Content-type": 'application/json'}
            # headers = { "Content-type": 'application/json' }

            if not self.debug:
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

    def hue_on_off(self, api_url, api_port, api_user, group, set_on):
        payload = ""
        if set_on:
            payload = '{"on":true}'
        else:
            payload = '{"on":false}'

        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_scene(self, api_url, api_port, api_user, group, scene):
        payload = '{"scene":"' + scene + '"}'
        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_effect(self, api_url, api_port, api_user, group, effect):
        payload = '{"effect":"'

        if effect:
            payload = payload + 'colorloop"}'
        else:
            payload = payload + 'none"}'

        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_alert(self, api_url, api_port, api_user, group, alert):
        payload = ""
        if alert:
            payload = '{"alert":"lselect"}'
        else:
            payload = '{"alert":"none"}'

        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_bri(self, api_url, api_port, api_user, group, bri):
        if bri > 0:
            self.hue_on_off(api_url, api_port, api_user, group, True)
        payload = '{"bri":' + str(bri) + '}'
        ret = self.http_put(api_url, api_port, api_user, group, payload)
        if "success" in ret["data"]:
            self.curr_bri = bri
        return "success" in ret["data"]

    def set_hue_color(self, api_url, api_port, api_user, group, hue_col):
        payload = '{"hue":' + str(hue_col) + '}'
        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_sat(self, api_url, api_port, api_user, group, sat):
        payload = '{"sat":' + str(sat) + '}'
        ret = self.http_put(api_url, api_port, api_user, group, payload)
        return "success" in ret["data"]

    def set_ct(self, api_url, api_port, api_user, group, ct):
        payload = '{"ct":' + str(ct) + '}'
        ret = self.http_put(api_url, api_port, api_user, group, payload)
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
        itm_idx = int(self._get_input_value(self.PIN_I_ITM_IDX))
        hue_state = {"data": str(self._get_input_value(self.PIN_I_STAT_JSON)), "status": 200}
        bri = int(self._get_input_value(self.PIN_I_NBRI) / 100.0 * 255.0)
        hue_ol = int(self._get_input_value(self.PIN_I_NHUE))
        sat = int(self._get_input_value(self.PIN_I_NSAT) / 100.0 * 255.0)
        ct = int(self._get_input_value(self.PIN_I_NCT))
        ctrl_group = self._get_input_value(self.PIN_I_CTRL_GRP)

        # If trigger == 1, get data via web request
        if (self.PIN_I_BTRIGGER == index) and (bool(value)):
            if ctrl_group:
                hue_state = self.get_data(api_url, api_port, api_user, "groups")
            else:
                hue_state = self.get_data(api_url, api_port, api_user, "lights")

        if ((self.PIN_I_BTRIGGER == index) or
                (self.PIN_I_STAT_JSON == index)):
            if hue_state["data"]:
                if itm_idx > 0:
                    self.read_json(hue_state["data"], itm_idx)
                    self._set_output_value(self.PIN_O_JSON, hue_state["data"])

        # Process set commands
        if (self._get_input_value(self.PIN_I_SUSER) == "") or (self._get_input_value(self.PIN_I_SHUEIP) == ""):
            return

        if self.PIN_I_BONOFF == index:
            res = self.hue_on_off(api_url, api_port, api_user, itm_idx, value)
            if res:
                self._set_output_value(self.PIN_O_BSTATUSONOFF, value)

        elif self.PIN_I_SSCENE == index:
            res = self.set_scene(api_url, api_port, api_user, itm_idx, value)
            if res:
                self._set_output_value(self.PIN_O_BSTATUSONOFF, True)

        elif self.PIN_I_NBRI == index:
            self.hue_on_off(api_url, api_port, api_user, itm_idx, True)
            res = self.set_bri(api_url, api_port, api_user, itm_idx, bri)
            print(res)
            if res:
                self._set_output_value(self.PIN_O_NBRI, bri / 255.0 * 100.0)

        elif self.PIN_I_NHUE == index:
            self.hue_on_off(api_url, api_port, api_user, itm_idx, True)
            res = self.set_hue_color(api_url, api_port, api_user, itm_idx, hue_ol)
            if res:
                self._set_output_value(self.PIN_O_NHUE, hue_ol)

        elif self.PIN_I_NSAT == index:
            self.hue_on_off(api_url, api_port, api_user, itm_idx, True)
            res = self.set_sat(api_url, api_port, api_user, itm_idx, sat)
            if res:
                self._set_output_value(self.PIN_O_NSAT, sat / 255.0 * 100)

        elif self.PIN_I_NCT == index:
            self.hue_on_off(api_url, api_port, api_user, itm_idx, True)
            res = self.set_ct(api_url, api_port, api_user, itm_idx, ct)
            if res:
                self._set_output_value(self.PIN_O_NCT, ct)

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
                self._set_output_value(self.PIN_O_NR, red)
                self._set_output_value(self.PIN_O_NG, green)
                self._set_output_value(self.PIN_O_NB, blue)

        elif self.PIN_I_BALERT == index:
            alert = int(self._get_input_value(self.PIN_I_BALERT))
            self.set_alert(api_url, api_port, api_user, itm_idx, alert)
            ###

        elif self.PIN_I_NEFFECT == index:
            effect = int(self._get_input_value(self.PIN_I_NEFFECT))
            self.set_effect(api_url, api_port, api_user, itm_idx, effect)

        elif self.PIN_I_NRELDIM == index:
            self.prep_dim(value)