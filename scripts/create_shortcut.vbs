Set WshShell = WScript.CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")

Set oShortcut = WshShell.CreateShortcut(strDesktop & "\Agilize Gestion.lnk")
oShortcut.TargetPath = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\AgilizeGestion\venv\Scripts\pythonw.exe"
oShortcut.Arguments = "main.py"
oShortcut.WorkingDirectory = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\AgilizeGestion"
oShortcut.WindowStyle = 1
oShortcut.Description = "Agilize Gestion - Sistema Empresarial"
oShortcut.Save
