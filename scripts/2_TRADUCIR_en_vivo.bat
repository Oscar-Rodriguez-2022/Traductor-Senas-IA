@echo off
REM Lanzador del modulo de entrenamiento + traduccion en vivo (scripts/traducir_en_vivo.py)
cd /d "%~dp0.."
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" scripts\traducir_en_vivo.py
echo.
echo --- Programa finalizado ---
pause
