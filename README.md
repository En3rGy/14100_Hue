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
| --- | --- | --- | --- |
| 1 |  | |  |

## Ausgänge

| Nr. | Name | Initialisierung | Beschreibung |
| --- | --- | --- | --- |
| 1 |  |  |  |

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
