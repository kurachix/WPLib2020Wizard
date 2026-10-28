@echo off
setlocal
cd /d "%~dp0"
title Compilando WPILib 2020 Robot Wizard

echo ======================================================================
echo           WPILIB 2020 ROBOT WIZARD - COMPILADOR AUTOMATICO .EXE
echo ======================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Python nao foi encontrado no PATH do sistema.
    echo Por favor, instale o Python 3.10+ e adicione-o ao PATH.
    pause
    exit /b 1
)

echo Instalando / atualizando dependencias de requirements.txt...
python -m pip install -r requirements.txt --quiet

echo.
echo Executando build.py...
python build.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCESSO] Compilacao concluida com exito!
    echo Os executaveis estao prontos na pasta 'dist'.
) else (
    echo.
    echo [ERRO] Ocorreu uma falha durante o processo de build.
)

echo.
pause
