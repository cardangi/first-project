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
REM SET _documentsID=123456797
SET _gnucashID=123456798


REM ==================
REM Initializations 3.
REM ==================
SET _wsdocuments=%_BACKUP%\workspace.documents
SET _wsmusic=%_BACKUP%\workspace.music
SET _wsvideos=%_BACKUP%\workspace.videos
REM SET _targetsfile=%_COMPUTING%\documentsbackuptargets.txt
SET _workdir=%TEMP%\tmp-Xavier
SET _arecabackuplog=%_COMPUTING%\ArecaBackupLog.txt
SET _videos=%USERPROFILE%\videos
SET _filesrotation=%_COMPUTING%\filesrotation.cmd


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
rem IF "%_yready%%_zready%" EQU "YY" (

rem     PUSHD %_PYTHONPROJECT%
rem     python -m Applications.Database.dbLastRunDates delta "%_documentsID%" -t "5"
rem     IF NOT ERRORLEVEL 1 (
rem         FOR /F "usebackq delims=; eol=# tokens=2" %%a IN ("%_targetsfile%") DO (
rem             IF EXIST "%_arecabackuplog%" (
rem                 IF EXIST "%_filesrotation%" CALL "%_filesrotation%" 5 500000 "%_arecabackuplog%"
rem             )
rem             (
rem                 ECHO.
rem                 ECHO -------------
rem                 ECHO Start backup.
rem                 ECHO -------------
rem                 ECHO INFO -  - !date! !time!
rem             ) >> %_arecabackuplog%
rem             "C:\Program Files\Areca\areca_cl.exe" backup -c -wdir "%_workdir%" -config "%_wsdocuments%\%%a.bcfg" >> %_arecabackuplog%
rem             IF NOT ERRORLEVEL 1 (
rem                 IF "%_xready%" EQU "Y" (
rem                     IF EXIST "%_XXCOPYLOG%" (
rem                         IF EXIST "%_filesrotation%" CALL "%_filesrotation%" 5 150000 "%_XXCOPYLOG%"
rem                     )
rem                     XXCOPY z:\%%a\ x:\%%a\ /CLONE /oA:%_XXCOPYLOG%
rem                 )
rem             )
rem         )
rem         python -m Applications.Database.dbLastRunDates update "%_documentsID%"
rem     )
rem     POPD

rem )
SHIFT
GOTO MAIN


REM     -----------------------
REM  5. Backup "sandboxie.ini".
REM     -----------------------
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
:STEP4
IF "%_yready%" EQU "Y" XXCOPY %_BACKUP%\*\*.log /RS /DB#8 /R /H /Y /PD0 /ED /Fo:%TEMP%\RemoveArecaLog.lst /FM:L
SHIFT
GOTO MAIN


REM     ---------------------------
REM  7. Backup "zoho docs" content.
REM     ---------------------------
:STEP5
IF "%_yready%" EQU "Y" XXCOPY "%_MYDOCUMENTS%\zoho docs" "y:\" /KS /Y /BI /FF
SHIFT
GOTO MAIN


REM     ---------------------------------
REM  8. Backup "mypythonproject" content.
REM     ---------------------------------
:STEP6
IF "%_yready%" EQU "Y" (
    IF EXIST y:\Python XXCOPY y:\Python\ /S /RS /FC /DB#10 /R /H /Y /PD0 /Fo:%TEMP%\RemovePythonScripts.lst /FM:L
    IF EXIST "%_XXCOPYLOG%" (
        IF EXIST "%_filesrotation%" CALL "%_filesrotation%" 5 150000 "%_XXCOPYLOG%"
    )
    XXCOPY %_PYTHONPROJECT%\*\ y:\Python\/$ymmdd$\ /X:*.pyc /X:*.xml /KS /BI /FF /Y /R /Fo:%TEMP%\PythonBackup.lst /FM:DTZA /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     -------------------------------
REM  9. Backup both CSS ans XSL sheets.
REM     -------------------------------
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
    IF EXIST "%_XXCOPYLOG%" (
        IF EXIST "%_filesrotation%" CALL "%_filesrotation%" 5 150000 "%_XXCOPYLOG%"
    )
    XXCOPY %_MYDOCUMENTS%\Administratif\*\*.pdf z:\Z123456789\ /KS /BI /FF /Y /R /Fo:%TEMP%\Administratif.lst /FM:DTZA /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     --------------------------
REM 11. Clone "album art" content.
REM     --------------------------
:STEP10
IF "%_zready%" EQU "Y" (
    IF EXIST "%_XXCOPYLOG%" (
        IF EXIST "%_filesrotation%" CALL "%_filesrotation%" 5 150000 "%_XXCOPYLOG%"
    )
    XXCOPY "%_MYDOCUMENTS%\Album Art\*\*.jpg" z:\Z123456790\ /CLONE /Fo:%TEMP%\AlbumArt.lst /FM:DTZA /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     ---------------------------
REM 12. Clone MP3Tag configuration.
REM     ---------------------------
:STEP11
IF "%_zready%" EQU "Y" (
    IF EXIST "%_XXCOPYLOG%" (
        IF EXIST "%_filesrotation%" CALL "%_filesrotation%" 5 150000 "%_XXCOPYLOG%"
    )
    XXCOPY "%APPDATA%\MP3Tag\" z:\Z123456791\ /X:*.log /X:*.zip /CLONE /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     --------------
REM 13. Backup videos.
REM     --------------
:STEP12
IF "%_zready%" EQU "Y" (
    IF EXIST "%_XXCOPYLOG%" (
        IF EXIST "%_filesrotation%" CALL "%_filesrotation%" 5 150000 "%_XXCOPYLOG%"
    )
    XXCOPY "%_videos%\*.mp4" z:\Z123456792\ /CLONE /oA:%_XXCOPYLOG%
)
SHIFT
GOTO MAIN


REM     -------------------------------
REM 14. Delete GNUCash sandbox content.
REM     -------------------------------
:STEP13
REM PUSHD %_PYTHONPROJECT%
REM python -m Applications.Database.dbLastRunDates delta "%_gnucashID%" -t "10" && "C:\Program Files\Sandboxie\Start.exe" /box:GNUCash delete_sandbox_silent && python -m Applications.Database.dbLastRunDates update "%_gnucashID%"
REM POPD
SHIFT
GOTO MAIN