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
SET _xxcopy=%TEMP%\xxcopy.txt


REM ===============
REM Main algorithm.
REM ===============

:START
IF EXIST %_xxcopy% DEL %_xxcopy%
PUSHD %_PYTHONPROJECT%
python -m Applications.AudioFiles.importFiles --test
IF ERRORLEVEL 1 (
    GOTO EXIT
)

:EXIT
POPD
CLS
EXIT /B 0