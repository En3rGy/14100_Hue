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
        self.PIN_I_NTRANSTIME=18
        self.PIN_I_BALERT=19
        self.PIN_I_NEFFECT=20
        self.PIN_I_NRELDIM=21
        self.PIN_I_NDIMRAMP=22
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

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    g_debug = False
    g_currBri = 0
    g_intervall = 0
    g_timer = threading.Timer(1000, None)
    g_stopp = False

    # get general web request
    def getData(self, api_url, api_port, api_user, api_cmd):
        api_path = '/api/' + api_user + '/' + api_cmd
        data = ""

        try:
            httpClient = httplib.HTTPConnection(api_url, int(api_port), timeout=5)
            if (self.g_debug == False):
                httpClient.request("GET", api_path)
                response = httpClient.getresponse()
                status = response.status
                data = {'data' : response.read(), 'status' : status}
            else:
                data = {'data' : "debug", 'status' : 200}
            self.DEBUG.add_message("14100: Hue bridge response code: " + str(status))
        except Exception as e:
            self.DEBUG.add_message(str(e))
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
                    if 'reachable' in jsonState[str(light)]['state']:
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
        data = {'data' : "", 'status' : -1}
        try:
            nTransTime = int(self._get_input_value(self.PIN_I_NTRANSTIME))
            if (nTransTime > 0):
                payload = payload[:-1]
                payload = payload + ',"transitiontime":' + str(nTransTime) + '}'

            api_path = '/api/' + api_user + '/groups/' + str(group) + '/action'
            headers = { "HOST": str(api_url + ":" + str(api_port)), "CONTENT-LENGTH": str(len(payload)), "Content-type": 'application/json' }
            #headers = { "Content-type": 'application/json' }

            if (self.g_debug == False):
                httpClient = httplib.HTTPConnection(api_url, int(api_port), timeout=5)
    
                httpClient.request("PUT", api_path, payload, headers) 
                response = httpClient.getresponse()
                status = response.status
                data = {'data' : response.read(), 'status' : status}
            else:
                data = {'data' : '{"success" : True}', 'status' : 200}
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
        return ("success" in ret["data"])

    def setBri(self, api_url, api_port, api_user, group, nBri):
        if (nBri > 0):
            self.hueOnOff(api_url, api_port, api_user, group, True)
        payload = '{"bri":' + str(nBri) + '}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        if "success" in ret["data"]:
            self.g_currBri = nBri
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

    def prepDim(self, val):
        self.DEBUG.set_value("Dim cmd", str(val) + " " + str(type(val)))

        if (type(val) is float) or (type(val) is int):
            val = int(val)
            val = chr(val)
            val = bytearray(val)

        if (val[-1] == 0x00):
            self.g_stopp = True
            self.g_timer = threading.Timer(1000, None)
            print("abort")
            return

        sgn_bte = int((val[-1] & 0x08) >> 3)
        val = int(val[-1] & 0x07)

        self.g_intervall = round(255.0 / pow(2, val - 1), 0)

        if(sgn_bte == 1):
            pass
        else:
            self.g_intervall = int(-1 * self.g_intervall)

        self.g_stopp = False
        self.doDim()


    def doDim(self):
        if (self.g_stopp == True):
            return

        api_url = str(self._get_input_value(self.PIN_I_SHUEIP))
        api_port = int(self._get_input_value(self.PIN_I_NHUEPORT))
        api_user = str(self._get_input_value(self.PIN_I_SUSER))
        group = int(self._get_input_value(self.PIN_I_NGROUP))

        newBri = int(self.g_currBri + self.g_intervall)
        if (newBri > 255):
            newBri = 255
        elif(newBri < 1):
            newBri = 1

        self.setBri(api_url, api_port, api_user, group, newBri)

        duration = float(self._get_input_value(self.PIN_I_NDIMRAMP))
        steps = 255 / abs(self.g_intervall)
        step = float(round(duration / steps, 4))

        self.g_timer = threading.Timer(step, self.doDim)
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
        hueGroupState = {"data" : str(self._get_input_value(self.PIN_I_SGROUPSTATJSON)), "status" : 200}
        hueLightState = {"data" : str(self._get_input_value(self.PIN_I_SLIGHTSSTATJSON)), "status"  :200}
        nBri = int(self._get_input_value(self.PIN_I_NBRI) / 100.0 * 255.0)
        nHueCol = int(self._get_input_value(self.PIN_I_NHUE))
        nSat = int(self._get_input_value(self.PIN_I_NSAT) / 100.0 * 255.0)
        nCt = int(self._get_input_value(self.PIN_I_NCT))

        #### If trigger == 1, get data via web request
        if (self.PIN_I_BTRIGGER == index) and (bool(value)):
            hueGroupState = self.getData(sApi_url, nApi_port, sApi_user, "groups")
            hueLightState = self.getData(sApi_url, nApi_port, sApi_user, "lights")

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

        elif self.PIN_I_SSCENE == index:
            res = self.setScene(sApi_url, nApi_port, sApi_user, group, value)
            if (res):
                self._set_output_value(self.PIN_O_BSTATUSONOFF, True)

        elif self.PIN_I_NBRI == index :
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.setBri(sApi_url, nApi_port, sApi_user, group, nBri)
            print(res)
            if (res):
                self._set_output_value(self.PIN_O_NBRI, nBri / 255.0 * 100.0)

        elif self.PIN_I_NHUE == index :
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.setHueColor(sApi_url, nApi_port, sApi_user, group, nHueCol)
            if (res):
                self._set_output_value(self.PIN_O_NHUE, nHueCol)

        elif self.PIN_I_NSAT == index :
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.setSat(sApi_url, nApi_port, sApi_user, group, nSat)
            if (res):
                self._set_output_value(self.PIN_O_NSAT, nSat / 255.0 * 100)

        elif self.PIN_I_NCT == index :
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)
            res = self.setCt(sApi_url, nApi_port, sApi_user, group, nCt)
            if (res):
                self._set_output_value(self.PIN_O_NCT, nCt)

        elif ((self.PIN_I_NR == index) or
             (self.PIN_I_NG == index) or
             (self.PIN_I_NB == index)):
            self.hueOnOff(sApi_url, nApi_port, sApi_user, group, True)

            nR = int(int(self._get_input_value(self.PIN_I_NR)) * 2.55)
            nG = int(int(self._get_input_value(self.PIN_I_NG)) * 2.55)
            nB = int(int(self._get_input_value(self.PIN_I_NB)) * 2.55)
            #h, s, v = self.rgb2hsv(r, g, b)
            h, s, v = colorsys.rgb_to_hsv(r = (nR / 255.0), g = (nG / 255.0), b = (nB / 255.0))
            h = int(360.0 * 182.04 * h)
            s = int(s * 255)
            v = int(v * 255)

            ret1 = self.setBri(sApi_url, nApi_port, sApi_user, group, v)
            ret2 = self.setHueColor(sApi_url, nApi_port, sApi_user, group, h)
            ret3 = self.setSat(sApi_url, nApi_port, sApi_user, group, s)

            if(ret1 and ret2 and ret3):
                #set rgb as output
                self._set_output_value(self.PIN_O_NR, nR)
                self._set_output_value(self.PIN_O_NG, nG)
                self._set_output_value(self.PIN_O_NB, nB)

        elif (self.PIN_I_BALERT == index):
            bAlert = int(self._get_input_value(self.PIN_I_BALERT))
            self.setAlert(sApi_url, nApi_port, sApi_user, group, bAlert)
            ###

        elif (self.PIN_I_NEFFECT == index):
            nEffect = int(self._get_input_value(self.PIN_I_NEFFECT))
            self.setEffect(sApi_url, nApi_port, sApi_user, group, nEffect)

        elif (self.PIN_I_NRELDIM == index):
            self.prepDim(value)
