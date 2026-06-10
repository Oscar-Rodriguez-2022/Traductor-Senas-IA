@echo off
REM Abre la web app en tu navegador local (http://localhost:8501)
cd /d "%~dp0"
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -m streamlit run app.py
pause
