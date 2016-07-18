option explicit

' ==========
' Constants.
' ==========
const outputFile = "c:\users\xavier\appdata\local\temp\serial.xav"

' ==========
' Variables.
' ==========
dim fso, d, dc, f, line

' ===============
' Main algorithm.
' ===============
set fso = CreateObject("Scripting.FileSystemObject")

' -------------------
' Remove output file.
' -------------------
if fso.FileExists(outputFile) then
	fso.DeleteFile(outputFile)
end if

' ---------------------------
' Retrieve drives properties.
' ---------------------------
set f = fso.OpenTextFile(outputFile, 2, true, -1)

' Header.
f.WriteLine("DriveLetter" & vbTab & "VolumeName" & vbTab  & "SerialNumber" & vbTab & "Free Space (Kbytes)" & vbTab & "Type" & vbTab & "Ready")
f.WriteLine("-----------" & vbTab & "----------" & vbTab & "-------------" & vbTab & "-------------------" & vbTab & "----" & vbTab & "-----")

' Detail.
set dc = fso.Drives
For Each d in dc
	if d.IsReady then
		line = d.DriveLetter & vbTab & vbTab & d.VolumeName
		if Len(d.VolumeName) < 8 then
			line = line & vbTab
		end if
		line = line & vbTab & d.SerialNumber & vbTab & d.FreeSpace/1024
		if Len(d.FreeSpace/1024) < 8 then
			line = line & vbTab
		end if
		line = line & vbTab & vbTab & d.DriveType & vbTab & d.IsReady
		f.WriteLine(line)
	end if
Next

f.Close