@ECHO off
REM Stocker dans un fichier JSON les arguments permettant de copier un fichier audio FLAC
REM Le profil associé à la copie est transmis à un script python en qualité de premier paramètre.
REM Le nom du fichier audio est transmis en qualité de deuxième paramètre.
REM La lettre identifiant le lecteur reçevant le fichier copié est transmise en qualité de troisième paramètre.
REM Le nom du fichier JSON est transmis en qualité de quatrième paramètre.


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
SET _json=%TEMP%\arguments.json


REM ==================================
REM Enumérer les lecteurs disponibles.
REM ==================================
wscript "G:\Computing\Serial.vbs"


REM ======================================================================
REM Détecter le lecteur amovible possédant le numéro de série "962933300".
REM ======================================================================
IF NOT EXIST "%_drives%" EXIT /B 100
IF EXIST "%_drives%" (
    FOR /F "delims=; tokens=1-2 usebackq" %%a IN ("%_drives%") DO (
        IF "%%b" == "962933300" (
            SET _drive=%%a
        )
    )
)
IF NOT DEFINED _drive EXIT /B 100


REM ======================================================
REM Ecrire les arguments de copie dans un un fichier JSON.
REM ======================================================
PUSHD %_PYTHONPROJECT%
python -m Applications.CDRipper.AudioDigitalFiles`CopyArguments "%~1" "%_drive%:" -o "%_json%"
POPD
