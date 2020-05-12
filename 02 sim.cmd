@echo off 

set path=%path%;C:\Python27
set PYTHONPATH=C:\Python27;C:\Python27\Lib

cd ..\..
C:\Python27\python simulator.pyc "14100_Hue" "tst"

pause