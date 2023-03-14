# coding=utf-8
import hue_lib.supp_fct as supp_fct
import threading
import logging


class HueDevice:

    def __init__(self, logger):
        """
        Initialize the device object and store a reference to the logger.

        :param logger: The logger to use for logging messages.
        :type logger: logging.Logger
        """
        self.interval = 0  # type: int
        self.logger = logger
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
        self.timer = threading.Timer(10, self.do_dim)   # type: threading.Timer
        self.ip = str()  # type: str
        self.key = str()  # type: str
        self.dim_ramp = 0  # type: int
        self.gamut_type = str()

    def __str__(self):
        res = ("<tr>" +
                "<td>" + self.room_name.encode("ascii", "xmlcharrefreplace") + "</td>" +
                "<td>" + self.name.encode("ascii", "xmlcharrefreplace") + "</td>" +
                "<td>" + self.device_id.encode("ascii", "xmlcharrefreplace") + "</td>" +
                "<td>" + self.light_id.encode("ascii", "xmlcharrefreplace") + "</td>")
        res += "<td><ul>"
        for light_id in self.grouped_lights:
            res += "<li>{}</li>\n".format(str(light_id).encode("ascii", "xmlcharrefreplace"))
        res += "</ul></td>"
        res += ( "<td>" + self.zigbee_connectivity_id.encode("ascii", "xmlcharrefreplace") + "</td>" +
                 "<td>" + self.room.encode("ascii", "xmlcharrefreplace") + "</td>" +
                 "<td>" + self.zone.encode("ascii", "xmlcharrefreplace") + "</td>" +
                 "<td>")

        # table in table
        res += "<table><tr><th>Name</th><th>Scene Id</th></tr>"
        for scene in self.scenes:
            sc_name = scene["name"].encode("ascii", "xmlcharrefreplace")
            sc_id = scene["id"].encode("ascii", "xmlcharrefreplace")
            res += "<tr><td>{name}</td><td>{id}</td></tr>".format(name=sc_name, id=sc_id)
        res += "</table>"
        res += "</td></tr>\n"

        return res

    def get_device_ids(self):
        with supp_fct.TraceLog(self.logger):
            ret = [self.device_id, self.light_id, self.zigbee_connectivity_id, self.room, self.zone]   # type: [str]
            for scene in self.scenes:
                ret.append(scene["id"])  # tod: check if extend vs. append
            ret.extend(self.grouped_lights)
            ret = filter(lambda x: x != '', ret)  # remove empty elements

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
        :return: True if successful, false if otherwise
        """
        with supp_fct.TraceLog(self.logger):
            if self.rtype == "room" or self.rtype == "zone":
                self.logger.warning("Trying to set a room or zone on/off. This is not allowed. Discarding.")
                return False

            if set_on:
                payload = '{"on":{"on":true}}'
            else:
                payload = '{"on":{"on":false}}'

            ret = supp_fct.http_put(ip, key, self.id, self.rtype, payload, self.logger)
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
        with supp_fct.TraceLog(self.logger):

            payload = '{"dimming":{"brightness":' + str(brightness) + '}}'
            ret = supp_fct.http_put(ip, key, self.id, self.rtype, payload, self.logger)
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
        :return: True if successful, false if not.
        """
        with supp_fct.TraceLog(self.logger):
            payload = '{"color":{"xy":{"x":' + str(x) + ', "y":' + str(y) + '}}}'

            ret = supp_fct.http_put(ip, key, self.id, self.rtype, payload, self.logger)
            self.logger.debug("In set_color_xy_bri #780, return code is " + str(ret["status"]))
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
        :return: True if successful, false if not.
        """
        with supp_fct.TraceLog(self.logger):
            r = int(r * 2.55)  # type: int
            g = int(g * 2.55)  # type: int
            b = int(b * 2.55)  # type: int

            [x, y, bri] = supp_fct.rgb_to_xy_bri(r, g, b, self.gamut_type)
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
        :return: True if successful, false if not.
        """
        with supp_fct.TraceLog(self.logger):
            payload = '{"recall":{"action": "active"}}'
            ret = supp_fct.http_put(ip, key, scene_id, "scene", payload, self.logger)
            return ret["status"] == 200

    def set_dynamic_scene(self, ip, key, scene_id, speed):
        """

        :param speed: Speed of dynamic palette for this scene (0-1)
        :type speed: float
        :param key:
        :type key: str
        :param scene_id:
        :type scene_id: str
        :param ip:
        :type ip: str
        :rtype: bool
        :return: True if successful, false if not.
        """
        with supp_fct.TraceLog(self.logger):
            payload = '{"recall": {"action": "dynamic_palette"}, "speed": ' + str(speed) + '}'
            ret = supp_fct.http_put(ip, key, scene_id, "scene", payload, self.logger)
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
        :return: None
        """
        with supp_fct.TraceLog(self.logger):

            if (type(val) is float) or (type(val) is int):
                val = int(val)
                val = chr(val)
                val = bytearray(val)

            if val[-1] == 0x00:
                self.stop = True
                # self.timer.cancel()
                self.timer = None
                self.logger.debug("abort")
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
        with supp_fct.TraceLog(self.logger):
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
        """

        :return: Type of this Hue device (device, room, zone, scene, grouped_light, light)
        :rtype: str
        """
        with supp_fct.TraceLog(self.logger):
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
