# coding=utf-8
import urlparse
import ssl
import urllib2
import json
import inspect
import rgbxy


class TraceLog:
    # Usage e.g. tracelog = supp_fct.TraceLog(self.logger)
    def __init__(self, logger):
        self.logger = logger
        self.logger.trace("Entering {}".format(inspect.stack()[1][3]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

    def __del__(self):
        self.logger.trace("Leaving {}".format(inspect.stack()[1][3]))


def rgb_to_xy(red, green, blue, gamut):
    """
    Convert rgb to xy

    :param gamut: A, B or C; if other, Gamut B is used.
    :type gamut: str
    :param red: 0-255
    :param green: 0-255
    :param blue: 0-255
    :return: [x (0.0-1.0), y (0.0-1.0), brightness (0-100%)]
    """

    if gamut is "A":
        gamut_type = rgbxy.GamutA
    elif gamut is "B":
        gamut_type = rgbxy.GamutB
    elif gamut is "C":
        gamut_type = rgbxy.GamutC
    else:
        gamut_type = rgbxy.GamutB

    color_conf = rgbxy.Converter(gamut=gamut_type)
    x, y = color_conf.rgb_to_xy(red, green, blue)
    return [x, y, 1]


def xy_bri_to_rgb(x, y, bri, gamut):
    """
    Convert CIE XY gamut position to rgb

    :param gamut: A, B or C; if other, Gamut B is used.
    :type gamut: str
    :param x: number – minimum: 0 – maximum: 1
    :type x: float
    :param y: number – minimum: 0 – maximum: 1
    :type y: float
    :param bri: 0-100 prct
    :type bri: int
    :return: [r, g, b] each 0-100%
    """

    if gamut is "A":
        gamut_type = rgbxy.GamutA
    elif gamut is "B":
        gamut_type = rgbxy.GamutB
    elif gamut is "C":
        gamut_type = rgbxy.GamutC
    else:
        gamut_type = rgbxy.GamutB

    color_conv = rgbxy.Converter(gamut=gamut_type)
    return color_conv.xy_to_rgb(x, y, bri)


def hex2int(msg):
    """

    :param msg: hex number (e.g. 0x11)
    :type msg: str
    :return: Int representation of hex value
    :rtype: int
    """
    if not msg:
        return 0

    msg = bytearray(msg)
    val = 0
    val = val | msg[0]
    for byte in msg[1:]:
        val = val << 8
        val = val | byte

    return int(val)


def get_val(json_data, key, do_xmlcharrefreplace=True):
    """

    :param json_data:
    :type json_data: dict
    :param key:
    :type key: str
    :param do_xmlcharrefreplace: True to perform an XML character replacement
    :type do_xmlcharrefreplace: bool
    :return: Requested value, str() in case of error
    """
    # type : (json, str, bool) -> Any

    val = str()

    if type(json_data) != dict:
        return val

    if key in json_data:
        val = json_data[key]
    if (type(val) == unicode) and do_xmlcharrefreplace:
        val = val.encode("ascii", "xmlcharrefreplace")
    return val


def get_data(ip, key, api_cmd, logger):
    """
    {'data': str(result), 'status': str(return code)}
    :param logger:
    :param api_cmd:
    :type api_cmd: str
    :param key:
    :type key: str
    :param ip:
    :type ip: str
    :return: {'data': Data received, 'status': html return code}
    :rtype: {str, str}
    """
    logger.debug("supp_fct.py | get_data | ip= '{}', key= '{}', api_cmd= '{}'".format(ip, key, api_cmd))
    api_path = 'https://{}/clip/v2/resource/{}'.format(ip, api_cmd)
    url_parsed = urlparse.urlparse(api_path)
    headers = {'Host': url_parsed.hostname, "hue-application-key": key}

    # Build a SSL Context to disable certificate verification.
    ctx = ssl._create_unverified_context()

    try:
        # Build a http request and overwrite host header with the original hostname.
        request = urllib2.Request(api_path, headers=headers)
        # Open the URL and read the response.
        response = urllib2.urlopen(request, data=None, timeout=5, context=ctx)
        data = {'data': response.read(), 'status': str(response.getcode())}
        logger.debug("supp_dct.py | get_data | Received {} byte with return code {}".format(len(data.get("data")),
                                                                                            data.get("status")))

        if int(data["status"]) != 200:
            logger.warning(
                "supp_dct.py | get_data | Hue bridge response code for '{cmd}' is {status}".format(cmd=api_cmd,
                                                                                                    status=data[
                                                                                                        "status"]))

    except Exception as e:
        data = {'data': str(e), 'status': str(0)}
        logger.error("supp_dct.py | get_data | For request '{cmd}' received '{error}', data: {data}".format(cmd=api_cmd,
                                                                                                     error=e,
                                                                                                     data=data))
    return data


def http_put(ip, key, device_rid, api_path, payload, logger):
    """

    :param ip:
    :param key:
    :param device_rid:
    :param api_path:
    :param payload:
    :param logger:
    :return:
    :rtype: dict
    """
    with TraceLog(logger):

        api_path = "https://" + ip + '/clip/v2/resource/' + api_path + "/" + device_rid
        url_parsed = urlparse.urlparse(api_path)
        headers = {"Host": url_parsed.hostname,
                   "Content-type": 'application/json',
                   "hue-application-key": str(key)}

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()

        try:
            # Build a http request and overwrite host header with the original hostname.
            request = urllib2.Request(api_path, headers=headers)
            request.get_method = lambda: 'PUT'
            # Open the URL and read the response.
            response = urllib2.urlopen(request, data=payload, timeout=5, context=ctx)
            data = {'data': response.read(), 'status': response.getcode()}
            logger.debug("Received code {code} for: {data}".format(data=data.get("data"), code=data.get("status")))

        except (urllib2.HTTPError, urllib2.URLError) as e:
            logger.error("In http_put #169, " + str(e) + " with " + "device_rid=" + device_rid +
                         "; api_path=" + api_path +
                         "; payload=" + str(payload))
            data = {'data': str(e), 'status': 0}
        except Exception as e:
            logger.error("In http_put #174, " + str(e) + " with " + "device_rid=" + device_rid +
                         "; api_path=" + api_path +
                         "; payload=" + str(payload))
            data = {'data': str(e), 'status': 0}

        if data["status"] != 200:
            try:
                json_data = json.loads(data["data"])
                if "errors" in json_data:
                    for msg_error in json_data["errors"]:
                        logger.error("In http_put #184, for {}, {} "
                                     "(http code {})".format(device_rid, get_val(msg_error, "description"),
                                                             data["status"]))
            except Exception as e:
                logger.error("In http_put #194, " + str(e))

        if data["status"] == 207:  # todo check if other behaviour makes more sense
            data["status"] = 200

        return data
