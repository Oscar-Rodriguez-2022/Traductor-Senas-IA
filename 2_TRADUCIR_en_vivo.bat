@echo off
REM Lanzador del modulo de entrenamiento + traduccion en vivo (B.py)
cd /d "%~dp0"
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" B.py
echo.
echo --- Programa finalizado ---
pause
