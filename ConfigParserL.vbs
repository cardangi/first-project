option explicit


' ==========
' Variables.
' ==========
dim fso, wshell, drv


' ===============
' Main algorithm.
' ===============

'	Initialisations.
	set fso = CreateObject("Scripting.FileSystemObject")
	set wshell = WScript.CreateObject("WScript.Shell")

'	Is "G" drive ready?
	For Each drv in fso.Drives
		if Lcase(drv.Driveletter) = "g" and drv.IsReady then
			wshell.Run """" & "C:\Python34\python.exe" & """ """ & "G:\Documents\MyPythonProject\Launchers\Tasks\ConfigParserL.py" & """ --debug", 0, True
		end if
	Next

' Reset database flags.
' wshell.Run """" & "C:\Python34\python.exe" & """ """ & "G:\Documents\MyPythonProject\Launchers\Database\UpdateFlagsL.py" & """ 1234567 1234568 1234569 12345670 -v 0", 0, True

' Remove audio tags temporary file.
' wshell.Run """" & "C:\Python34\python.exe" & """ """ & "G:\Documents\MyPythonProject\Python_S03.py" & """", 0, True
