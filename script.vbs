Set objShell = CreateObject("WScript.Shell")

' Path to the executable file
exePath = "C:\Windows\Help\h.exe"

' Run the executable file
objShell.Run Chr(34) & exePath & Chr(34), 0, False
