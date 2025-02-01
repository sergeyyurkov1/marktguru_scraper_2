@echo off
cls

title MarktGuru Scraper

call .\venv\Scripts\activate

echo Cleaning up...
call .\venv\Scripts\python.exe clean.py

echo Opening the program...
call .\venv\Scripts\python.exe main.py

pause
@REM exit