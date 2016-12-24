@ECHO off
REM Exécuté depuis le scheduler windows avec les paramètres 1 2 3 4 5 6 7 9 10 11 13.


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
SET _xready=N
SET _yready=N
SET _zready=N


REM ==================
REM Initializations 3.
REM ==================
SET _documentsID=123456797
SET _gnucashID=123456798
SET _videos=%USERPROFILE%\videos


REM ===============
REM Main algorithm.
REM ===============


REM     -----------------------------------------
REM  1. Check if both Y and Z drives are present.
REM     -----------------------------------------
FOR /F "usebackq skip=1 delims=:" %%i IN (`wmic logicaldisk get caption`) DO (
    IF "%%i" EQU "X" SET _xready=Y
    IF "%%i" EQU "Y" SET _yready=Y
    IF "%%i" EQU "Z" SET _zready=Y
)


REM     ------
REM  2. Tasks.
REM     ------
:MAIN
IF "%~1" EQU "" EXIT /B %ERRORLEVEL%
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "2" GOTO STEP2
IF "%~1" EQU "3" GOTO STEP3
IF "%~1" EQU "4" GOTO STEP4
IF "%~1" EQU "5" GOTO STEP5
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
:STEP1
XXCOPY %TEMP%\ /S /RS /DB#1 /R /H /Y /PD0 /Fo:%TEMP%\ClearTemp.lst /FM:L
SHIFT
GOTO MAIN


REM     -----------------
REM  4. Backup documents.
REM     -----------------
:STEP2
REM IF "%_yready%%_zready%" EQU "YY" (
    REM PUSHD %_PYTHONPROJECT%
    REM python -m Applications.Database.LastRunDates.dbLastRunDates delta %_documentsID% -t 5
    REM IF NOT ERRORLEVEL 1 (

        REM Run Backup.
        REM python Backups`Areca`L.py documents --check --debug --target 1282856126

        REM Update last run date.
        REM python -m Applications.Database.LastRunDates.dbLastRunDates update %_documentsID%

    REM )
    REM POPD
REM )
SHIFT
GOTO MAIN


REM     -----------------------
REM  5. Backup "sandboxie.ini".
REM     -----------------------
REM     /Y:  suppresses prompt when overwriting existing files.
REM     /BI: backs up incrementally. Different, by time/size, files only.
:STEP3
IF "%_yready%" EQU "Y" (
    XXCOPY "%WINDIR%\sandboxie.ini" "y:\" /KS /Y /BI /FF
    XXCOPY "%_MYDOCUMENTS%\comptes.gnucash" "y:\" /KS /Y /BI /FF
    XXCOPY "%_COMPUTING%\database.db" "y:\" /KS /Y /BI /FF
)
SHIFT
GOTO MAIN

REM     -----------------------
REM  6. Remove Areca log files.
REM     -----------------------
REM     /DB#8: removes files older than or equal to 8 days.
:STEP4
IF "%_yready%" EQU "Y" XXCOPY %_BACKUP%\*\*.log /RS /DB#8 /R /H /Y /PD0 /ED /Fo:%TEMP%\RemoveArecaLog.lst /FM:L
SHIFT
GOTO MAIN


REM     ---------------------------
REM  7. Backup "zoho docs" content.
REM     ---------------------------
:STEP5
REM IF "%_yready%" EQU "Y" XXCOPY "%_MYDOCUMENTS%\zoho docs" "y:\" /KS /Y /BI /FF
SHIFT
GOTO MAIN


REM     ---------------------------------
REM  8. Backup "mypythonproject" content.
REM     ---------------------------------
REM     /DB#10: removes files older than or equal to 10 days.
:STEP6
IF "%_yready%" EQU "Y" (
    IF EXIST y:\Python XXCOPY y:\Python\ /S /RS /FC /DB#10 /R /H /Y /PD0 /Fo:%TEMP%\RemovePythonScripts.lst /FM:L
    XXCOPY %_PYTHONPROJECT%\*\ y:\Python\/$ymmdd$\ /X:*.pyc /X:*.xml /KS /BI /FF /Y /R /Fo:%TEMP%\PythonBackup.lst /FM:DTZA /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     -------------------------------
REM  9. Backup both CSS ans XSL sheets.
REM     -------------------------------
REm     /SX: flattens subdirectories.
:STEP7
IF "%_yready%" EQU "Y" (
    XXCOPY %_COMPUTING%\*.xsl y:\ /SX /KS /Y /BI /FF
    XXCOPY %_COMPUTING%\*.css y:\ /SX /KS /Y /BI /FF
)
SHIFT
GOTO MAIN


REM     ---------------------
REM 10. Backup PDF documents.
REM     ---------------------
:STEP9
IF "%_zready%" EQU "Y" (
    XXCOPY %_MYDOCUMENTS%\Administratif\*\*.pdf z:\Z123456789\ /KS /BI /FF /Y /R /Fo:%TEMP%\Administratif.lst /FM:DTZA /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     --------------------------
REM 11. Clone "album art" content.
REM     --------------------------
:STEP10
IF "%_zready%" EQU "Y" (
    XXCOPY "%_MYDOCUMENTS%\Album Art\*\*.jpg" z:\Z123456790\ /CLONE /Fo:%TEMP%\AlbumArt.lst /FM:DTZA /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     ---------------------------
REM 12. Clone MP3Tag configuration.
REM     ---------------------------
:STEP11
IF "%_zready%" EQU "Y" (
    XXCOPY "%APPDATA%\MP3Tag\" z:\Z123456791\ /X:*.log /X:*.zip /CLONE /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     --------------
REM 13. Backup videos.
REM     --------------
:STEP12
IF "%_zready%" EQU "Y" (
    XXCOPY "%_videos%\*.mp4" z:\Z123456792\ /CLONE /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     -------------------------------
REM 14. Delete GNUCash sandbox content.
REM     -------------------------------
:STEP13
REM PUSHD %_PYTHONPROJECT%
REM python -m Applications.Database.LastRunDates.dbLastRunDates delta "%_gnucashID%" -t 10 && "C:\Program Files\Sandboxie\Start.exe" /box:GNUCash delete_sandbox_silent && python -m Applications.Database.LastRunDates.dbLastRunDates update "%_gnucashID%"
REM POPD
SHIFT
GOTO MAIN


REM     ---------------------------------------
REM 15. Clone "H:" to "\\Diskstation\pictures".
REM     ---------------------------------------
:STEP14

REM -->  1. Clone "H:" to "\\Diskstation\pictures". Don't delete extra files.
XXCOPY "C:\Users\Xavier\Downloads\h\" "%TEMP%\h\" /CLONE /I /Z0 /oA:%_XXCOPYLOG%

REM -->  2. Reverse both source and destination. Only remove brand new files. Exclude "#recycle folder".
XXCOPY "%TEMP%\h\" "C:\Users\Xavier\Downloads\h\" /RS /BN /PD0 /S /RSY /X:#recycle\ /oA:%_XXCOPYLOG%

SHIFT
GOTO MAIN


REM     ---------------------------------------
REM 15. Clone "H:" to "\\Diskstation\pictures".
REM     ---------------------------------------
:STEP15

REM -->  1. Clone "H:" to "\\Diskstation\pictures". Don't delete extra files.
XXCOPY "H:\" "\\Diskstation\pictures" /CLONE /Z0 /oA:%_XXCOPYLOG%

REM -->  2. Reverse both source and destination. Then remove brand new files but exclude "#recycle" folder.
REM         This trick allows to remove files from "\\Diskstation\pictures" not present in "H:".
XXCOPY "\\Diskstation\pictures" "H:\" /RS /BN /PD0 /S /RSY /X:#recycle\ /oA:%_XXCOPYLOG%

SHIFT
GOTO MAIN
