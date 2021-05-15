@echo off
set path=%path%;C:\Python27\
set PYTHONPATH=C:\Python27;C:\Python27\Lib

echo ^<head^> > .\release\log14100.html
echo ^<link rel="stylesheet" href="style.css"^> >> .\release\log14100.html
echo ^<title^>Logik - Hue Group (14100)^</title^> >> .\release\log14100.html
echo ^<style^> >> .\release\log14100.html
echo body { background: none; } >> .\release\log14100.html
echo ^</style^> >> .\release\log14100.html
echo ^<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"^> >> .\release\log14100.html
echo ^</head^> >> .\release\log14100.html

@echo on

type .\README.md | C:\Python27\python -m markdown -x tables >> .\release\log14100.html

cd ..\..
C:\Python27\python generator.pyc "14100_Hue" UTF-8

xcopy .\projects\14100_Hue\src .\projects\14100_Hue\release /exclude:.\projects\14100_Hue\src\exclude.txt

@echo Fertig.

@pause