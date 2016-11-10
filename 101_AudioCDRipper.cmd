@ECHO off


SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _json=%TEMP%\arguments.json
SET _jsonrippinglog=%TEMP%\rippinglog.json
SET _htmlrippinglog=%_COMPUTING%\rippingLog\rippinglog.html
SET _jsondigitalaudiobase=%TEMP%\digitalaudiodatabase.json
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
IF "%~1" EQU "5" GOTO STEP5
IF "%~1" EQU "6" GOTO STEP6
SHIFT
GOTO MAIN


REM        ------------
REM  1 --> Ripping log.
REM        ------------
:STEP1
IF EXIST "%_jsonrippinglog%" (
    python %_PYTHONPROJECT%\CDRipper`AudioCD`RippingLog`L.py
    DEL "%_jsonrippinglog%"
)
SHIFT
GOTO MAIN


REM        -----------------------
REM  2 --> Digital audio database.
REM        -----------------------
:STEP2
IF EXIST "%_jsondigitalaudiobase%" (
    PUSHD "%_PYTHONPROJECT%"
    python -m Applications.Database.DigitalAudio.insert "%_jsondigitalaudiobase%"
    POPD
    DEL "%_jsondigitalaudiobase%"
)
SHIFT
GOTO MAIN


REM        -------------------------
REM  3 --> Update Ripping log views.
REM        -------------------------
:STEP3
python %_PYTHONPROJECT%\Database`HTMLView`L.py RippingLog
IF NOT ERRORLEVEL 1 (
    REM PUSHD %_PYTHONPROJECT%
    REM python -m Applications.Database.RippingLog.View2
    REM POPD
)
SHIFT
GOTO MAIN


REM        ------------------------------------
REM  4 --> Update Digital Audio database views.
REM        ------------------------------------
:STEP4
python %_PYTHONPROJECT%\Database`HTMLView`L.py DigitalAudio
IF NOT ERRORLEVEL 1 (
    PUSHD "%_PYTHONPROJECT%"
    python -m Applications.Database.DigitalAudio.View1
    POPD
    IF EXIST "%_xmldigitalaudiobase%" (
        java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
        DEL "%_xmldigitalaudiobase%"
    )
)
SHIFT
GOTO MAIN


REM        -----------------
REM  5 --> Copy audio files.
REM        -----------------
:STEP5
START "" /B /D %_COMPUTING% 102_AudioCDRipper.cmd "%_json%" 30
SHIFT
GOTO MAIN


REM        -------------------
REM  6 --> Change "album" tag.
REM        -------------------
:STEP6
START "" /B /D %_COMPUTING% 104_AudioCDRipper.cmd 60
SHIFT
GOTO MAIN