# coding=utf-8
import hue_lib.supp_fct as supp_fct
import threading


class HueDevice:

    def __init__(self):
        self.interval = 0  # type: int
        self.id = str()  # type: str
        self.name = str()  # type: str
        self.room_name = str()  # type: str
        self.device_id = str()  # type: str
        self.light_id = str()  # type: str
        self.zigbee_connectivity_id = str()  # type: str
        self.room = str()  # type: str
        self.zone = str()  # type: str
        self.scenes = []  # type: [str]
        self.grouped_lights = []  # type: [str]
        self.rtype = str()  # type: str
        self.curr_bri = 0  # type: int
        self.stop = False  # type: bool
        self.timer = None   # type: threading.Timer
        self.ip = str()  # type: str
        self.key = str()  # type: str
        self.dim_ramp = 0  # type: int

    def __str__(self):
        return ("<tr>" +
                "<td>" + self.room_name.encode("ascii", "xmlcharrefreplace") + "</td>" +
                "<td>" + self.name.encode("ascii", "xmlcharrefreplace") + "</td>" +
                "<td>" + self.device_id.encode("ascii", "xmlcharrefreplace") + "</td>" +
                "<td>" + self.light_id.encode("ascii", "xmlcharrefreplace") + "</td>" +
                "<td>" + str(self.grouped_lights).encode("ascii", "xmlcharrefreplace") + "</td>" +
                "<td>" + self.zigbee_connectivity_id.encode("ascii", "xmlcharrefreplace") + "</td>" +
                "<td>" + self.room.encode("ascii", "xmlcharrefreplace") + "</td>" +
                "<td>" + self.zone.encode("ascii", "xmlcharrefreplace") + "</td>" +
                "<td>" + str(self.scenes).encode("ascii", "xmlcharrefreplace") + "</td>" +
                "</tr>\n")

    def get_device_ids(self):
        ret = [self.device_id, self.light_id, self.zigbee_connectivity_id, self.room, self.zone]   # type: [str]
        for scene in self.scenes:
            ret.extend(scene["id"])
        ret.extend(self.grouped_lights)

        return ret

    def set_on(self, ip, key, set_on):
        """
        on / off

        :param key:
        :param ip:
        :type ip: str
        :type key: str
        :param set_on: True / False
        :type set_on: bool
        :rtype: bool
        :return:
        """
        supp_fct.log_debug("entering set_on")

        if self.rtype == "room" or self.rtype == "zone":
            supp_fct.log_debug("In set_on #744, on/off not available for rooms or zones")
            return False

        if set_on:
            payload = '{"on":{"on":true}}'
        else:
            payload = '{"on":{"on":false}}'

        ret = supp_fct.http_put(ip, key, self.id, self.rtype, payload)
        return ret["status"] == 200

    def set_bri(self, ip, key, brightness):
        """
        Brightness percentage. value cannot be 0, writing 0 changes it to the lowest possible brightness

        :param key:
        :param ip:
        :type ip: str
        :type key: str
        :type brightness: int
        :param brightness: number – maximum: 100
        :return: True if successful, otherwise False
        :rtype: bool
        """
        supp_fct.log_debug("entering set_bri")

        payload = '{"dimming":{"brightness":' + str(brightness) + '}}'
        ret = supp_fct.http_put(ip, key, self.id, self.rtype, payload)
        self.curr_bri = brightness
        return ret["status"] == 200

    def set_color_xy_bri(self, ip, key, x, y, bri):
        """
        CIE XY gamut position

        :param key:
        :type key: str
        :param ip:
        :type ip: str
        :param x: number – minimum: 0 – maximum: 1
        :type x: float
        :param y: number – minimum: 0 – maximum: 1
        :type y: float
        :param bri: 0-100%
        :type bri: int
        :rtype: bool
        :return:
        """
        supp_fct.log_debug("set_color_xy_bri")

        payload = '{"color":{"xy":{"x":' + str(x) + ', "y":' + str(y) + '}}}'

        ret = supp_fct.http_put(ip, key, self.id, self.rtype, payload)
        supp_fct.log_debug("In set_color_xy_bri #780, return code is " + str(ret["status"]))
        return ret["status"] == 200  # & self.set_bri(bri)

    def set_color_rgb(self, ip, key, r, g, b):
        """

        :param key:
        :type key: str
        :param ip:
        :type ip: str
        :type r: int
        :type g: int
        :type b: int
        :param r: 0-100 prct
        :param g: 0-100 prct
        :param b: 0-100 prct
        :rtype: bool
        :return:
        """

        r = int(r * 2.55)  # type: int
        g = int(g * 2.55)  # type: int
        b = int(b * 2.55)  # type: int

        supp_fct.log_debug("entering set_color")
        [x, y, bri] = supp_fct.rgb_to_xy_bri(r, g, b)
        return self.set_color_xy_bri(ip, key, x, y, bri)

    def set_scene(self, ip, key, scene_id):
        """

        :param key:
        :type key: str
        :param scene_id:
        :type scene_id: str
        :param ip:
        :type ip: str
        :rtype: bool
        :return:
        """
        supp_fct.log_debug("Entering set_scene")
        payload = '{"recall":{"action": "active"}}'
        ret = supp_fct.http_put(ip, key, scene_id, "scene", payload)
        return ret["status"] == 200

    def set_dynamic_scene(self, ip, key, scene_id):
        """

        :param key:
        :type key: str
        :param scene_id:
        :type scene_id: str
        :param ip:
        :type ip: str
        :rtype: bool
        :return:
        """
        supp_fct.log_debug("Entering set_dynamic_scene")
        payload = '{"recall": {"action": "dynamic_palette"}, "speed": 0.7}'
        ret = supp_fct.http_put(ip, key, scene_id, "scene", payload)
        return ret["status"] == 200

    def prep_dim(self, ip, key, val, dim_ramp):
        """

        :param dim_ramp: Time in [s] until next dim step is performed
        :param key:
        :param ip:
        :param val:
        :type dim_ramp: int
        :type key: str
        :type ip: str
        :type val: int
        :return:
        """

        supp_fct.log_debug("Dim cmd, str(val)" + " " + str(type(val)))

        if (type(val) is float) or (type(val) is int):
            val = int(val)
            val = chr(val)
            val = bytearray(val)

        if val[-1] == 0x00:
            self.stop = True
            # self.timer.cancel()
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
        self.ip = ip
        self.key = key
        self.dim_ramp = dim_ramp
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

        self.set_bri(self.ip, self.key, new_bri)

        if new_bri == 255 or new_bri == 1:
            return

        steps = 255 / abs(self.interval)
        step = float(round(self.dim_ramp / steps, 4))

        self.timer = threading.Timer(step, self.do_dim)
        self.timer.start()

    def get_type_of_device(self):
        if self.id in self.device_id:
            self.rtype = "device"
        elif self.id in self.room:
            self.rtype = "room"
        elif self.id in self.zone:
            self.rtype = "zone"
        elif self.id in self.scenes:
            self.rtype = "scene"
        elif self.id in self.grouped_lights:
            self.rtype = "grouped_light"
        elif self.id in self.light_id:
            self.rtype = "light"

        return self.rtype
