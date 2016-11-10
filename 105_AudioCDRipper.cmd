@ECHO off


SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ======================================================
REM Ecrire les arguments de copie dans un un fichier JSON.
REM ======================================================
PUSHD %_PYTHONPROJECT%
python -m Applications.CDRipper.AudioCD`OutFiles "%~1"
POPD
