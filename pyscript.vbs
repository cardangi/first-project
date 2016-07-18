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

'	Does "pyscript.py" exist?
For Each drv in fso.Drives
	if Lcase(drv.Driveletter) = "g" and drv.IsReady then
		if fso.FileExists(wshell.ExpandEnvironmentStrings("%TEMP%") & "\pyscript.py") then

'			Exécution du script python "pyscript.py".
			wshell.Run """" & "C:\Python34\python.exe" & """ """ & "G:\Documents\MyPythonProject\RunScript.py" & """", 0, False

'			Suppression du script python "pyscript.py".
'			set pyscript = fso.GetFile(wshell.ExpandEnvironmentStrings("%TEMP%") & "\pyscript.py")
'			pyscript.Delete

		end if
	end if
Next
