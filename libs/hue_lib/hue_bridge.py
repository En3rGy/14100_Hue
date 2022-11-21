import socket
import threading
import json
import time

import hue_lib.supp_fct as supp_fct
import hue_lib.hue_item as hue_item


def get_bridge_ip(host_ip):
    """
    Function to return the globally stored Hue bridge IP. Thread save.
    Triggers a discovery for the bridge, if IP not set before.

    :return: str
    """

    global bridge_ip  # type: str
    global bridge_ip_lock

    try:
        bridge_ip_lock.locked()
    except NameError:
        bridge_ip_lock = threading.Lock()
    finally:
        bridge_ip_lock.acquire()

    try:
        if bridge_ip:
            pass
    except NameError:
        bridge_ip = str()

    if not bridge_ip:
        try:
            bridge_ip_lock.release()
            discover_hue(host_ip)
        except NameError:
            bridge_ip = str()

    ip = bridge_ip
    if bridge_ip_lock.locked():
        bridge_ip_lock.release()
    return ip


def set_bridge_ip(ip):
    """
    Function to manually set the Hue bridge IP globally.
    Thread safe.

    :type ip: str
    :rtype: None
    """
    global bridge_ip  # type: str
    global bridge_ip_lock

    try:
        bridge_ip_lock.locked()
    except NameError:
        bridge_ip_lock = threading.Lock()
    finally:
        loop = 0
        while True:
            if not bridge_ip_lock.locked():
                bridge_ip_lock.acquire()
                break
            else:
                time.sleep(2)
            loop = loop + 1
            if loop > 2:
                return

    bridge_ip = ip
    bridge_ip_lock.release()


def discover_hue(host_ip):
    """
    Function to automatically discover the Hue bridge IP.
    Returns a tuple of status message and bridge IP.

    :type host_ip: str
    :param host_ip: IP of machine, hosting the logic module.
    :return: str, str
    """
    supp_fct.log_debug("entering hue_bridge.discover_hue, host_ip = " + host_ip)

    err_msg = str()

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
    mcast_port = 5353
    mcast_grp = ('224.0.0.251', mcast_port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 8)

    sock.settimeout(8)

    sock.bind((host_ip, 0))  # host_ip = self.FRAMEWORK.get_homeserver_private_ip()

    # send data
    try:
        bytes_send = sock.sendto(query_msg, mcast_grp)
        if bytes_send != len(query_msg):
            err_msg = "Something wrong here"
    except socket.error as e:
        err_msg = "Socket Error discover: " + str(e)
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
    except Exception as e:
        err_msg = "Error discover: " + str(e)
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

    while True:
        try:
            data = sock.recv(1024)
            # sock.shutdown(socket.SHUT_RDWR)

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
            ans_rd_length = data[ans_idx + 10:ans_idx + 12]
            ans_rd_length = supp_fct.hex2int(ans_rd_length)
            # ans_r_dara = data[ans_idx + 12:ans_idx + 12 + ans_rd_length]

            # answers = data[ans_idx:ans_idx + 12 + ans_rd_length]

            add_rec_idx = ans_idx + 12 + ans_rd_length
            add_records = data[add_rec_idx:]

            # process additional records
            ar_offset = 0
            for i in range(ar_count):
                # get record type (= A) and extrakt ip
                ar_type = add_records[ar_offset + 2:ar_offset + 4]
                # print(":".join("{:02x}".format(ord(c)) for c in ar_type))
                ar_length = add_records[ar_offset + 10: ar_offset + 12]
                ar_length = supp_fct.hex2int(ar_length)

                if ar_type == "\x00\x01":  # Type A, get IP & Port
                    ar_ip = add_records[ar_offset + 12:ar_offset + 12 + ar_length]
                    ip1 = supp_fct.hex2int(ar_ip[0])
                    ip2 = supp_fct.hex2int(ar_ip[1])
                    ip3 = supp_fct.hex2int(ar_ip[2])
                    ip4 = supp_fct.hex2int(ar_ip[3])

                    ip = str(ip1) + "." + str(ip2) + "." + str(ip3) + "." + str(ip4)
                    err_msg = "Bridge IP (auto) is " + ip
                    set_bridge_ip(ip)
                    return err_msg, ip

                ar_offset = ar_offset + 12 + ar_length

        except socket.timeout:
            err_msg = "Discovery timeout"
            break

    sock.close()
    return err_msg, str()


class HueBridge:

    # methods
    def __init__(self):
        self.rid = str()
        self.device = hue_item.HueDevice()
        global devices
        try:
            len(devices)
        except NameError:
            devices = {}  # type: {str, hue_item.HueDevice}


    def get_html_device_list(self):
        """
        Function to create an HTML page of all Hue devices and associated IDs.
        Should be used after register_devices function.

        :return: str
        """
        info_data = "<html>\n"
        info_data = info_data + "<style>"
        info_data = info_data + get_css() + "</style>"
        info_data = info_data + "<title>Hue devices and associated IDs</title>"
        info_data = info_data + "<h1>Hue devices and associated IDs</h1>"
        info_data = (info_data + '<table border="1">\n' +
                     "<tr>" +
                     "<th>Room Name</th>" +
                     "<th>Name</th>" +
                     "<th>Device</th>" +
                     "<th>Light</th>" +
                     "<th>Grouped Lights</th>" +
                     "<th>Zigbee Connectivity</th>" +
                     "<th>Room</th>" +
                     "<th>Zone</th>" +
                     "<th>Scenes</th>" +
                     "</tr>\n")

        global devices

        for device in devices.values():
            info_data = info_data + str(device)

        info_data = info_data + "</table>\n</html>\n"

        return info_data

    def __register_device_type(self, data):
        global devices
        for item in data:
            item_id = supp_fct.get_val(item, "id")

            services = supp_fct.get_val(item, "services")
            device = hue_item.HueDevice()
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
                        supp_fct.log_debug(
                            "In register_devices #414, device not registered as device but requested by "
                            "'room': '" + rid + "'")

    def __register_zone_type(self, data):
        global devices
        for item in data:
            item_id = supp_fct.get_val(item, "id")
            children = supp_fct.get_val(item, "children")
            for i in range(len(children)):
                rid = supp_fct.get_val(children[i], "rid")
                rtype = supp_fct.get_val(children[i], "rtype")

                if rtype == "light":
                    for device in devices.values():
                        if device.light_id == rid:
                            device.zone = item_id
                            devices[device.device_id] = device

    def __register_scene_type(self, data):
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

        item_types = ["device", "room", "zone", "scene", "grouped_light"]

        # start to store info of devices
        global devices
        devices = {}
        self.rid = rid  # type: str

        for item_type in item_types:

            # 1. get all text data from each item type from bridge
            data_raw = supp_fct.get_data(get_bridge_ip(host_ip), key, item_type)  # type: str

            try:
                data = json.loads(data_raw["data"])  # type: {}
            except Exception as e:
                supp_fct.log_debug("In register_devices #377, " + str(e))
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

        supp_fct.log_debug("In register_devices #466, registered " + str(len(devices)) + " devices")

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
        if rid in self.device.get_device_ids():
            if rid != self.device.id:
                self.device.id = rid
                self.device.get_type_of_device()
            return self.device

        # search and store own device if not identified before
        else:
            for device in devices.values():
                if rid in device.get_device_ids():
                    self.device = device
                    self.device.id = rid
                    self.device.get_type_of_device()
                    break

        if self.device is None:
            supp_fct.log_debug("Requested device not found")

        return self.device

def get_css():
    css = '''/*** *********************** ***/
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

    return css
