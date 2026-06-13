@echo off
chcp 65001 >nul
title Augmentation + Entrenamiento — LSP Vision AI

echo ============================================================
echo   augmentar_dataset.py  ^|  LSP Vision AI — UPN Capstone
echo   Multiplica el dataset x16 y entrena el modelo SVM
echo ============================================================
echo.

cd /d "%~dp0.."

:: Buscar Python 3.12 (requerido por MediaPipe 0.10.21)
set PY312=
for %%P in (
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    "C:\Python312\python.exe"
) do (
    if exist %%P (
        set PY312=%%P
        goto :found
    )
)

:: Fallback: intentar con el lanzador py
where py >nul 2>&1
if %errorlevel%==0 (
    py -3.12 --version >nul 2>&1
    if %errorlevel%==0 (
        set PY312=py -3.12
        goto :found
    )
)

echo [ERROR] No se encontro Python 3.12.
echo         Descarga Python 3.12 desde https://www.python.org/downloads/
echo         y marca "Add to PATH" durante la instalacion.
pause
exit /b 1

:found
echo Usando: %PY312%
echo.
echo Iniciando extraccion de landmarks y augmentation...
echo (Esto puede tardar 1-3 minutos segun el tamaño del dataset)
echo.

%PY312% scripts\augmentar_dataset.py

if %errorlevel%==0 (
    echo.
    echo ============================================================
    echo   [OK] modelo.pkl actualizado con data augmentation.
    echo   Sube el modelo a GitHub antes de desplegar:
    echo     git add modelo.pkl
    echo     git commit -m "Modelo con augmentation"
    echo     git push
    echo ============================================================
) else (
    echo.
    echo [ERROR] El script termino con errores. Revisa la salida arriba.
)

echo.
pause
