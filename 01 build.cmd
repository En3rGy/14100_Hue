@echo off
set path=%path%;C:\Python27\
set PYTHONPATH=C:\Python27;C:\Python27\Lib
@echo on

cd ..\..
C:\Python27\python generator.pyc "14100_Hue" UTF-8

xcopy .\projects\14100_Hue\src .\projects\14100_Hue\release

@echo Fertig.

@pause