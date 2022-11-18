import hue_lib.supp_fct as supp_fcn
import threading
import BaseHTTPServer
import SocketServer

import supp_fct


class HtmlServer:

    # methods
    def __init__(self):
        self.server = ""
        self.t = ""
        self.http_request_handler = MyHttpRequestHandler

    def run_server(self, ip, port):
        """
        Start the server providing the info page with Hue IDs.

        :type ip: str
        :param ip: IP of machine hosting the server
        :type port: int
        :param port: Port used to provide the info page
        :rtype: None
        :return: No implemented
        """
        supp_fcn.log_debug("entering run_server, ip = " + str(ip) + ", port = " + str(port))
        server_address = (ip, port)

        self.stop_server()

        try:
            self.server = ThreadedTCPServer(server_address, self.http_request_handler, bind_and_activate=False)
            self.server.allow_reuse_address = True
            self.server.server_bind()
            self.server.server_activate()
        except Exception as e:
            supp_fcn.log_debug(str(e))
            return

        ip, port = self.server.server_address
        self.t = threading.Thread(target=self.server.serve_forever)
        self.t.setDaemon(True)
        self.t.start()
        server_url = "http://" + str(ip) + ":" + str(port)
        supp_fcn.log_debug('Server running on <a href="' + server_url + '">' + server_url + '</a>')

    def stop_server(self):
        """
        Stop server which provides info page
        """
        supp_fct.log_debug("Entering html_server.HTMLServer.stop_server")
        try:
            self.server.shutdown()
            self.server.server_close()
        except AttributeError:
            pass
        except Exception as e:
            supp_fcn.log_debug("html_server.HTMLServer.stop_server: " + str(e))
        finally:
            pass

    def set_html_content(self, content):
        """

        :param content: str
        :return: None
        """
        with self.http_request_handler.data_lock:
            self.http_request_handler.response_content_type = "text"
            self.http_request_handler.response_data = content


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


# class MyHttpRequestHandler(SocketServer.BaseRequestHandler):
class MyHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    data_lock = threading.RLock()

    def __init__(self, request, client_address, server):
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.response_content_type = ""
        self.response_data = ""

    def do_GET(self):
        with self.data_lock:
            self.send_response(200)
            self.send_header('Content-type', self.response_content_type)
            self.end_headers()

            self.wfile.write(self.response_data)
