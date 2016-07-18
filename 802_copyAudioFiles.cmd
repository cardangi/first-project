@ECHO off


REM
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _xxcopy=%TEMP%\xxcopy
SET _script=python -m Applications.AudioFiles.copyFiles


REM ===============
REM Main algorithm.
REM ===============
COLOR 3F

:MAIN
PUSHD %_PYTHONPROJECT%
%_script%
IF ERRORLEVEL 1 (
    POPD
    GOTO EXIT
)
IF EXIST "%_xxcopy%" (
    FOR /F usebackq^ delims^= %%i IN ("%_xxcopy%") DO (
        %%i
    )
)


:EXIT
CLS
EXIT /B 0
