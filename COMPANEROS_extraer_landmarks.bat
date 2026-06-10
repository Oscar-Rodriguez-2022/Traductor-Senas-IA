@echo off
REM ===== PARA LOS COMPANEROS =====
REM Genera tu CSV de landmarks despues de capturar con A.py.
REM Busca Python automaticamente.
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python extraer_landmarks.py
    goto fin
)
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 extraer_landmarks.py
    goto fin
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" extraer_landmarks.py
    goto fin
)
echo.
echo No se encontro Python. Instala Python 3.12 y ejecuta:
echo    pip install opencv-python mediapipe numpy scikit-learn
echo.
:fin
echo.
pause
