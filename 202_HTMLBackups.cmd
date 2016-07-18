@ECHO off

REM
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

REM ----------------
REM Initialisations.
REM ----------------
SET _first=Y
SET _computing=g:\computing
SET _pythonproject=%_computing%\mypythonproject
SET _output1=%TEMP%\output1.xml
SET _output2=%TEMP%\output2.xml
SET _backups=%_computing%\backups\backups
SET _saxon=c:\saxon\saxon9he.jar
SET _backup=y:\backup
SET _workspace=""

REM -----------------------
REM Inventaire des scripts.
REM -----------------------
FOR /R "%_backup% %%i IN (*.bcfg) DO (

REM 1. --> Extraction du nom du workspace.
    FOR /F "usebackq tokens=3 delims=.\" %%k IN ('%%~pi') DO SET _newworkspace=%%k

REM 2. --> Gestion de la rupture du workspace.
    IF NOT "!_newworkspace!"==!_workspace! (

REM 2a. --> Fermeture du tag "workspace" si la rupture n'est pas la première.
        IF NOT !_first!=="Y" (
        ECHO ^</workspace^>>>"%_output1%"
        )

REM 2b. --> Sauvegarde du nouveau workspace.
        SET _workspace="!_newworkspace!"

REM 2c. --> Ouverture du tag "workspace".
        IF "!_first!"=="Y" (
        ECHO ^<?xml version="1.0" encoding="UTF-8"?^>>"%_output1%"
        ECHO ^<?xml-stylesheet type="text/xsl" href="backups.xsl"?^>>>"%_output1%"
        ECHO ^<targets css="backups.css" title="Backup Scripts"^>>>"%_output1%"
        SET _first=N
        )
        ECHO ^<workspace name=!_workspace!^>>>"%_output1%"

    )

REM 3. --> Ajout de la structure XML du fichier BCFG lu.
    FOR /F usebackq^ skip^=^2^ delims^= %%j IN ("%%i") DO ECHO %%j>>"%_output1%"

)

REM 4. --> Fermeture du dernier tag "workspace".
ECHO ^</workspace^>>>"%_output1%"

REM 5. --> Fermeture du dernier tag "target".
ECHO ^</targets^>>>"%_output1%"

REM 6. --> Elaboration du fichier HTML.
IF EXIST "%_output1%" (
    PUSHD "%_pythonproject%"
    python -m Applications.Database.XMLBackups
    IF EXIST "%_output2%" (
        java -cp "%_saxon%" net.sf.saxon.Transform -s:"%_output2%" -xsl:"%_backups%.xsl" -o:"%_backups%.html"
    )
    POPD
)
