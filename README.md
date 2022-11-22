# 14100 Hue Group

## Description 

The logic module provides an interface to specific Hue lights, groups, rooms, zones, etc. Registered devices can be 
controlled and the device status is provided via the modules output. The module registers itself at the hue bridge 
using the Hue [Hue API v2](https://developers.meethue.com/develop/hue-api-v2/) and the _eventstream_ function. Using 
multiple instances of the logic module, just one will register for the _eventstream_ and provides received date to the 
other ones.

One module provides an auto discovery on the Hue bridge in order to receive the bridges IP address. A HS reboot is
necessary, if the bridge IP chances!

All outputs are configured as _send-by-change (sbc)_.

### Useage
- [Hue API v2](https://developers.meethue.com/develop/hue-api-v2/) addresses each device using a non-readable ID.<br>
This ID must be provided to the logic module instance of the corresponding Hue device (1 Hue Device : 1 Logic Module 
 Instance).<br>
In oder to identify the Hue ID of a specific device, one logic module creates a webpage showing the IDs and the 
corresponding rooms and device names. The link to this page is shown on the debug page in the logic modules section 
within the _HSL 2.0_ section.<br>
**Create at least one instance of the logic module and identify the Hue IDs of the devices you would like to control.**
- Set up an instance of the logic module for each hue item you would like to control or monitor the status.<br>
**In general, use the `light` or `grouped light` ID.**

## Inputs

| Nr. | Name                 | Init. | Description                                                                                                                                                      |
|-----|----------------------|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | Get Status           |       | A value =1 reads (manually) the full status of the device from the bridge                                                                                        |
| 2   | Key                  |       | Hue Bridge User Key                                                                                                                                              |
| 3   | Port Info Page       | 0     | Port of Information Website: Website containing all Hue devices and the corresponding or associated Hue IDs. The web site is provided at `http://<HS-IP>:<Port>` |
| 4   | Item Id              | 0     | ID of Hue device to be controlled. The device ID can be identified via the Information Website described in the description / Usage section                      |
| 5   | Scene ID             |       | ID of the scene to be called. Providing a valid scene ID on this input will switch on the device also.                                                           | 
| 6   | Dynamic scene On/Off | 0     | Activates the scene of Input 5 as "dynamic scene"                                                                                                                |
| 7   | Dyn. scene speed     | 0.7   | Speed of dynamic palette for the sceen given on input 5 and activated as "dynamic" on input 6 (0-1)                                                              |
| 5   | On/Off (1/0)         | 0     | Switches on (1) / off (0) the Hue device.                                                                                                                        |
| 6   | Brightness (%)       | 0     | Brightness in 0-100% <br/> Device will be switched on if value is set                                                                                            |
| 7   | r                    | 0     | RGB red (0-100%)                                                                                                                                                 |
| 8   | g                    | 0     | RGB green (0-100%)                                                                                                                                               |
| 9   | b                    | 0     | RGB blue (0-100%)                                                                                                                                                |
| 10  | KNX rel. Dimm        | 0     | Eingang für KNX-Dimm-Signal. Der zugh. Taster muss wie folgt parametrisiert werden:<br/>Relatives dimmen mit Stopp-Signal, ohne Telegramm-Wiederholung           |
| 11  | KNX Dimm Ramp        | 0.5   | KNX Dimm Rampe [s]; Zeit in Sekunden, in der der Dimmschritt wiederholt wird, bis ein Stopp-Signal empfangen wird.                                               |

## Outputs

| Nr. | Name            | Init. | Description                                                                                       |
|-----|-----------------|-------|---------------------------------------------------------------------------------------------------|
| 1   | RM On/Off       | 0     | Ein/Aus Status (1/0)                                                                              |
| 2   | RM Brightness   | 0     | Aktuelle Helligkeit 0-100%                                                                        | 
| 3   | r               | 0     | RGB Rotwert 0-100%                                                                                |
| 4   | g               | 0     | RGB Grünwert 0-100%                                                                               |
| 5   | b               | 0     | RGB Blauwert 0-100%                                                                               |
| 6   | Light Reachable | 0     | Erreichbarkeit der Lampe (*nicht aktiv bei Gruppen-Steuerung!*); 0=nicht erreichbar, 1=erreichbar |

## Examples

| Eingang | Ausgang |
|---------|---------|
| -       | -       |


## Other

- Neuberechnung beim Start: Nein
- Baustein ist remanent: nein
- Interne Bezeichnung: 14100
- Kategorie: Datenaustausch

### Change Log

- v3.0
    - Refactoring & Umstellung auf Hue API v2
- v2.0
    - Keine Änderung zu v1.6
- v1.6
    - Bug fixing	
- v1.5
    - Refactoring w.r.t. warnings
    - Light control
- v1.4

### Open Issues / Know Bugs

- see [issue](https://github.com/En3rGy/14100_Hue/issues)

### Support

Please use [GitHub issue feature](https://github.com/En3rGy/14100_Hue/issues) to report bugs or rise feature requests.
Questions can be addressed as new threads at the [knx-user-forum.de](https://knx-user-forum.de) also. There might be discussions and solutions already.

### Code

Der Code des Bausteins befindet sich in der hslz Datei oder auf [github](https://github.com/En3rGy/14100_Hue).

### Development Environment

- [Python 2.7.18](https://www.python.org/download/releases/2.7/)
    - Install python markdown module (for generating the documentation) `python -m pip install markdown`
- Python editor [PyCharm](https://www.jetbrains.com/pycharm/)
- [Gira Homeserver Interface Information](http://www.hs-help.net/hshelp/gira/other_documentation/Schnittstelleninformationen.zip)


## Requirements
- Pairing mit Hue Bridge über Logikmodul durchführen, s. [API v2 Getting started](https://developers.meethue.com/develop/hue-api-v2/getting-started/)
- Lampen ein/ausschalten [#12](https://github.com/En3rGy/14100_Hue/issues/12)
- Ein/aus-Status ausgeben [#16](https://github.com/En3rGy/14100_Hue/issues/16)
- Lampen dimmen und Dimmwert ausgeben [#17](https://github.com/En3rGy/14100_Hue/issues/17)
- Farbe bei Lampen vorgeben und ausgeben [#19](https://github.com/En3rGy/14100_Hue/issues/19)
- Erreichbar-Status / Verbunden-Status ausgeben [#20](https://github.com/En3rGy/14100_Hue/issues/20)
- Starten von Szenen [#21](https://github.com/En3rGy/14100_Hue/issues/21)
- Abspielen von dynamischen Szenen [#22](https://github.com/En3rGy/14100_Hue/issues/22)
- Auch für Zonen [#14](https://github.com/En3rGy/14100_Hue/issues/14) / Räume [#15](https://github.com/En3rGy/14100_Hue/issues/15) / Gruppen [#13](https://github.com/En3rGy/14100_Hue/issues/13)
- Manuelles Abrufen des Status der Leuchten [#18](https://github.com/En3rGy/14100_Hue/issues/18)
- Selbständiges finden & verbinden mit der Hue-Bridge [#11](https://github.com/En3rGy/14100_Hue/issues/11)
- Automatisches re-connect mit Hue-Bridge bei Verbindungsabbruch [#10](https://github.com/En3rGy/14100_Hue/issues/10)
- Bei mehreren Bausteininstanzen verbindet sich nur einer mit der Hue Bridge und teilt die erhaltenen Informatione [#9](https://github.com/En3rGy/14100_Hue/issues/9)
- Bereitstellen einer Web-Seite mit Informationen zu Hue-IDs [#8](https://github.com/En3rGy/14100_Hue/issues/8)
- Soll den HS nicht blockieren [#23](https://github.com/En3rGy/14100_Hue/issues/23)

## Software Design Description
Das Modul ist so weit möglich objektorientiert entwickelt.
Hierbei gibt es vor allem zwei Objekte:
- Bridge Objekt<br>Zur Kommunikation mit der Hue Bridge, incl. Bridge Discovery
- Hue Item Objekt<br>Zur Kommandierung der Hue-Objekte, wie Lampen, Räume, Szenen, etc.
Wesentliches Element der Hue API v2 ist der *Eventstream*. Programme können sich für dieses registrieren und erhalten von der Hue Bridge quasi unmittelbar Statusänderungen.

Bei mehreren Hue-Logikbausteinen verbindet sich nur einer der Bausteine mit dem Eventstream und leitet eingehende Meldungen an alle anderen Hue-Bausteine weiter. 
Dies geschieht über den gemeinsamen Scope, eine Verbindung der Bausteine über iKO ist *nicht* notwendig. 

Außerdem:
- Lampen / Szenen / Zonen / Räume / Gruppen werden über die Id unterschieden; Abfrage des Typs via /resource {data{id, type}}
- Abh. von der Aktion wird die jew. rid über die Device id herausgesucht
- Nur ein Baustein verbindet sich mit der Hue Bridge, die übrigen nutzen diese Verbindung über [HS Instanzen](http://127.0.0.1/doc_extra/de/commloginst.html)
- Die eventstream Verbindung läuft in einem eigenen Thread in einer `While true`-Schleife
- Wenn zur Initialisierungszeit keine Netzwerkverbindung besteht, wird bei Signalen auf den Bausteineingängen versucht, eine Verbindung zur Bridge herzustellen. 

## Validation & Verification
- Unit tests are performed.

## Licence

Copyright 2021 T. Paul

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
