import unittest
import logging
import json
import socket
import hue_bridge


TRACE = 5


class TestModuleRegistration(unittest.TestCase):
    class FunctionHandler(logging.Handler):
        def __init__(self):
            super(TestModuleRegistration.FunctionHandler, self).__init__()

        def emit(self, record):
            print("{level}:{msg}".format(msg=record.getMessage(), level=record.levelname))

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.addLevelName(TRACE, "TRACE")

        def trace(self, message, *args, **kws):
            if self.isEnabledFor(TRACE):
                self._log(TRACE, message, args, **kws)

        logging.Logger.trace = trace

        handler = self.FunctionHandler()
        self.logger.addHandler(handler)

        self.logger.setLevel(logging.DEBUG)

        with open("credentials.json") as f:
            self.cred = json.load(f)
            self.bridge_ip = self.cred["PIN_I_SHUEIP"]
            self.key = self.cred["PIN_I_SUSER"]
            self.device_id = self.cred["hue_device_id"]

        hostname = socket.gethostname()
        self.ip = socket.gethostbyname(hostname)
        self.bridge = hue_bridge.HueBridge(self.logger)

    def tearDown(self):
        pass

    def test_get_bridge_ip(self):
        self.assertFalse(hue_bridge.BRIDGE_IP, "#1")
        bridge_ip = self.bridge.get_bridge_ip(self.ip)
        self.assertTrue(bridge_ip, "#2")
        self.assertTrue("192." in bridge_ip, "#3 Expected '192.' but got {}".format(bridge_ip))
        self.assertTrue("192." in hue_bridge.BRIDGE_IP, "#4 Expected '192.' but got {}".format(bridge_ip))
        hue_bridge.BRIDGE_IP = "123"

        # check singleton characteristics
        bridge2 = hue_bridge.HueBridge(self.logger)
        bridge_ip = bridge2.get_bridge_ip(self.ip)
        self.assertTrue("123" is bridge_ip, "#5")

        bridge2.set_bridge_ip("345")
        bridge_ip = self.bridge.get_bridge_ip(self.ip)
        self.assertTrue("345" is bridge_ip, "#6")

    def test_set_bridge_ip(self):
        ip = "no ip here"
        res = self.bridge.get_bridge_ip(self.ip)
        self.assertNotEqual(ip, res)

        self.bridge.set_bridge_ip(ip)
        res = self.bridge.get_bridge_ip(self.ip)
        self.assertEqual(ip, res)

    def test_get_html_device_list(self):
        self.bridge.set_bridge_ip(self.bridge_ip)
        amount = self.bridge.register_devices(self.key, self.device_id, self.ip)
        self.assertTrue(amount > 0)

        html_page = self.bridge.get_html_device_list()
        with open("debug_server_return.html", 'w') as out_file:
            out_file.write(html_page)

        self.assertTrue(len(html_page) > 0)
        self.assertTrue(self.device_id in html_page)


if __name__ == '__main__':
    unittest.main()
