# 14100 Hue Group

## Beschreibung 

Der Baustein stellt eine Schnittstelle zu einzelnen Leuchten / Gruppen / Räumen / Zonen 
eines Hue-Systems dar. D.h. die angesprochenen Geräte lassen sich steuern und deren Status wird ausgegeben.
Hierzu meldet sich der Baustein bei der Hue-Bridge an und erhält so direkt von dieser Informationen zu 
Statusänderungen. Um die Netzwerklast zu verringern, können mehrere 
Bausteine als Kaskade geschaltet werden.

Der Baustein erkennt selbständig die Hue-Bridge im Netzwerk und verbindet sich mit dieser.

!Wenn sich die IP der Bridge ändert, ist ein Neustart des HS notwendig!

Der Baustein nutzt die [Hue API v2](https://developers.meethue.com/develop/hue-api-v2/).

## Eingänge

| Nr. | Name           | Initialisierung | Beschreibung                                                                                                                                           |
|-----|----------------|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | Get Status     |                 | Ein Wert =1 triggert den Status-Abruf über die Hue-Bridge.                                                                                             |
| 2   | Key            |                 | Hue Bridge User Key                                                                                                                                    |
| 3   | Port Info Page | 0               | Der Bautein erzeugt eine Webseite, mit den IDs der Hue leuchten, Räume usw. Die seite kann aufgerufen werden über http://<HS-IP>:<Port>                |
| 4   | Item Id        | 0               | Abh. von Eingang 6, die Id der auszuwertenden Hue Gruppe oder Lampe, vgl. http://hue-ip/api/hue-user/lights                                            |
| 5   | On/Off (1/0)   | 0               | Schaltet die Lampe / Gruppe ein (1) / aus (0).                                                                                                         |
| 6   | Brightness (%) | 0               | Helligkeit für die Hue Lampe / Gruppe in 0-100% <br/> Wird der Wert gesetzt, wird die Gruppe eingeschaltet.                                            |
| 7   | r              | 0               | RGB Rotwert 0-100%                                                                                                                                     |
| 8   | g              | 0               | RGB Grünwert 0-100%                                                                                                                                    |
| 9   | b              | 0               | RGB Blauwert 0-100%                                                                                                                                    |
| 10  | KNX rel. Dimm  | 0               | Eingang für das Dimm-Signal. Der zugh. Taster muss wie folgt parametrisiert werden:<br/>Relatives dimmen mit Stopp-Signal, ohne Telegramm-Wiederholung |
| 11  | KNX Dimm Ramp  | 0.5             | KNX Dimm Rampe [s]; Zeit in Sekunden, in der der Dimmschritt wiederholt wird, bis ein Stopp-Signal empfangen wird.                                     |

## Ausgänge

| Nr. | Name            | Initialisierung | Beschreibung                                                                                                                                                                                                                                             |
|-----|-----------------|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | RM On/Off       | 0               | Ein/Aus Status (1/0)                                                                                                                                                                                                                                     |
| 2   | RM Brightness   | 0               | Aktuelle Helligkeit 0-100%                                                                                                                                                                                                                               | 
| 3   | r               | 0               | RGB Rotwert 0-100%                                                                                                                                                                                                                                       |
| 4   | g               | 0               | RGB Grünwert 0-100%                                                                                                                                                                                                                                      |
| 5   | b               | 0               | RGB Blauwert 0-100%                                                                                                                                                                                                                                      |
| 6   | Light Reachable | 0               | Erreichbarkeit der Lampe (*nicht aktiv bei Gruppen-Steuerung!*); 0=nicht erreichbar, 1=erreichbar                                                                                                                                                        |

## Beispielwerte

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

- keine

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
