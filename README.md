# 14100 Hue Group

## Beschreibung 

Der Baustein steuert Hue Gruppen und liest den Status der Gruppe oder 
einzelner Lampen aus. Um die Netzwerklast zu verringern können mehrere 
Bausteine als Kaskade geschaltet werden, um die Statusmeldung der Hue-Bridge 
für mehrere Lampen bzw. Gruppen auszulesen.

Die ersten 3 Eingänge sind ausschließlich für den Status. Ein Baustein muss 
regelmäßig via Get (E3) getriggered werden. Dann generiert er über die letzten 
beiden Ausgänge die Infos für alle anderen Bauteile, die die Daten via deren 
E1 und E2 bekommen sollten. E3 sollte bei diesen anderen Bausteinen nicht 
getriggert werden, sonst würden sie zusätzlich den Status abfragen.

Sollen die Bausteine zum Schalten, etc. verwendet werden, brauchen Sie IP, 
Port und Benutzer und Group Id. Die Light Id wird nur für den Status genutzt 
(Reachable wird nur pro Light, nicht für Gruppen ausgegeben).

## Eingänge

| Nr. | Name | Initialisierung | Beschreibung |
| --- | ---  | --- | --- |
| 1   | Json |     | Für Baustein-Kaskade: Verknüpfung des gleichnamigen Ausgangs eines anderen Bausteins.<br/>Die Einstellung für die Steuerung einer Gruppe oder Leuchte muss in der ganzen Kaskade identisch konfiguriert sein (E6 bei allen 1 oder 0) |
| 2 | Get Status | | Ein Wert =1 triggert den Status-Abruf über die Hue-Bridge. Hier ist es z.B. Sinnvoll einen Telegrammgenerator anzuschließen. Damit kann detektiert werden, wenn eine Lampe auf einem anderen Weg, als über den Baustein geschaltet wird. |
| 3 | Hue Bridge IP | | IP der Hue Bridge |
| 4 | Hue Bridge Port | 80 | Port der Hue Bridge |
| 5 | User | | Hue Bridge User |
| 6 | Control Group | 0 | 1, wenn eine Lampengruppe gesteuert werden soll,<br/> 0 wenn eine einzelne Lampe gesteuert werden soll |
| 7 | Item Id | 0 | Abh. von Eingang 6, die Id der auszuwertenden Hue Gruppe oder Lampe, vgl. http://hue-ip/api/hue-user/lights |
| 8 | Grp On/Off | 0 | Schaltet die Lampe / Gruppe ein (1) / aus (0). |
| 9 | Brightness | 0 | Helligkeit für die Hue Lampe / Gruppe in 0-100% <br/> Wird der Wert gesetzt, wird die Gruppe eingeschaltet. |
| 10 | Grp Hue Color | 0 | Hue Color:<br/>0 - 65.535; mit 182,04 * Hue Color Wert<br/>Wird der Wert gesetzt, wird die Gruppe eingeschaltet. |
| 11 | Grp Saturation | 0 | Sättigung der Hue Gruppe in 0-100%<br/>Wird der Wert gesetzt, wird die Gruppe eingeschaltet. |
| 12 | Grp Color Temp | 0 | Farbtemperatur der Gruppe (nur Weißwert):<br/>154 - 500; mit 1.000.000 / CT-Wert, z.B. 6500K = 154 (kalt) und 2000K = 500 (warm)<br/>Wird der Wert gesetzt, wird die Gruppe eingeschaltet. |
| 13 | r | 0 | RGB Rotwert 0-100% |
| 14 | g | 0 | RGB Grünwert 0-100% |
| 15 | b | 0 | RGB Blauwert 0-100% |
| 16 | Grp Hue Scene | | Hue Scene für die Hue Gruppe, vgl. http://hue-bridge-ip/user/scenes |
| 17 | Transition Time | 0 | Zeit zum Einnehmen des neuen Zustandes in x * 10ms, 10 führt z.B. zu einem Übergangszeit von 1 sek. |
| 18 | Alert Effect | 0 | 1 startet den Alarm, 0 stoppt den Alarm wieder |
| 19 | Color Loop | 0 | Schaltet einen endlos-Farbdurchlauf ein oder aus. |
| 20 | KNX rel. Dimm | 0 | Eingang für das Dimm-Signal. Der zugh. Taster muss wie folgt parametrisiert werden:<br/>Relatives dimmen mit Stopp-Signal, ohne Telegrammwiederholung<br/>KNX Dimm Rampe [s] 	0.5 	Zeit in Sekunden, in der der Dimmschritt wiederholt wird, bis ein Stopp-Signal empfangen wird. |


## Ausgänge

| Nr. | Name | Initialisierung | Beschreibung |
| --- | --- | --- | --- |
| 1   | RM On/Off | 0 | Ein/Aus Status (1/0) |
| 2 | RM Brightness | 0 | Aktuelle Helligkeit 0-100% | 
| 3 | RM Hue Color 	| 0 | Aktuelle Hue Color 0-65534.4 | 
| 4 | RM Saturation | 0 | Aktuelle Sättigung in 0-100% | 
| 5 | RM Color Temp  | 0 | Farbtemperatur der Gruppe / Leuchte (nur Weißwert) 154 - 500 (vgl. Eingang) |
| 6 | r | 0 | RGB Rotwert 0-100% |
| 7 | g | 0 | RGB Grünwert 0-100% |
| 8 | b | 0 | RGB Blauwert 0-100% |
| 9 | Lght Reachable | 0 | Erreichbarkeit der Lampe (*nicht aktiv bei Gruppen-Steuerung!*); 0=nicht erreichbar, 1=erreichbar |
| 10 | Json | | Json Struktur für den Status der Gruppe für Kaskaden von Bausteinen (für den Eingang des Folgebausteins).<br/>Die Einstellung für die Steuerung einer Gruppe oder Leuchte muss in der ganzen Kaskade identisch konfiguriert sein (E6 bei allen 1 oder 0) | 

## Beispielwerte

| Eingang | Ausgang |
| --- | --- |
| - | - |


## Other

- Neuberechnug beim Start: Nein
- Baustein ist remanent: nein
- Interne Bezeichnung: 14100
- Kategorie: Datenaustausch

### Change Log

 - v1.5
     - Refactoring w.r.t. warnings
     - Light control
 - v1.4

### Open Issues / Know Bugs

- keine

### Support

Please use [github issue feature](https://github.com/En3rGy/14100_Hue/issues) to report bugs or rise feature requests.
Questions can be addressed as new threads at the [knx-user-forum.de](https://knx-user-forum.de) also. There might be discussions and solutions already.


### Code

Der Code des Bausteins befindet sich in der hslz Datei oder auf [github](https://github.com/En3rGy/14100_Hue).

### Devleopment Environment

- [Python 2.7.18](https://www.python.org/download/releases/2.7/)
    - Install python markdown module (for generating the documentation) `python -m pip install markdown`
- Python editor [PyCharm](https://www.jetbrains.com/pycharm/)
- [Gira Homeserver Interface Information](http://www.hs-help.net/hshelp/gira/other_documentation/Schnittstelleninformationen.zip)


## Requirements
-

## Software Design Description


## Validation & Verification
- Unit tests are performed.

## Licence

Copyright 2021 T. Paul

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
