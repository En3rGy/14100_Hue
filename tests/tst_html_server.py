import unittest
import html_server
import logging
import json
import time
import urlparse
import urllib2


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

    def tearDown(self):
        pass

    def test_08_server(self):
        server = html_server.HtmlServer(self.logger)
        server.run_server(self.ip, 8080)

        text = "Hello World!"
        server.set_html_content(text)

        time.sleep(1)

        api_path = 'http://{}:8080'.format(self.ip)
        url_parsed = urlparse.urlparse(api_path)
        headers = {'Host': url_parsed.hostname}
        request = urllib2.Request(api_path, headers=headers)
        response = urllib2.urlopen(request, data=None, timeout=5)
        data = response.read()

        self.assertEqual(response.getcode(), 200)
        self.assertEqual(data, text)

        # test stop server
        server.stop_server()

        try:
            response = urllib2.urlopen(request, data=None, timeout=5)
        except urllib2.URLError as e:
            pass  # everything ok, because error should be raised if server is down
        else:
            self.assertTrue(False, "Expected connection failure because server should not be running")


if __name__ == '__main__':
    unittest.main()

