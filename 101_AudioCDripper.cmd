@ECHO off


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
SET _workdir=%TEMP%\tmp-Xavier
SET _music=%_BACKUP%\workspace.music
SET _rippingbase=%TEMP%\rippingdatabase
SET _htmlrippinglog=%_COMPUTING%\rippinglog.html
SET _txtdigitalaudiobase=%TEMP%\digitalaudiodatabase.txt
SET _xmldigitalaudiobase=%TEMP%\digitalaudiobase.xml
SET _digitalaudiobase=%_COMPUTING%\digitalaudiobase\digitalaudiobase


REM ===============
REM Main algorithm.
REM ===============


:MAIN
IF "%~1" EQU "" EXIT /B %ERRORLEVEL%
IF "%~1" EQU "1" GOTO STEP1
IF "%~1" EQU "2" GOTO STEP2
IF "%~1" EQU "3" GOTO STEP3
IF "%~1" EQU "4" GOTO STEP4
SHIFT
GOTO MAIN


REM  1 --> Audio CD ripping database.
:STEP1
IF EXIST "%_rippingbase%" (
    SET _first=Y
    FOR /F "usebackq tokens=1-9 delims=;" %%a IN ("%_rippingbase%") DO (

        IF "!_first!"=="Y" (
            SET _first=N
            PUSHD "%_PYTHONPROJECT%"
            python -m Applications.CDRipper.AudioCDRippingLog insert "%%~a" %%~b "%%~c" "%%~d" %%~e %%~f "%%~i"
            POPD
        )

    )
    DEL "%_rippingbase%"
)
SHIFT
GOTO MAIN


REM  2 --> Digital audio database.
:STEP2
IF EXIST "%_txtdigitalaudiobase%" (
    PUSHD "%_PYTHONPROJECT%"
    python -m Applications.Database.DigitalAudio.insert "%_txtdigitalaudiobase%"
    POPD
    DEL "%_txtdigitalaudiobase%"
)
SHIFT
GOTO MAIN


REM  3 --> Ripping database HTML page.
:STEP3
PUSHD "%_PYTHONPROJECT%"
python -m Applications.Database.RippingLog.View1 > %_htmlrippinglog%
POPD
SHIFT
GOTO MAIN


REM  4 --> Digital audio database HTML page.
:STEP4
PUSHD "%_PYTHONPROJECT%"
python -m Applications.Database.DigitalAudio.View1
POPD
IF EXIST "%_xmldigitalaudiobase%" (
    java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
    DEL "%_xmldigitalaudiobase%"
)
SHIFT
GOTO MAIN
