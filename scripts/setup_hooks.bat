@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo   LSP Vision AI — Instalador de Git Hooks
echo   UPN Capstone 2026
echo ============================================================
echo.

:: Verificar que estamos en la raiz del repositorio
if not exist ".git\hooks" (
    echo [ERROR] Ejecuta este script desde la raiz del repositorio.
    echo         Ejemplo: cd C:\Traductor-Senas-IA
    echo                  scripts\setup_hooks.bat
    pause
    exit /b 1
)

:: Verificar que existe el hook fuente
if not exist "scripts\hooks\pre-commit" (
    echo [ERROR] No se encontro scripts\hooks\pre-commit
    echo         Asegurate de haber clonado el repositorio correctamente.
    pause
    exit /b 1
)

echo [1/2] Copiando pre-commit hook...
copy /Y "scripts\hooks\pre-commit" ".git\hooks\pre-commit" >nul
if errorlevel 1 (
    echo [ERROR] No se pudo copiar el archivo.
    pause
    exit /b 1
)

:: Git Bash necesita permisos de ejecucion (usa git update-index)
echo [2/2] Aplicando permisos de ejecucion...
git update-index --chmod=+x scripts/hooks/pre-commit >nul 2>&1

echo.
echo [OK] Hook instalado correctamente en .git\hooks\pre-commit
echo.
echo      A partir de ahora, cada "git commit" escaneara
echo      automaticamente secretos antes de confirmar cambios.
echo.
echo      Patrones detectados:
echo        - Archivos: secrets.toml, .env, *.pem, *.key, id_rsa ...
echo        - Contenido: APP_PASSWORD, api_key, token, claves privadas ...
echo        - Tokens:    AWS (AKIA...), GitHub (ghp_...), OpenAI (sk-...)
echo.
pause
