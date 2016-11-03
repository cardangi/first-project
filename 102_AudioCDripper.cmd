@ECHO off


SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initialisations 2.
REM ==================
SET _drives=%TEMP%\serial.txt
SET _audio=F:\`X5
SET /A _i=0


REM ==================================
REM Enumérer les lecteurs disponibles.
REM ==================================
REM wscript "G:\Computing\Serial.vbs"


REM =====================================================================
REM Détecter le lecteur amovible possédant le numéro de série "962933300".
REM =====================================================================
IF EXIST "%_drives%" (
    FOR /F "delims=; tokens=1-2 usebackq" %%a IN ("%_drives%") DO (
        IF "%%b" == "962933300" (
            SET _drive=%%a
        )
    )
)
IF NOT DEFINED _drive EXIT /B 100


REM =========================================
REM Détecter la présence de fichiers ".flac".
REM =========================================
IF EXIST "%_audio%" (
    FOR /R "%_audio%" %%i IN (*.flac) DO (
        SET /A _i=!_i! + 1
    )
)
IF "%_i%" EQU "0" EXIT /B 101


REM =====================================================
REM Copier les fichiers ".flac" vers le lecteur amovible.
REM =====================================================
PUSHD "%_PYTHONPROJECT%"
python -m Applications.CDRipper.AudioDigitalFilesCopy "%_drive%:" 30
POPD
