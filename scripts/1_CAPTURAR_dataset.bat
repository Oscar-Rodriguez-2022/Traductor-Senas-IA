@echo off
REM Lanzador del modulo de captura (scripts/capturar_dataset.py)
cd /d "%~dp0.."
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" scripts\capturar_dataset.py
echo.
echo --- Programa finalizado ---
pause
