@ECHO off


REM
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET me=%~n0
SET myparent=%~dp0


REM ==================
REM Initializations 2.
REM ==================
SET _xmldigitalaudiobase=%TEMP%\digitalaudiobase.xml
SET _digitalaudiobase=%_COMPUTING%\digitalaudiobase\digitalaudiobase
SET _xmlbootlegs1=%TEMP%\bootlegs.xml
SET _xmlbootlegs2=%TEMP%\output.xml
SET _bootlegs=%_COMPUTING%\bootlegs\bootlegs


REM ===============
REM Main algorithm.
REM ===============


REM     ------
REM  1. Tasks.
REM     ------
:MAIN
IF "%~1" EQU "" EXIT /B %ERRORLEVEL%
IF /I "%~1" EQU "A" GOTO STEP1
IF /I "%~1" EQU "B" GOTO STEP2
IF /I "%~1" EQU "C" GOTO STEP3
IF /I "%~1" EQU "D" GOTO STEP4
IF /I "%~1" EQU "E" GOTO STEP5
SHIFT
GOTO MAIN


REM     ----------------------
REM  2. DigitalAudio TXT view.
REM     ----------------------
:STEP1
PUSHD "%_PYTHONPROJECT%"
python -m Applications.Database.DigitalAudio.View3 > "%_COMPUTING%\DigitalAudioBase\txtview.txt"
POPD
SHIFT
GOTO MAIN


REM     -----------------------------
REM  3. DigitalAudio HTML fancy view.
REM     -----------------------------
:STEP2
PUSHD "%_PYTHONPROJECT%"
python -m Applications.Database.DigitalAudio.View1
IF NOT ERRORLEVEL 1 (
    IF EXIST "%_xmldigitalaudiobase%" (
        java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmldigitalaudiobase%" -xsl:"%_digitalaudiobase%.xsl" -o:"%_digitalaudiobase%.html"
        DEL "%_xmldigitalaudiobase%"
    )
)
POPD
SHIFT
GOTO MAIN


REM     ---------------------------
REM  4. RippingLog HTML fancy view.
REM     ---------------------------
:STEP3
PUSHD "%_PYTHONPROJECT%"
python -m Applications.Database.RippingLog.View1 > "%_COMPUTING%\RippingLog\rippinglog.html"
POPD
SHIFT
GOTO MAIN


REM     ------------------------
REM  5. HTML pearl jam bootlegs.
REM     ------------------------
:STEP4
IF EXIST "%_xmlbootlegs1%" (
    PUSHD "%_PYTHONPROJECT%"
    python -m Applications.Database.XMLBootlegs
    IF NOT ERRORLEVEL 1 (
        IF EXIST "%_xmlbootlegs%" (
            java -cp "%_SAXON%" net.sf.saxon.Transform -s:"%_xmlbootlegs2%" -xsl:"%_bootlegs%.xsl" -o:"%_bootlegs%.html"
        )
        DEL "%_xmlbootlegs2%"
    )
    DEL "%_xmlbootlegs1%"
    POPD
)
SHIFT
GOTO MAIN


REM     -----------------
REM  6. Audio files list.
REM     -----------------
:STEP5
PUSHD "%_PYTHONPROJECT%"
python -m Applications.CDRipper.AudioDigitalFilesList "G:\Computing\AudioDigitalFilesList.xav" --dir "f:\\" --ext ape flac m4a mp3 ofr ogg
POPD
SHIFT
GOTO MAIN