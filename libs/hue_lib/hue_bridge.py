import socket
import threading
import json
import urlparse
import select
import logging

import hue_lib.supp_fct as supp_fct
import hue_lib.hue_item as hue_item

BRIDGE_IP = str()  # type: str
BRIDGE_IP_LOCK = threading.RLock()
MCAST_PORT = 5353
MCAST_GRP = ('224.0.0.251', MCAST_PORT)


class HueBridge:

    # methods
    def __init__(self, logger):
        """
        Initialize the device object and store a reference to the logger.

        :param logger: The logger to use for logging messages.
        :type logger: logging.Logger
        """
        self.logger = logger
        self.rid = str()
        self.device = hue_item.HueDevice(self.logger)
        global devices
        try:
            len(devices)
        except NameError:
            devices = {}  # type: {str, hue_item.HueDevice}

    def get_bridge_ip(self, host_ip):
        """
        Function to return the globally stored Hue bridge IP. Thread save.
        Triggers a discovery for the bridge, if IP not set before.

        :type host_ip: str
        :return: ip
        :rtype: str
        """
        with supp_fct.TraceLog(self.logger):
            global BRIDGE_IP
            global BRIDGE_IP_LOCK

            if not BRIDGE_IP:
                ip = self.__discover_hue(host_ip)
                with BRIDGE_IP_LOCK:
                    BRIDGE_IP = ip

            return BRIDGE_IP

    def set_bridge_ip(self, ip):
        """
        Function to manually set the Hue bridge IP globally.
        Thread safe.

        :type ip: str
        :rtype: None
        """
        with supp_fct.TraceLog(self.logger):
            global BRIDGE_IP
            global BRIDGE_IP_LOCK

            with BRIDGE_IP_LOCK:
                BRIDGE_IP = ip

    def __discover_hue(self, host_ip):
        """
        Function to automatically discover the Hue bridge IP.
        Returns a tuple of status message and bridge IP.

        :type host_ip: str
        :param host_ip: IP of machine, hosting the logic module.
        :rtype: str, str
        :return: error message, ip
        """
        # best definition https://courses.cs.duke.edu/fall16/compsci356/DNS/DNS-primer.pdf
        msg_id = '\x00\x01'
        query = "\x01\x00"
        questions = "\x00\x01"
        answers = "\x00\x00"
        authority = '\x00\x00'
        additional = '\x00\x00'
        search = '\x04_hue\x04_tcp\x05local\x00'
        # query_type = '\x00\x01'  # A = a host address, https://www.rfc-editor.org/rfc/rfc1035
        query_type = '\x00\xff'  # * = All data available
        query_class = '\x00\x01'  # IN = the Internet, https://www.rfc-editor.org/rfc/rfc1035
        query_header = msg_id + query + questions + answers + authority + additional
        search = search + query_type + query_class
        query_msg = query_header + search

        # configure socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 8)
        sock.settimeout(8)
        sock.bind((host_ip, 0))  # host_ip = self.FRAMEWORK.get_homeserver_private_ip()

        # send data
        bytes_send = sock.sendto(query_msg, MCAST_GRP)
        if bytes_send != len(query_msg):
            self.logger.warning("Something wrong here, send bytes not equal provided bytes")

        while True:
            try:
                data = sock.recv(1024)

                self.logger.info("Discover result msg:\n{}".format(data.encode("ascii", "xmlcharrefreplace")))

                # check reply for "additional records", Type A, class IN contains IP4 address
                # header = data[:12]
                # qd_count = hex2int(data[4:6])
                # an_count = hex2int(data[6:8])
                # ns_count = hex2int(data[8:10])
                ar_count = supp_fct.hex2int(data[10:12])

                ans_idx = 12 + len(search)
                # ans_name = data[ans_idx:ans_idx + 2]
                # ans_type = data[ans_idx + 2:ans_idx + 4]
                # ans_class = data[ans_idx + 4:ans_idx + 6]
                # ans_ttl = data[ans_idx + 6:ans_idx + 10]
                ans_rd_length = supp_fct.hex2int(data[ans_idx + 10:ans_idx + 12])
                # ans_r_dara = data[ans_idx + 12:ans_idx + 12 + ans_rd_length]

                # answers = data[ans_idx:ans_idx + 12 + ans_rd_length]

                add_records = data[ans_idx + 12 + ans_rd_length:]

                # process additional records
                ar_offset = 0
                for i in range(ar_count):
                    # get record type (= A) and extrakt ip
                    ar_type = add_records[ar_offset + 2:ar_offset + 4]
                    # self.logger.debug(":".join("{:02x}".format(ord(c)) for c in ar_type))
                    ar_length = add_records[ar_offset + 10: ar_offset + 12]
                    ar_length = supp_fct.hex2int(ar_length)

                    if ar_type == "\x00\x01":  # Type A, get IP & Port
                        ar_ip = add_records[ar_offset + 12:ar_offset + 12 + ar_length]
                        ip1 = supp_fct.hex2int(ar_ip[0])
                        ip2 = supp_fct.hex2int(ar_ip[1])
                        ip3 = supp_fct.hex2int(ar_ip[2])
                        ip4 = supp_fct.hex2int(ar_ip[3])
                        ip = str(ip1) + "." + str(ip2) + "." + str(ip3) + "." + str(ip4)
                        ip = ".".join(str(supp_fct.hex2int(c)) for c in ar_ip)
                        self.logger.info("Discovered bridge at {}".format(ip))
                        self.set_bridge_ip(ip)
                        sock.close()
                        return ip

                    ar_offset = ar_offset + 12 + ar_length

            except socket.timeout:
                self.logger.error("No bridge discovered (timeout).")
                break

        sock.close()
        return str()

    def get_html_device_list(self):
        """
        Function to create an HTML page of all Hue devices and associated IDs.
        Should be used after register_devices function.

        :return: str
        """
        with supp_fct.TraceLog(self.logger):
            info_data = "<html>\n"
            info_data += "<style>" + CSS_STYLE + "</style>"
            info_data += "<title>Hue devices and associated IDs</title>"
            info_data += "<h1>Hue devices and associated IDs</h1>"
            info_data = (info_data + '<table border="1">\n' +
                         "<tr>" +
                         '<th class="sticky-header">Room Name</th>' +
                         '<th class="sticky-header">Name</th>' +
                         '<th class="sticky-header">Device</th>' +
                         '<th class="sticky-header">Light</th>' +
                         '<th class="sticky-header">Grouped Lights</th>' +
                         '<th class="sticky-header">Zigbee Connectivity</th>' +
                         '<th class="sticky-header">Room</th>' +
                         '<th class="sticky-header">Zone</th>' +
                         '<th class="sticky-header">Scenes</th>' +
                         "</tr>\n")

            global devices

            rooms = {}

            table_rows = str()
            for device in devices.values():
                table_rows += str(device)

                if device.room_name:
                    if device.room_name not in rooms:
                        rooms[device.room_name] = {}
                        rooms[device.room_name]["group_id"] = device.grouped_lights
                    else:
                        existing_list = rooms[device.room_name]["group_id"]
                        rooms[device.room_name]["group_id"] = list(set(existing_list) & set(device.grouped_lights))

                    rooms[device.room_name]["room_id"] = device.room

            for room_name in rooms.keys():
                room = rooms[room_name]
                group_id = room["group_id"][0]
                table_rows = (table_rows + "<tr>" +
                              "<td>{}</td>".format(room_name) +
                              "<td>-</td>" +
                              "<td>-</td>" +
                              "<td>-</td>" +
                              "<td>{}</td>".format(group_id) +
                              "<td>-</td>" +
                              "<td>{}</td>".format(room["room_id"]) +
                              "<td>-</td>" +
                              "<td>-</td>" +
                              "</tr>\n")

            sorted_rows = table_rows.split("</tr>\n")
            sorted_rows = sorted(sorted_rows)
            for row in sorted_rows:
                info_data += row + "</tr>\n"
            info_data += "</table>\n</html>\n"

            return info_data

    def __register_device_type(self, data):
        global devices
        for item in data:
            item_id = supp_fct.get_val(item, "id")

            services = supp_fct.get_val(item, "services")
            device = hue_item.HueDevice(self.logger)
            device.device_id = item_id
            metadata = supp_fct.get_val(item, "metadata")
            device.name = supp_fct.get_val(metadata, "name")

            for service in services:
                rid = supp_fct.get_val(service, "rid")

                rtype = supp_fct.get_val(service, "rtype")
                if rtype == "light":
                    device.light_id = rid
                elif rtype == "zigbee_connectivity":
                    device.zigbee_connectivity_id = rid

            devices[device.device_id] = device

    def __register_room_type(self, data):
        with supp_fct.TraceLog(self.logger):
            global devices
            for item in data:
                item_id = supp_fct.get_val(item, "id")
                children = supp_fct.get_val(item, "children")
                metadata = supp_fct.get_val(item, "metadata")
                room_name = supp_fct.get_val(metadata, "name")
                for i in range(len(children)):
                    rid = supp_fct.get_val(children[i], "rid")
                    rtype = supp_fct.get_val(children[i], "rtype")

                    if rtype == "device":
                        if rid in devices:
                            device = devices[rid]
                            device.room = item_id
                            device.room_name = room_name
                            devices[device.device_id] = device
                        else:
                            self.logger.debug(
                                "In register_devices #414, device not registered as device but requested by "
                                "'room': '" + rid + "'")

    def __register_zone_type(self, data):
        """
        Register a zone type for devices with the provided data.

        :param data: A list of dictionaries representing zone and device information.
        :type data: List[Dict[str, Any]]
        :returns: None
        :rtype: None
        """
        with supp_fct.TraceLog(self.logger):
            global devices
            for item in data:
                item_id = supp_fct.get_val(item, "id")
                children = supp_fct.get_val(item, "children")
                for child in children:
                    rid = supp_fct.get_val(child, "rid")
                    rtype = supp_fct.get_val(child, "rtype")

                    if rtype == "light":
                        for device in devices.values():
                            if device.light_id == rid:
                                device.zone = item_id
                                devices[device.device_id] = device

    def __register_scene_type(self, data):
        with supp_fct.TraceLog(self.logger):
            global devices
            for item in data:
                item_id = supp_fct.get_val(item, "id")
                group = supp_fct.get_val(item, "group")
                rid = supp_fct.get_val(group, "rid")
                rtype = supp_fct.get_val(group, "rtype")
                metadata = supp_fct.get_val(item, "metadata")
                scene_name = supp_fct.get_val(metadata, "name")

                if rtype == "zone":
                    for device in devices.values():
                        if device.zone == rid:
                            scene_entry = {"name": scene_name, "id": item_id}
                            device.scenes.append(scene_entry)
                            devices[device.device_id] = device

                elif rtype == "room":
                    for device in devices.values():
                        if device.room == rid:
                            scene_entry = {"name": scene_name, "id": item_id}
                            device.scenes.append(scene_entry)
                            devices[device.device_id] = device

    def __register_grouped_light_type(self, data):
        global devices
        for item in data:
            item_id = supp_fct.get_val(item, "id")
            owner = supp_fct.get_val(item, "owner")
            rid = supp_fct.get_val(owner, "rid")
            rtype = supp_fct.get_val(owner, "rtype")

            for device in devices.values():
                if rtype == "room":
                    if device.room == rid:
                        device.grouped_lights.append(item_id)
                        devices[device.device_id] = device
                elif rtype == "zone":
                    if device.zone == rid:
                        device.grouped_lights.append(item_id)
                        devices[device.device_id] = device

    def register_devices(self, key, rid, host_ip):
        """
        Goal 1: Build html tabel containing all IDs and associated service IDs
        Goal 2: Build object list containing all hue devices and associated service infos / ISs
        Goal 3: Get all alias IDs for own ID

        Returns the number of registered devices

        :param host_ip:
        :type host_ip: str
        :type key: str
        :param key: Hue bridge access key
        :type rid: str
        :param rid: ID of Hue device managed by the logic module
        :return: int
        """
        with supp_fct.TraceLog(self.logger):
            item_types = ["device", "room", "zone", "scene", "grouped_light"]

            # start to store info of devices
            global devices
            devices = {}
            self.rid = rid  # type: str

            for item_type in item_types:

                # 1. get all text data from each item type from bridge
                data_raw = supp_fct.get_data(self.get_bridge_ip(host_ip), key, item_type, self.logger)  # type: dict

                try:
                    data = json.loads(data_raw["data"])  # type: dict
                except Exception as e:
                    self.logger.error("hue_bridge.py | register_devices({key}, {rid}, {host}) | "
                                      "Caught exception '{msg}'".format(key=key, rid=rid, host=host_ip, msg=e))
                    continue

                data = supp_fct.get_val(data, "data")

                if item_type == "device":
                    self.__register_device_type(data)
                elif item_type == "room":
                    self.__register_room_type(data)
                elif item_type == "zone":
                    self.__register_zone_type(data)
                elif item_type == "scene":
                    self.__register_scene_type(data)
                elif item_type == "grouped_light":
                    self.__register_grouped_light_type(data)

            return len(devices)

    def get_own_device(self, rid):
        """
        Function to return a device with a given ID *or* associated ID

        :type rid: str
        :param rid:
        :rtype: hue_item.HueDevice
        :return: Device
        """
        global devices

        # check if identified before
        if rid in self.device.get_device_ids(True):
            if rid != self.device.id:
                self.logger.debug("hue_bridge.py | get_own_device({}) | Restorig device".format(rid))
                self.device.id = rid
                self.device.get_type_of_device()
            return self.device

        # search and store own device if not identified before
        else:
            for device in devices.values():
                if rid in device.get_device_ids(True):
                    self.logger.debug("hue_bridge.py | get_own_device({}) | Registering device".format(rid))
                    self.device = device
                    self.device.id = rid
                    self.device.get_type_of_device()
                    break

        if not self.device.id:
            error_msg = ("hue_bridge.py | get_own_device('{rid}') | Requested device not found!".format(rid=rid))
            self.logger.error(error_msg)
            assert error_msg

        return self.device

    def connect_to_eventstream(self, conn, host_ip, key):
        with supp_fct.TraceLog(self.logger):
            hue_bridge_ip = self.get_bridge_ip(host_ip)
            api_path = 'https://' + hue_bridge_ip + '/eventstream/clip/v2'
            url_parsed = urlparse.urlparse(api_path)

            conn.bind(('', 0))
            try:
                conn.connect((hue_bridge_ip, 443))
            except socket.error as e:
                if e.errno == 10035:
                    pass
                else:
                    raise

            while True:
                ready = select.select([], [conn], [], 5)
                if ready[1]:
                    error = conn.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                    if error == 0:
                        break
                    else:
                        raise socket.error(error, 'Connect error')
                else:
                    raise socket.error('Timeout while connecting')

            try:
                conn.send("GET /eventstream/clip/v2 HTTP/1.1\r\n")
                conn.send("Host: " + url_parsed.hostname + "\r\n")
                conn.send("hue-application-key: " + key + "\r\n")
                conn.send("Accept: text/event-stream\r\n\r\n")
                self.logger.info("Connected to eventstream")
                return True
            except socket.socket as e:
                conn.close()
                self.logger.error("Error connecting  to eventstream.")
                return False


CSS_STYLE = '''/*** *********************** ***/
/*** ***** ALLGEMEINES ***** ***/
/*** *********************** ***/
body { width:97%; max-width:950px;
       font-size:1.0em; font-weight:normal; font-family:Verdana, Arial; padding-left:8px;
       background: url(company.png) no-repeat; background-position: 1em 1em;
     }
.mono { font-family: monospace }
/*** Text-Formatierungen ***/
.small    { font-size:0.7em; }
.normal   { font-size:1.0em; }
.big      { font-size:1.3em; }
.center   { text-align:center; }
.left     { text-align:left; }
.right    { text-align:right; }
/*** Links ***/
a:link    { color:#0000ff; }
a:visited { color:#990099; }
a:hover   { color:#ff0000; }
/*** *********************** ***/
/*** ***** Klappmenues ***** ***/
/*** *********************** ***/
.xcheckbox { display: none; }
.button-simu { color: #0060f6; cursor: pointer;  }
label:hover { color: #ffb400; }
.folded div a { text-decoration: none; }
.folded div a:hover { color: #ffb400; }
.vanish-block-4 { display: none; }
input[type="checkbox"]:checked ~ .vanish-block-4 { display: block; margin-bottom: 20px; margin-left: 27px; }
.vanish-block-5 { display: none; }
input[type="checkbox"]:checked ~ .vanish-block-5 { display: block; margin-bottom: 20px; margin-left: 27px; }
.vanish-block-6 { display: none; }
input[type="checkbox"]:checked ~ .vanish-block-6 { display: block; margin-bottom: 20px; margin-left: 27px; }
.vanish-block-7 { display: none; }
input[type="checkbox"]:checked ~ .vanish-block-7 { display: block; margin-bottom: 20px; margin-left: 27px; }
.vanish-block-8 { display: none; }
input[type="checkbox"]:checked ~ .vanish-block-8 { display: block; margin-bottom: 20px; margin-left: 27px; }
.vanish-block-1 { display: block; margin-bottom: 20px; margin-left: 27px; }
input[type="checkbox"]:checked ~ .vanish-block-1 { display: none; }
.vanish-block-2 { display: block; margin-bottom: 20px; margin-left: 27px; }
input[type="checkbox"]:checked ~ .vanish-block-2 { display: none; }
.vanish-block-3 { display: block; margin-bottom: 20px; margin-left: 27px;  }
input[type="checkbox"]:checked ~ .vanish-block-3 { display: none; }
/*** ************************************* ***/
/*** ***** Spezielles fuer Dokumente ***** ***/
/*** ************************************* ***/
/*** Layout der "ersten Seite" mit Hintergrund-Bild ***/
.fp-layout { width:100%; max-width:950px;
             background: url(company_doc.png) no-repeat; background-position: 100% 50%;
           }
/*** Farben fuer Texte ***/
.green  { color:#00FF21; }
.darkgreen  { color:#009900; }
.orange { color:#FF6A00; }
.red    { color:#FF0000; }
.blue   { color:#0000FF; }
.yellow { color:#FFD800; }
/*** Farben fuer Hintergruende ***/
.bg-yellow { background-color:yellow;  }
.bg-green  { background-color:#e8fde9; }
.bg-orange { background-color:#ffb27f; }
.bg-red    { background-color:#ff7f7f; }
.bg-blue   { background-color:#ebfdfe; }
/*** ************************** ***/
/*** ***** UEBERSCHRIFTEN ***** ***/
/*** ************************** ***/
/*** Ueberschriften ***/
h1, h2, h3, h4, h5, h6 { margin-left:0px; font-weight:bold; }
h1 { font-size:1.5em; margin-top:0.8em; margin-bottom:0.5em; }
h2 { font-size:1.2em; margin-top:0.7em; margin-bottom:0.4em; }
h3 { font-size:1.2em; margin-top:0.6em; margin-bottom:0.3em; font-style:italic; }
h4 { font-size:1.2em; margin-top:0.6em; margin-bottom:0.3em; font-style:italic; font-weight:normal; }
h5 { font-size:1.2em; margin-top:0.5em; margin-bottom:0.2em; font-style:italic; font-weight:normal; color:#707070; }
h6 { font-size:1.0em; margin-top:0.5em; margin-bottom:0.2em; font-style:italic; font-weight:normal; color:#707070; }
/*** ************************* ***/
/*** ***** TEXT-ELEMENTE ***** ***/
/*** ************************* ***/
/*** Titel des Dokuments ***/
.top-title     { margin-bottom:10px; margin-top:11px; margin-right:0.7em;  margin-left:100px;
                 text-align:right; font-size:1.0em;  font-size:1.5em; font-weight:bold; }
/*** Navigations-Zeile ***/
.nav           { margin-bottom:0.5em; }
/*** Inhaltsverzeichnis ***/
.index         { margin-top:1em; margin-bottom:1.5em;  font-size: 1.2em; }
.index-title   { margin-bottom: 1em; font-weight: bold; }
/*** Zeilen im Inhaltsverzeichnis / Ueberschriften-Elemente ***/
.t-line        {  margin-bottom: 0.3em; }
.t-chapter     { float:left; min-width:60px; padding-right:0.7em; }
.t-text        {  }
/*** Den Inhalt (Alles ab dem Inhaltsverzeichnis (exkl.) umschliessende Container <div>  ***/
.content       {  }
/*** Container fuer Bereiche ***/
.topic         {  }
/*** Description (Einleitungstext) ***/
.descr         { margin-bottom:1.0em; margin-top:1.5em; }
.descr-no-tit  { margin-bottom:1.5em; margin-top:1.5em; }
/*** Field ***/
.field           { margin-bottom:1.5em; }
.field-title     { font-style:normal; font-size:0.8em; font-weight: bold; }
.field-title-red { font-style:normal; font-size:0.8em; font-weight: bold; color:red; }
.xhtml         {  }
/*** ************************** ***/
/*** ***** MELDUNGS-BOXEN ***** ***/
/*** ************************** ***/
.alert-box     { font-size: 1.0em; font-weight: normal;
                 padding-top: 0.5em; padding-left: 0.2em;
                 margin-bottom: 1.0em; margin-top: 1.0em;
                 border-spacing:0; border-collapse: collapse;
                 border: 2px solid #BABABA;
                 width:100%; max-width:950px; background-color:#ffff00; }
.ibox-hint     { background: url(ibox-h.png) no-repeat; background-position: 0.4em 0.4em; }
.ibox-note     { background: url(ibox-n.png) no-repeat; background-position: 0.4em 0.4em; }
.ibox-warn     { background: url(ibox-w.png) no-repeat; background-position: 0.4em 0.4em; }
.box-title     { font-weight:bold;
                 padding-left:2.5em; padding-bottom:0px;
                 margin-left:1em; margin-bottom:20px; margin-top:10px;
               }
.box-text      { clear:both; padding-bottom:0.5em; padding-top:0px; margin-top:0px; }
.box-text .descr { margin-top:12px; }
/*** ******************************** ***/
/*** ****** SPRACH-AUSWAHL-BOX ****** ***/
/*** ******************************** ***/
.sel_lbl      {  }
.sel_box      { padding-left:1em; margin-left:1em; }
/*** ******************** ***/
/*** ****** LISTEN ****** ***/
/*** ******************** ***/
/*** Liste mit groesseren Abstaenden zwischen den Listeneintraegen ***/
.big-list li   {margin-bottom: 0.3em; margin-top: 0.3em; }
/*** Nummerierte Listen ***/
ol.lalpha       {list-style-type: lower-alpha; }
ol.ualpha       {list-style-type: upper-alpha; }
/*** ******************** ***/
/*** ***** TABELLEN ***** ***/
/*** ******************** ***/
.small-rows td  {padding:0px; }
/*** ********** Tabellen, allgemein ********** ***/
table              { border-spacing:0; border-collapse:collapse;
                     padding-left:8px; margin-top:0.5em; margin-bottom:0.5em;
                     font-size:1.0em;
                     width:100%; max-width:950px; }
table td, table th { border:1px solid #aaa; vertical-align:top; text-align:left; font-size:0.9em; padding:10px; }
th.sticky-header {
  position: sticky;
  top: 0;
  z-index: 10;
  /*To not have transparent background.
  background-color: white;*/
}
table th           { font-weight:bold;  background-color:#eee; font-size:0.9em; }
/*** ********** Spezielle Tabellen-Formatierungen ********** ***/
.table-no-border         { padding-bottom:0em; padding-top:0em; margin-bottom:0em; margin-top:0em; }
.table-standard          { background-color:white }
.table-green             { background-color:#e8fde9; }
.table-blue              { background-color:#ebfdfe; }
/*** *** Tabelle OHNE Rahmen! (z.B. Logikbaustein Sonstiges) *** ***/
.table-no-border td  { border:0px; }
.table-no-border th  { border:0px;  background-color:transparent; }
/*** ************************************************************** ***/
/*** ********** EINGAENGE und AUSGAENGE (Logikbausteine) ********** ***/
/*** ************************************************************** ***/
/*** Tabellen fuer Eingaenge und Ausgaenge der Logik-Bausteine ***/
.table-in  {  }
.table-out {  }
/*** Farben fuer Eingaenge und Ausgaenge, wie im GLE. Eigener Style, weil es evtl. mal OHNE Tabelle gebraucht werden koennte ***/
.input       { background-color:#80ff80; }
.output      { background-color:#ff8080; }
.string      { background-color:#E0E0E0; }
/*** Spalten der Eingangs- und Ausgangs- Tabellen ***/
.io-nr       { width:30px; }
.io-name     { width:150px; max-width:150px; word-wrap:break-word; }
.io-init     { width:100px; max-width:100px; word-wrap:break-word; }
.o-sbc       { width:49px; }
/*** Formatierungen fuer die einzelnen Spalten der Eingangs-Tabellen ***/
/*** Header ***/
.table-in  th.io-nr      {  }
.table-in  th.io-name    {  }
.table-in  th.io-init    {  }
.table-in  th.io-descr   {  }
/*** Zellen ***/
.table-in  td.io-nr      {  }
.table-in  td.io-name    {  }
.table-in  td.io-init    {  }
.table-in  td.io-descr   {  }
.table-in  .descr        { margin-bottom:0px; margin-top:0px; }
/*** Formatierungen fuer die einzelnen Spalten der Ausgangs-Tabellen ***/
/*** Header ***/
.table-out  th.io-nr     {  }
.table-out  th.io-name   {  }
.table-out  th.io-init   {  }
.table-out  th.o-sbc     {  }
.table-out  th.io-descr  {  }
/*** Zellen ***/
.table-out td.io-nr      {  }
.table-out td.io-name    {  }
.table-out td.io-init    {  }
.table-out td.o-sbc      {  }
.table-out td.io-descr   {  }
.table-out .descr        { margin-bottom:0px; margin-top:0px; }
/*** ************************************** ***/
/*** ***** SONSTIGES (Logikbausteine) ***** ***/
/*** ************************************** ***/
.table-logic-info        { padding-bottom:0em; padding-top:0em; margin-bottom:0em; margin-top:0em; }
.table-logic-info th     { border:0px; font-weight:normal; background-color:white; width:200px; }
.table-logic-info td     { border:0px;  }
/*** ************************************************* ***/
/*** ***** AEHNLICHE FUNKTIONEN (Logikbausteine) ***** ***/
/*** ************************************************* ***/
.t-sim-func   {  }
.t-sf-grptit  { font-weight:bold; margin-top:1.5em; margin-bottom:0.3em; }
.t-sf-grpitm  { font-size:0.9em; }
'''
