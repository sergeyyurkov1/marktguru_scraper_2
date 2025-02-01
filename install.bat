@echo off
cls
call .\venv\Scripts\activate
if exist requirements-frozen.txt call .\venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements-frozen.txt
if not exist requirements-frozen.txt call .\venv\Scripts\python.exe -m pip install -r requirements.txt
call .\venv\Scripts\python.exe -m pip freeze -l > requirements-frozen.txt
pause
