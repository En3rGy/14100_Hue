# coding: UTF-8
import httplib
import json
import colorsys

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class HueGroup_14100_14100(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "hsl20_3_Hue")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
        self.PIN_I_SGROUPSTATJSON=1
        self.PIN_I_SLIGHTSSTATJSON=2
        self.PIN_I_BTRIGGER=3
        self.PIN_I_SHUEIP=4
        self.PIN_I_NHUEPORT=5
        self.PIN_I_SUSER=6
        self.PIN_I_NGROUP=7
        self.PIN_I_NLIGHT=8
        self.PIN_I_BONOFF=9
        self.PIN_I_NBRI=10
        self.PIN_I_NHUE=11
        self.PIN_I_NSAT=12
        self.PIN_I_NCT=13
        self.PIN_I_NR=14
        self.PIN_I_NG=15
        self.PIN_I_NB=16
        self.PIN_I_SSCENE=17
        self.PIN_O_BSTATUSONOFF=1
        self.PIN_O_NBRI=2
        self.PIN_O_NHUE=3
        self.PIN_O_NSAT=4
        self.PIN_O_NCT=5
        self.PIN_O_NR=6
        self.PIN_O_NG=7
        self.PIN_O_NB=8
        self.PIN_O_NREACHABLE=9
        self.PIN_O_NGRPJSON=10
        self.PIN_O_NLGHTSJSON=11
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    # get general web request
    def getData(self, api_url, api_port, api_user, api_cmd):
        api_path = '/api/' + api_user + '/' + api_cmd
        data = ""

        try:
            httpClient = httplib.HTTPConnection(api_url, int(api_port), timeout=5)
            httpClient.request("GET", api_path)
            response = httpClient.getresponse()
            status = response.status
            data = {'data' : response.read(), 'status' : status}
            self.DEBUG.set_value("Response code", status)
        except Exception as e:
            print(e)
            return
        finally:
            if httpClient:
                httpClient.close()

        return data

    # read light data from json
    def readLightsJson(self, jsonState, light):
        try:
            jsonState = json.loads(jsonState)

            if str(light) in jsonState:
                if 'state' in jsonState[str(light)]:
                    if 'reachable' in jsonState[str(light)]['action']:
                        bReachable = jsonState[str(light)]['state']['reachable']
                        self._set_output_value(self.PIN_O_NREACHABLE, bReachable)
        except:
            jsonState = []

        return json.dumps(jsonState)

    def readGroupsJson(self, jsonState, group):
        try:
            jsonState = json.loads(jsonState)
            
            if str(group) in jsonState:
                if 'action' in jsonState[str(group)]:
                    actionSub = jsonState[str(group)]["action"]
                    bOnOff = actionSub['on']
                    self._set_output_value(self.PIN_O_BSTATUSONOFF, bOnOff)

                    if 'bri' in actionSub:
                        nBri = int(actionSub['bri'] / 254.0 * 100)
                        self._set_output_value(self.PIN_O_NBRI, nBri)
                    if 'hue' in actionSub:
                        nHue = actionSub['hue']
                        self._set_output_value(self.PIN_O_NHUE, nHue)
                    if 'sat' in actionSub:
                        nSat = actionSub['sat'] / 254.0 * 100
                        self._set_output_value(self.PIN_O_NSAT, nSat)
                    if 'ct' in actionSub:
                        nCt = actionSub['ct']
                        self._set_output_value(self.PIN_O_NCT, nCt)
                        
                    r, g, b = colorsys.hsv_to_rgb(nHue / 360.0 / 182.04, nSat / 255.0, nBri / 255.0)

                    r = int(r * 255.0)
                    g = int(g * 255.0)
                    b = int(b * 255.0)

                    self._set_output_value(self.PIN_O_NR, r)
                    self._set_output_value(self.PIN_O_NG, g)
                    self._set_output_value(self.PIN_O_NB, b)
        except:
            jsonState = []

        return json.dumps(jsonState)

    def httpPut(self, api_url, api_port, api_user, group, payload):
        httpClient = None
        data = {'data' : "", 'status' : -1}
        try:
            api_path = '/api/' + api_user + '/groups/' + str(group) + '/action'
            headers = { "HOST": str(api_url + ":" + str(api_port)), "CONTENT-LENGTH": str(len(payload)), "Content-type": 'application/json' }
            #headers = { "Content-type": 'application/json' }            
            httpClient = httplib.HTTPConnection(api_url, int(api_port), timeout=5)
            httpClient.request("PUT", api_path, payload, headers) 
            response = httpClient.getresponse()
            status = response.status
            data = {'data' : response.read(), 'status' : status}
            #print data
            return data
        #except Exception as e:
        except:
            return data
        finally:
            if httpClient:
                httpClient.close()

    def hueOnOff(self, api_url, api_port, api_user, group, bSetOn):
        payload = ""
        if bSetOn == True:
            payload = '{"on":true}'
        else:
            payload = '{"on":false}'

        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ("success" in ret["data"])

    def setScene(self, api_url, api_port, api_user, group, sScene):
        payload = '{"scene":"' + sScene + '"}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ("success" in ret["data"])

    def setBri(self, api_url, api_port, api_user, group, nBri):
        if (nBri > 0):
            self.hueOnOff(api_url, api_port, api_user, group, True)
        payload = '{"bri":' + str(nBri) + '}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ("success" in ret["data"])

    def setHueColor(self, api_url, api_port, api_user, group, nHueCol):
        payload = '{"hue":' + str(nHueCol) + '}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ("success" in ret["data"])

    def setSat(self, api_url, api_port, api_user, group, nSat):
        payload = '{"sat":' + str(nSat) + '}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ("success" in ret["data"])

    def setCt(self, api_url, api_port, api_user, group, nCt):
        payload = '{"ct":' + str(nCt) + '}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ("success" in ret["data"])

    #Hue HSB (heu, sat, bri) = HSV
    #def rgb2hsv(self, r, g, b):
    #    r, g, b = r / 255.0, g / 255.0, b / 255.0
    #    mx = max(r, g, b)
    #    mn = min(r, g, b)
    #    df = mx - mn

    #    if mx == mn:
    #        h = 0
    #    elif mx == r:
    #        h = (60 * ((g-b)/df) + 360) % 360
    #    elif mx == g:
    #        h = (60 * ((b-r)/df) + 120) % 360
    #    elif mx == b:
    #        h = (60 * ((r-g)/df) + 240) % 360

    #    if mx == 0:
    #        s = 0
    #    else:
    #        s = df/mx

    #    v = mx

    #    h = int(182.04 * h)
    #    s = int(s * 255)
    #    v = int(v * 255)

        return h, s, v


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
        hueGroupState = {"data" : str(self._get_input_value(self.PIN_I_SGROUPSTATJSON)), "status" : 200}
        hueLightState = {"data" : str(self._get_input_value(self.PIN_I_SLIGHTSSTATJSON)), "status"  :200}
        nBri = int(self._get_input_value(self.PIN_I_NBRI) / 100.0 * 254)
        nHueCol = int(self._get_input_value(self.PIN_I_NHUE))
        nSat = int(self._get_input_value(self.PIN_I_NSAT) / 100.0 * 254)
        nCt = int(self._get_input_value(self.PIN_I_NCT))

        #### If trigger == 1, get data via web request
        if (self.PIN_I_BTRIGGER == index) and (bool(value)):
            hueGroupState = self.getData(sApi_url, nApi_port, sApi_user, "groups")
            hueLightState = self.getData(sApi_url, nApi_port, sApi_user, "lights")
            #self.DEBUG.set_value("grp json", hueGroupState)
            #self.DEBUG.set_value("lght json", hueLightState)

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
                    self.readLightsJson(hueLightState["data"], light)
                    self._set_output_value(self.PIN_O_NLGHTSJSON, hueLightState["data"])

        #### Process set commands
        if (self._get_input_value(self.PIN_I_SUSER) == "") or (self._get_input_value(self.PIN_I_SHUEIP) == ""):
            return

        if self.PIN_I_BONOFF == index:
            res = self.hueOnOff(sApi_url, nApi_port, sApi_user, group, value)
            if (res):
                self._set_output_value(self.PIN_O_BSTATUSONOFF, value)

        if self.PIN_I_SSCENE == index:
            res = self.setScene(sApi_url, nApi_port, sApi_user, group, value)
            if (res):
                self._set_output_value(self.PIN_O_BSTATUSONOFF, True)

        if self.PIN_I_NBRI == index :
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.setBri(sApi_url, nApi_port, sApi_user, group, nBri)
            print(res)
            if (res):
                self._set_output_value(self.PIN_O_NBRI, nBri)

        if self.PIN_I_NHUE == index :
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.setHueColor(sApi_url, nApi_port, sApi_user, group, nHueCol)
            if (res):
                self._set_output_value(self.PIN_O_NHUE, nHueCol)

        if self.PIN_I_NSAT == index :
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.setSat(sApi_url, nApi_port, sApi_user, group, nSat)
            if (res):
                self._set_output_value(self.PIN_O_NSAT, nSat)

        if self.PIN_I_NCT == index :
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.setCt(sApi_url, nApi_port, sApi_user, group, nCt)
            if (res):
                self._set_output_value(self.PIN_O_NCT, nCt)

        if ((self.PIN_I_NR == index) or
            (self.PIN_I_NG == index) or
            (self.PIN_I_NB == index)):
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)

            r = int(self._get_input_value(self.PIN_I_NR))
            g = int(self._get_input_value(self.PIN_I_NG))
            b = int(self._get_input_value(self.PIN_I_NB))
            #h, s, v = self.rgb2hsv(r, g, b)
            h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            h = int(360.0 * 182.04 * h)
            s = int(s * 255)
            v = int(v * 255)

            ret1 = self.setBri(sApi_url, nApi_port, sApi_user, group, v)
            ret2 = self.setHueColor(sApi_url, nApi_port, sApi_user, group, h)
            ret3 = self.setSat(sApi_url, nApi_port, sApi_user, group, s)

            if(ret1 and ret2 and ret3):
                #set rgb as output
                self._set_output_value(self.PIN_O_NR, r)
                self._set_output_value(self.PIN_O_NG, g)
                self._set_output_value(self.PIN_O_NB, b)
