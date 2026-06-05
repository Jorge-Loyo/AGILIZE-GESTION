Set WshShell = WScript.CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")

Set oShortcut = WshShell.CreateShortcut(strDesktop & "\Agilize Gestion.lnk")
oShortcut.TargetPath = "C:\Desarrollo\Agilize-Gestion\venv\Scripts\pythonw.exe"
oShortcut.Arguments = "main.py"
oShortcut.WorkingDirectory = "C:\Desarrollo\Agilize-Gestion"
oShortcut.WindowStyle = 1
oShortcut.Description = "Agilize Gestion - Sistema Empresarial"
oShortcut.Save
