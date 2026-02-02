Set oWS = WScript.CreateObject("WScript.Shell")
Set oFSO = CreateObject("Scripting.FileSystemObject")

sScriptDir = oFSO.GetParentFolderName(WScript.ScriptFullName)
sLinkFile = oWS.SpecialFolders("Programs") & "\SAP AI Core LLM Proxy.lnk"

Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "pwsh.exe"
oLink.Arguments = "-ExecutionPolicy Bypass -NoExit -File """ & sScriptDir & "\run-proxy.ps1"""""
oLink.WorkingDirectory = sScriptDir
oLink.Description = "SAP AI Core LLM Proxy Server"
oLink.IconLocation = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe,0"
oLink.Save

WScript.Echo "Shortcut created successfully in Start Menu!"
WScript.Echo "Location: " & sLinkFile
