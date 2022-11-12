# coding=utf-8
import hue_lib.supp_fct as supp_fct


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
        self.rtype = str()  # type: str
        self.curr_bri = 0  # type: int

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
        :param r: 0-255
        :param g: 0-255
        :param b: 0-255
        :rtype: bool
        :return:
        """

        r = int(r / 255.0)  # type: int
        g = int(g / 255.0)  # type: int
        b = int(b / 255.0)  # type: int

        supp_fct.log_debug("entering set_color")
        [x, y, bri] = supp_fct.rgb_to_xy_bri(r, g, b)
        return self.set_color_xy_bri(ip, key, x, y, bri)

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

        # if not self.rtype == "scene":
        #     supp_fct.log_debug("In set_dynamic_scene #818, dynamic scenes only work with scenes")
        #     return False

        payload = '{"recall": {"action": "dynamic_palette"}, "speed": 0.7}'

        ret = supp_fct.http_put(ip, key, scene_id, "scene", payload)
        return ret["status"] == 200

