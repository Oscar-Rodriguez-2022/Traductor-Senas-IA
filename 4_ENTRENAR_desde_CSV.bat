@echo off
REM ===== PARA TI (encargado del dataset) =====
REM Combina todos los CSV de la carpeta landmarks_csv y entrena modelo.pkl.
cd /d "%~dp0"
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" entrenar_desde_csv.py
echo.
pause
