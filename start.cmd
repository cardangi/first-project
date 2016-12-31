@ECHO off
REM Exécuté depuis le scheduler windows avec les paramètres 1 3 4 6 7 9 10 11 13.


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
SET _videos=%USERPROFILE%\videos


REM ===============
REM Main algorithm.
REM ===============


REM     ------
REM  2. Tasks.
REM     ------
:MAIN
IF "%~1" EQU "" EXIT /B %ERRORLEVEL%
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "3" GOTO STEP3
IF "%~1" EQU "4" GOTO STEP4
IF "%~1" EQU "6" GOTO STEP6
IF "%~1" EQU "7" GOTO STEP7
IF "%~1" EQU "9" GOTO STEP9
IF "%~1" EQU "10" GOTO STEP10
IF "%~1" EQU "11" GOTO STEP11
IF "%~1" EQU "12" GOTO STEP12
IF "%~1" EQU "13" GOTO STEP13
IF "%~1" EQU "14" GOTO STEP14
SHIFT
GOTO MAIN


REM     --------------------------
REM  3. Clear temporary directory.
REM     --------------------------
REM     /DB#1: removes files older than or equal to 1 day.
:STEP1
XXCOPY %TEMP%\ /S /RS /DB#1 /R /H /Y /PD0 /Fo:%TEMP%\ClearTemp.lst /FM:L
SHIFT
GOTO MAIN


REM     ------
REM  4. Dummy.
REM     ------
:STEP2
SHIFT
GOTO MAIN


REM     ---------------------------------------------------------
REM  5. Backup "sandboxie.ini" and others single important files.
REM     ---------------------------------------------------------
REM     /Y:  suppresses prompt when overwriting existing files.
REM     /BI: backs up incrementally. Different, by time/size, files only.
:STEP3
IF EXIST "y:" (
    XXCOPY "%WINDIR%\sandboxie.ini" "y:\" /KS /Y /BI /FF
    XXCOPY "%_MYDOCUMENTS%\comptes.gnucash" "y:\" /KS /Y /BI /FF
    XXCOPY "%_MYDOCUMENTS%\comptes.xlsx" "y:\" /KS /Y /BI /FF
    XXCOPY "%_COMPUTING%\database.db" "y:\" /KS /Y /BI /FF
    XXCOPY "%_COMPUTING%\logging.yml" "y:\" /KS /Y /BI /FF
    XXCOPY "%_COMPUTING%\.gitignore" "y:\" /KS /Y /BI /FF
)
SHIFT
GOTO MAIN

REM     -----------------------
REM  6. Remove Areca log files.
REM     -----------------------
REM     /DB#8: removes files older than or equal to 8 days.
:STEP4
IF EXIST %_BACKUP% XXCOPY %_BACKUP%\*\*.log /RS /DB#8 /R /H /Y /PD0 /ED /Fo:%TEMP%\RemoveArecaLog.lst /FM:L
SHIFT
GOTO MAIN


REM     ---------------------------------
REM  8. Backup "mypythonproject" content.
REM     ---------------------------------
REM     /DB#10: removes files older than or equal to 10 days.
REM     /IA   : copies file(s) only if destination directory must not exist.
:STEP6
IF EXIST y:\python (
    XXCOPY y:\python\ /S /RS /FC /DB#10 /R /H /Y /PD0 /Fo:%TEMP%\RemovepythonScripts.lst /FM:L
    XXCOPY %_PYTHONPROJECT%\*\ y:\python\/$ymmdd$\ /X:*.pyc /X:*.xml /IA /KS /BI /FF /Y /R /Fo:%TEMP%\pythonScriptsBackup.lst /FM:DTZA /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     -------------------------------
REM  9. Backup both CSS ans XSL sheets.
REM     -------------------------------
REm     /SX: flattens subdirectories.
:STEP7
IF EXIST "y:" (
    XXCOPY %_COMPUTING%\*.xsl y:\ /SX /KS /Y /BI /FF
    XXCOPY %_COMPUTING%\*.css y:\ /SX /KS /Y /BI /FF
)
SHIFT
GOTO MAIN


REM     ---------------------
REM 10. Backup PDF documents.
REM     ---------------------
:STEP9
IF EXIST "z:\Z123456789" XXCOPY "%_MYDOCUMENTS%\Administratif\*\*.pdf" "z:\Z123456789\" /KS /BI /FF /Y /R /Fo:%TEMP%\Administratif.lst /FM:DTZA /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -----------------
REM 11. Clone album arts.
REM     -----------------
:STEP10
IF EXIST "z:\Z123456790" XXCOPY "%_MYDOCUMENTS%\Album Art\*\*.jpg" "z:\Z123456790\" /CLONE /Fo:%TEMP%\AlbumArt.lst /FM:DTZA /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     ---------------------------
REM 12. Clone MP3Tag configuration.
REM     ---------------------------
:STEP11
IF EXIST "z:\Z123456791" XXCOPY "%APPDATA%\MP3Tag\" "z:\Z123456791\" /X:*.log /X:*.zip /CLONE /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -------------
REM 13. Clone videos.
REM     -------------
:STEP12
IF EXIST "z:\Z123456792" XXCOPY "%_videos%\*.mp4" "z:\Z123456792\" /CLONE /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN


REM     -------------------------------
REM 14. Delete GNUCash sandbox content.
REM     -------------------------------
:STEP13
python G:\Computing\MyPythonProject\Tasks\Task01.py
SHIFT
GOTO MAIN


REM     ---------------------------------------
REM 15. Clone "H:" to "\\Diskstation\pictures".
REM     ---------------------------------------
:STEP14

REM -->  1. Clone "H:" to "\\Diskstation\pictures". Don't delete extra files.
REM         Exclude "RECYCLER".
REM         Exclude "$RECYCLE.BIN".
REM         Exclude "SYSTEM VOLUME INFORMATION".
REM         Exclude "IPHONE".
REM         Exclude "RECOVER".
XXCOPY "H:\*\*.jpg" "\\Diskstation\pictures" /X:*recycle*\ /X:*volume*\ /X:iphone\ /X:recover\ /CLONE /Z0 /oA:%_XXCOPYLOG%

REM -->  2. Reverse both source and destination. Then remove brand new files but exclude "#recycle" folder.
REM         This trick allows to remove files from "\\Diskstation\pictures" not present in "H:".And preserve "#recycle"!
XXCOPY "\\Diskstation\pictures" "H:\" /RS /BN /PD0 /S /RSY /X:#recycle\ /oA:%_XXCOPYLOG%

SHIFT
GOTO MAIN


REM     ------------------------------------
REM 16. Clone "F:" to "\\Diskstation\music".
REM     ------------------------------------
REM     Only FLAC.
:STEP15
REM XXCOPY "F:\*\Springsteen*\*\*.flac" %TEMP% /CLONE /Z0 /oA:%_XXCOPYLOG%
SHIFT
GOTO MAIN
