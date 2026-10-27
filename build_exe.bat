@echo off
title Compilando WPILib 2020 Robot Wizard para .exe
echo ============================================================
echo   Compilando WPILib 2020 Robot Wizard para .exe
echo ============================================================
echo.

cd /d "%~dp0python"

echo Verificando instalacao do PyInstaller...
python -m pip install pyinstaller --quiet

echo.
echo Executando build do executavel...
python build.py

echo.
echo Processo finalizado!
pause
