@echo off
title Inicializador de Ambiente de Desenvolvimento

REM --- Limpa a tela e exibe uma mensagem de boas-vindas ---
cls
echo =========================================================
echo      INICIANDO AMBIENTE DE DESENVOLVIMENTO
echo =========================================================
echo.
echo Este script ira configurar e iniciar o backend e o frontend
echo em janelas de terminal separadas.
echo.
timeout /t 2 /nobreak >nul

REM -----------------------------------------------------------------
REM ETAPA 1: CONFIGURAR E INICIAR O BACKEND (COMPILADORES)
REM -----------------------------------------------------------------
echo --- [1/2] Preparando o Backend (Flask)...

start "Backend - Servidor Python" cmd /k "cd ./compiladores && (if exist venv\ (echo. && echo Ambiente virtual 'venv' encontrado. && echo Ativando e instalando dependencias... && call venv\Scripts\activate && pip install flask flask-cors && echo. && echo --- INICIANDO SERVIDOR PYTHON --- && python main.py) else (echo. && echo ERRO: A pasta 'venv' nao foi encontrada em 'compiladores'. && echo Certifique-se de cria-la primeiro com: python -m venv venv && pause))"

echo Backend iniciado em uma nova janela.
echo.
timeout /t 3 /nobreak >nul

REM -----------------------------------------------------------------
REM ETAPA 2: CONFIGURAR E INICIAR O FRONTEND (COMPILADORES-FRONT-JS)
REM -----------------------------------------------------------------
echo --- [2/2] Preparando o Frontend (JavaScript)...

start "Frontend - Servidor de Dev" cmd /k "cd ./compilador-front-js && (if not exist node_modules (echo. && echo Pasta 'node_modules' nao encontrada. && echo Rodando 'npm install', isso pode levar alguns minutos... && npm install) else (echo. && echo Pasta 'node_modules' encontrada, pulando 'npm install'.)) && echo. && echo --- INICIANDO SERVIDOR DE DESENVOLVIMENTO --- && npm run dev"

echo Frontend iniciado em uma nova janela.
echo.
echo =========================================================
echo. 
echo Processo de inicializacao concluido!
echo Voce pode fechar esta janela.
echo.
pause