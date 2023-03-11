import unittest
import logging
import json

import hue_bridge


TRACE = 5


class TestModuleRegistration(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        logging.addLevelName(TRACE, "TRACE")

        def trace(self, message, *args, **kws):
            if self.isEnabledFor(TRACE):
                self._log(TRACE, message, args, **kws)

        logging.Logger.trace = trace

        with open("credentials.json") as f:
            self.cred = json.load(f)
            self.ip = self.cred["my_ip2"]

        self.bridge = hue_bridge.HueBridge(self.logger)

    def tearDown(self):
        pass

    def test_get_bridge_ip(self):
        self.assertFalse(hue_bridge.BRIDGE_IP)
        bridge_ip = self.bridge.get_bridge_ip(self.ip)
        self.assertTrue("192." in bridge_ip, "Expected '192.' but got {}".format(bridge_ip))
        self.assertTrue("192." in hue_bridge.BRIDGE_IP, "Expected '192.' but got {}".format(bridge_ip))
        hue_bridge.BRIDGE_IP = "123"

        # check singleton characteristics
        bridge2 = hue_bridge.HueBridge(self.logger)
        bridge_ip = bridge2.get_bridge_ip(self.ip)
        self.assertTrue("123" is bridge_ip)

        bridge2.set_bridge_ip("345")
        bridge_ip = self.bridge.get_bridge_ip(self.ip)
        self.assertTrue("345" is bridge_ip)


if __name__ == '__main__':
    unittest.main()
