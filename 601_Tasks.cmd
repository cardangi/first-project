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


REM -------------
REM Display menu.
REM -------------
:MENU
python %_PYTHONPROJECT%\Tasks\Tasks.py


REM ----------
REM Exit menu.
REM ----------
IF ERRORLEVEL 99 GOTO EXIT


REM ----------
REM Numbering.
REM ----------
IF ERRORLEVEL 36 (
    python %_PYTHONPROJECT%\Images\Numbering.py
    GOTO MENU
)


REM ----------------------------------
REM Delete "RippingLog" table records.
REM ----------------------------------
IF ERRORLEVEL 35 (
    python %_PYTHONPROJECT%\AudioCD\Delete.py
    GOTO MENU
)


REM --------------------
REM Edit folder content.
REM --------------------
IF ERRORLEVEL 34 (
    python %_PYTHONPROJECT%\Files\FolderContent.py
    GOTO MENU
)


REM ------------------
REM Sort lists tester.
REM ------------------
IF ERRORLEVEL 33 (
    CLS
    PUSHD %_PYTHONPROJECT%
    python -m unittest -v Applications.Tests.module1.Test03
    POPD
    PAUSE
    GOTO MENU
)


REM ----------------------------
REM Default Audio CD rip tester.
REM ----------------------------
IF ERRORLEVEL 32 (
    CLS
    PUSHD %_PYTHONPROJECT%
    python -m unittest -v Applications.Tests.module1.Test01DefaultCDTrack Applications.Tests.module1.Test02DefaultCDTrack Applications.Tests.module1.Test03DefaultCDTrack Applications.Tests.module1.Test04DefaultCDTrack Applications.Tests.module1.Test05DefaultCDTrack
    POPD
    PAUSE
    GOTO MENU
)


REM --------------
REM Parser tester.
REM --------------
IF ERRORLEVEL 31 (
    CLS
    PUSHD %_PYTHONPROJECT%
    python -m unittest -v Applications.Tests.module2
    POPD
    PAUSE
    GOTO MENU
)


REM ----------------------------------
REM Update "RippingLog" table records.
REM ----------------------------------
IF ERRORLEVEL 30 (
    python %_PYTHONPROJECT%\AudioCD\Update.py
    GOTO MENU
)


REM ---------------------------
REM Regular expressions tester.
REM ---------------------------
IF ERRORLEVEL 29 (
    CLS
    PUSHD %_PYTHONPROJECT%
    python -m unittest -v Applications.Tests.module1.TestRegex
    POPD
    PAUSE
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 200* bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 28 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1222562470
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 2009 bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 27 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1068554868
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 201* bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 26 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1306312508
    GOTO MENU
)


REM ----------------------------------------
REM Springsteen 2016 bootlegs series backup.
REM ----------------------------------------
IF ERRORLEVEL 25 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1066663185
    GOTO MENU
)


REM -------------------
REM Convert Unix epoch.
REM -------------------
IF ERRORLEVEL 24 (
    REM python Applications`convertUnixEpoch`L.py
    REM IF ERRORLEVEL 11 GOTO MENU
    GOTO MENU
)


REM -------------------------
REM Get Unix epoch from date.
REM -------------------------
IF ERRORLEVEL 23 (
    REM python Applications`getUnixEpoch`L.py
    GOTO MENU
)


REM ----------------------
REM Timestamp audio files.
REM ----------------------
IF ERRORLEVEL 22 (
    REM python AudioFiles`Taggingtime`L.py
    GOTO MENU
)


REM -------------------
REM Rename audio files.
REM -------------------
IF ERRORLEVEL 21 (
    REM python AudioFiles`renameFiles`L.py
    GOTO MENU
)


REM ----------------------------------
REM Copy audio files from audio drive.
REM ----------------------------------
IF ERRORLEVEL 20 (
    REM REM CALL "G:\Computing\802_copyAudioFiles.cmd"
    GOTO MENU
)


REM ----------------------------------
REM Import audio files to audio drive.
REM ----------------------------------
IF ERRORLEVEL 19 (
    REM CALL "G:\Computing\801_importAudioFiles.cmd"
    GOTO MENU
)


REM ---------------------------
REM Display geometric sequence.
REM ---------------------------
IF ERRORLEVEL 18 (
    REM python Math`Sequences`L.py G
    GOTO MENU
)


REM ----------------------------
REM Display arithmetic sequence.
REM ---------------------------
IF ERRORLEVEL 17 (
    REM python Math`Sequences`L.py A
    GOTO MENU
)


REM ------------------------
REM Edit RippingLog Content.
REM ------------------------
IF ERRORLEVEL 15 (
    python %_PYTHONPROJECT%\AudioCD\RippedCD`View1.py
    python %_PYTHONPROJECT%\AudioCD\RippedCD`View2.py
    GOTO MENU
)


REM -------------------------------------
REM Digital audio files HTML simple view.
REM -------------------------------------
IF ERRORLEVEL 13 (
    python %_PYTHONPROJECT%\AudioCD\DigitalAudioFiles`View1.py
    IF NOT ERRORLEVEL 1 (
        IF EXIST "%_xmldigitalaudiobase%" (
            java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
            DEL "%_xmldigitalaudiobase%"
        )
    )
    python %_PYTHONPROJECT%\AudioCD\DigitalAudioFiles`View2.py
    python %_PYTHONPROJECT%\Database\DigitalAudioFiles`View3.py
    GOTO MENU
)


REM --------------------------------
REM "LastRunDates" HTML simple view.
REM --------------------------------
IF ERRORLEVEL 12 (
    REM python %_PYTHONPROJECT%\Database`HTMLView`L.py LastRunDates
    GOTO MENU
)


REM --------------------------
REM "Backup" HTML simple view.
REM --------------------------
IF ERRORLEVEL 11 (
    REM python %_PYTHONPROJECT%\Database`HTMLView`L.py Backups
    GOTO MENU
)


REM ----------------------
REM Backup python scripts.
REM ----------------------
IF ERRORLEVEL 10 (
    REM CALL "G:\Computing\start.cmd" 6
    GOTO MENU
)


REM --------------
REM Backup videos.
REM --------------
IF ERRORLEVEL 9 (
    REM CALL "G:\Computing\start.cmd" 12
    GOTO MENU
)


REM -----------------
REM Backup documents.
REM -----------------
IF ERRORLEVEL 8 (

    REM Run Backup.
    python G:\Computing\MyPythonProject\Areca\Areca.py -c documents 1282856126

    REM Update last run date.
    REM python -m Applications.Database.LastRunDates.dbLastRunDates update 123456797

    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2011 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 7 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1484552884
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2010 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 6 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 445045058
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2006 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 5 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1404261019
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2003 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 4 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1557918403
    GOTO MENU
)


REM --------------------------------------
REM Pearl Jam 2000 bootlegs series backup.
REM --------------------------------------
IF ERRORLEVEL 3 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1460302155
    GOTO MENU
)


REM --------------------------
REM Pearl Jam bootlegs backup.
REM --------------------------
IF ERRORLEVEL 2 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 1460302155 1557918403 1404261019 445045058 1484552884
    GOTO MENU
)


REM ---------------------------
REM Default audio files backup.
REM ---------------------------
IF ERRORLEVEL 1 (
    python %_PYTHONPROJECT%\Areca\Areca.py -c music 854796030 1674209532 1196865155 1535780732 204959095
    GOTO MENU
)


REM ==========
REM Exit menu.
REM ==========
:EXIT
CLS
EXIT /B 0
