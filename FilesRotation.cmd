@ECHO off


REM
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION


REM ==================
REM Initializations 1.
REM ==================
SET _me=%~n0
SET _myparent=%~dp0


REM ===============
REM Main algorithm.
REM ===============
FOR %%i IN ("%~3") DO (
    SET _size=%%~zi
    SET _fil=%%~dpni
    SET _nam=%%~ni
    SET _ext=%%~xi
)
IF %_size% GTR %~2 (
    FOR /L %%i IN (%~1, -1, 1) DO (
        SET /A _i=%%i
        SET /A _j=%%i+1
        IF %%i EQU %~1 (
            IF EXIST "%_fil%!_i!%_ext%" DEL "%_fil%!_i!%_ext%"
        )
        IF %%i LSS %~1 (
            IF %%i GEQ 1 (
                IF EXIST "%_fil%!_i!%_ext%" REN "%_fil%!_i!%_ext%" %_nam%!_j!%_ext%"
            )
        )
    )
    IF EXIST "%~3" REN "%~3" %_nam%1%_ext%"
)
EXIT /B 0