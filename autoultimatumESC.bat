@echo off
title AutoUltimatum

rem Roda sempre a partir da pasta onde este .bat esta salvo,
rem sem nenhum caminho fixo.
pushd "%~dp0"

set "PY=.venv\Scripts\python.exe"

if not exist "%PY%" (
    echo [ERRO] Nao encontrei o ambiente virtual em .venv
    echo        A pasta .venv deve estar junto deste .bat.
    goto :fim
)

echo ============================================================
echo  AutoUltimatum
echo  F8 = iniciar/parar   F7 = normal/grueling   F6 = sair
echo ============================================================
echo.

"%PY%" "autoulti_esc.py"

echo.
echo Script encerrado.

:fim
popd
pause
