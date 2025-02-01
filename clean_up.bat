@echo off
cls

call .\venv\Scripts\activate

echo Cleaning up...
call .\venv\Scripts\python.exe clean.py

pause
@REM exit