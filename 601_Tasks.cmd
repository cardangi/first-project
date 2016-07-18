@ECHO off

REM
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ================
REM Initializations.
REM ================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _xmldigitalaudiobase=%TEMP%\digitalaudiobase.xml
SET _digitalaudiobase=%_COMPUTING%\digitalaudiobase\digitalaudiobase


REM ===============
REM Main algorithm.
REM ===============
COLOR 3F
PUSHD %_PYTHONPROJECT%


REM -------------
REM Display menu.
REM -------------
:MENU
python -m Applications.Tasks.displayMenu


REM ----------
REM Exit menu.
REM ----------
IF ERRORLEVEL 99 GOTO EXIT


REM -------------------
REM Convert Unix epoch.
REM -------------------
IF ERRORLEVEL 23 (
    python Applications`convertUnixEpoch`L.py
    IF ERRORLEVEL 11 GOTO MENU
    GOTO MENU
)


REM -------------------------
REM Get Unix epoch from date.
REM -------------------------
IF ERRORLEVEL 22 (
    python Applications`getUnixEpoch`L.py
    GOTO MENU
)


REM ----------------------
REM Timestamp audio files.
REM ----------------------
IF ERRORLEVEL 21 (
    python AudioFiles`Taggingtime`L.py
    GOTO MENU
)


REM -------------------
REM Rename audio files.
REM -------------------
IF ERRORLEVEL 20 (
    python AudioFiles`renameFiles`L.py
    GOTO MENU
)


REM ----------------------------------
REM Copy audio files from audio drive.
REM ----------------------------------
IF ERRORLEVEL 19 (
    CALL "G:\Computing\802_copyAudioFiles.cmd"
    GOTO MENU
)


REM ----------------------------------
REM Import audio files to audio drive.
REM ----------------------------------
IF ERRORLEVEL 18 (
    CALL "G:\Computing\801_importAudioFiles.cmd"
    GOTO MENU
)


REM ---------------------------
REM Display geometric sequence.
REM ---------------------------
IF ERRORLEVEL 17 (
    python Math`Sequences`L.py G
    GOTO MENU
)


REM ----------------------------
REM Display arithmetic sequence.
REM ---------------------------
IF ERRORLEVEL 16 (
    python Math`Sequences`L.py A
    GOTO MENU
)


REM ------------------------------
REM Digital Audio HTML fancy view.
REM ------------------------------
IF ERRORLEVEL 15 (
    PUSHD %_PYTHONPROJECT%
    python -m Applications.Database.DigitalAudio.View1
    IF NOT ERRORLEVEL 1 (
        IF EXIST "%_xmldigitalaudiobase%" (
            java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
            DEL "%_xmldigitalaudiobase%"
        )
    )
    POPD
    GOTO MENU
)


REM ---------------------------
REM RippingLog HTML fancy view.
REM ---------------------------
IF ERRORLEVEL 14 (
    python G:\Computing\MyPythonProject\Database`HTMLView`L.py RippingLog
    GOTO MENU
)


REM -------------------------
REM RippingLog HTML raw view.
REM -------------------------
IF ERRORLEVEL 13 (
    PUSHD %_PYTHONPROJECT%
    python -m Applications.Database.RippingLog.View2
    POPD
    GOTO MENU
)


REM ---------------------------------
REM Digital Audio base HTML raw view.
REM ---------------------------------
IF ERRORLEVEL 12 (
    python G:\Computing\MyPythonProject\Database`HTMLView`L.py DigitalAudio
    GOTO MENU
)


REM ---------------------------
REM LastRunDates HTML raw view.
REM ---------------------------
IF ERRORLEVEL 11 (
    python G:\Computing\MyPythonProject\Database`HTMLView`L.py LastRunDates
    GOTO MENU
)


REM ---------------------
REM Backup HTML raw view.
REM ---------------------
IF ERRORLEVEL 10 (
    python G:\Computing\MyPythonProject\Database`HTMLView`L.py Backups
    GOTO MENU
)


IF ERRORLEVEL 8 GOTO EXIT


REM --------------------------------------
REM Pearl Jam 2011 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 7 (
    python Backups`Areca`L.py music --check --debug --target 1484552884
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2010 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 6 (
    python Backups`Areca`L.py music --check --debug --target 445045058
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2006 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 5 (
    python Backups`Areca`L.py music --check --debug --target 1404261019
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2003 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 4 (
    python Backups`Areca`L.py music --check --debug --target 1557918403
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2000 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 3 (
    python Backups`Areca`L.py music --check --debug --target 1460302155
    GOTO MENU
)


REM --------------------------
REM Pearl Jam bootlegs backup.
REM --------------------------
IF ERRORLEVEL 2 (
    python Backups`Areca`L.py music --check --debug --target 1460302155 1557918403 1404261019 445045058 1484552884
    GOTO MENU
)


REM ---------------------------
REM Default audio files backup.
REM ---------------------------
IF ERRORLEVEL 1 (
    python Backups`Areca`L.py music --check --debug --target 854796030 1674209532 1196865155 1535780732 204959095
    GOTO MENU
)


REM ---------------------------------------------
REM HTML digital audio database view. DEPRECATED!
REM ---------------------------------------------
REM CALL "%_COMPUTING%\201_HTMLPages.cmd" C
REM ECHO.
REM ECHO.
REM ECHO HTML output created with success.
REM PAUSE
REM GOTO MENU


REM ----------------------------------------------------------
REM HTML Pearl Jam digital bootlegs database view. DEPRECATED!
REM ----------------------------------------------------------
REM CALL "%_COMPUTING%\201_HTMLPages.cmd" D
REM ECHO.
REM ECHO.
REM ECHO HTML output created with success.
REM PAUSE
REM GOTO MENU


REM ----------------------------
REM Backup documents. A REVOIR !
REM ----------------------------
REM python deletelastrundate 123456797
REM IF NOT ERRORLEVEL 1 (
REM     CALL "%_COMPUTING%\start.cmd" 2
REM )
REM PAUSE
REM GOTO MENU


REM ----------------------
REM Backup python scripts.
REM ----------------------
REM CALL "%_COMPUTING%\start.cmd" 6
REM PAUSE
REM GOTO MENU


REM --------------------
REM Tasks HTML raw view.
REM --------------------
REM STEP10
REM PUSHD "%_PYTHONPROJECT%"
REM python -m Applications.Database.Tasks.View1 > "%_COMPUTING%\Tasks\rawview.html"
REM POPD
REM GOTO MENU


REM ---------------------------
REM LastRunDates HTML raw view.
REM ---------------------------
rem :STEP11
rem PUSHD "%_PYTHONPROJECT%"
rem python -m Applications.Database.LastRunDates.View1 > "%_COMPUTING%\LastRunDates\rawview.html"
rem POPD
rem GOTO MENU


REM ---------------------------
REM DigitalAudio HTML raw view.
REM ---------------------------
rem :STEP12
rem PUSHD "%_PYTHONPROJECT%"
rem python -m Applications.Database.DigitalAudio.View2 > "%_COMPUTING%\DigitalAudioBase\rawview.html"
rem POPD
rem GOTO MENU


REM ---------------------------
REM Clear "LastRunDates" table.
REM ---------------------------
REM python %_PYTHONPROJECT%\UpdateDatabase.py 7
REM ECHO.
REM ECHO.
REM PAUSE
REM GOTO MENU


REM aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa


REM ==========
REM Exit menu.
REM ==========
:EXIT
POPD
CLS
EXIT /B 0
