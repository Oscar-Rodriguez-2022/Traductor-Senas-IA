@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

:menu
cls
echo ==========================================================
echo        SUITE DE CALIDAD DE SOFTWARE - TRADUCTOR LSP
echo ==========================================================
echo.
echo   1. Pruebas unitarias e integracion (pytest)
echo   2. Cobertura de codigo (HTML)
echo   3. Benchmark de rendimiento
echo   4. Medicion de FPS (30s)
echo   5. Test de estres (100..5000)
echo   6. Precision del modelo (Accuracy/Precision/Recall/F1)
echo   7. Matriz de confusion (PNG)
echo   8. Validacion cruzada K-Fold
echo   9. Robustez ante condiciones adversas
echo  10. Consumo de RAM y CPU
echo  11. Calidad de codigo (flake8 + pylint)
echo  12. Generar REPORTE consolidado (PDF + HTML)
echo  13. EJECUTAR TODO (suite completa)
echo   0. Salir
echo.
set /p op="Elige una opcion: "

if "%op%"=="1" "%PY%" -m pytest tests/ & pause & goto menu
if "%op%"=="2" "%PY%" -m pytest tests/ --cov=lsp_core --cov-report=html --cov-report=term & echo. & echo Abre htmlcov\index.html & pause & goto menu
if "%op%"=="3" "%PY%" qa\benchmark.py & pause & goto menu
if "%op%"=="4" "%PY%" qa\fps_test.py & pause & goto menu
if "%op%"=="5" "%PY%" qa\stress_test.py & pause & goto menu
if "%op%"=="6" "%PY%" qa\evaluate.py & pause & goto menu
if "%op%"=="7" "%PY%" qa\confusion_matrix.py & pause & goto menu
if "%op%"=="8" "%PY%" qa\cross_validation.py & pause & goto menu
if "%op%"=="9" "%PY%" qa\robustez.py & pause & goto menu
if "%op%"=="10" "%PY%" qa\recursos.py & pause & goto menu
if "%op%"=="11" "%PY%" -m flake8 lsp_core.py qa tests & "%PY%" -m pylint lsp_core.py & pause & goto menu
if "%op%"=="12" "%PY%" qa\generar_reportes.py & pause & goto menu
if "%op%"=="13" goto todo
if "%op%"=="0" exit
goto menu

:todo
echo Ejecutando suite completa...
"%PY%" -m pytest tests/
"%PY%" qa\benchmark.py
"%PY%" qa\fps_test.py
"%PY%" qa\stress_test.py
"%PY%" qa\evaluate.py
"%PY%" qa\confusion_matrix.py
"%PY%" qa\cross_validation.py
"%PY%" qa\robustez.py
"%PY%" qa\recursos.py
"%PY%" qa\generar_reportes.py
echo.
echo ===== QA COMPLETO. Revisa la carpeta reportes\ =====
pause
goto menu
