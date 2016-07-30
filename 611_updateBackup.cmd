@ECHO off

REM
SETLOCAL ENABLEEXTENSIONS

REM Initializations.
SET _me=%~n0
SET _myparent=%~dp0

REM Main algorithm.
:START
IF "%~1" EQU "" EXIT /B 0

:MAIN
PUSHD "%_PYTHONPROJECT%"
python -m Applications.Database.Backups.dbBackup update %~1
POPD
SHIFT
GOTO START
