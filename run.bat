@echo off
cd /d "%~dp0"
title CineSENAI & Teatro - Sistema de Bilheteria
echo ===================================================
echo     CineSENAI & Teatro - Bilheteria e Bomboniere
echo     Projeto Final de Curso SENAI
echo ===================================================
echo.

IF EXIST .venv\Scripts\python.exe (
    echo Iniciando com o ambiente virtual local...
    .venv\Scripts\python.exe app.py
) ELSE (
    echo Verificando instalacao de dependencias...
    python -m venv .venv
    if errorlevel 1 goto erro
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 goto erro
    echo Iniciando CineSENAI...
    .venv\Scripts\python.exe app.py
)

pause
exit /b
:erro
echo Nao foi possivel preparar o ambiente. Instale Python 3.11 ou mais recente e confira a conexao.
pause
