:: CMD Enumeration of Windows Systems
@echo off

:: https://www.youtube.com/watch?v=xvFZjo5PgG0
:: Environment Variables
:: %USERNAME% -> Current Username
:: %USERDOMAIN% -> Domain of current logged in user
:: %SYSTEMROOT% -> Points to windows folder "C:\Windows"
:: %APPDATA% -> Points to user roaming directory "C:\Users\Username\Appdata\Roaming"
:: %COMPUTERNAME% -> Computer hostname
:: %HOMEDRIVE% -> Typically "C:\"
:: %HOMEPATH% -> Users directory "C:\Users\Username"
:: %SYSTEMDRIVE% -> Typically "C:\"
:: %TMP% & %TEMP% -> Points to user temp folder "C:\Users\Username\AppData\Local\Temp"
:: %USERPROFILE% -> Points towards user profilefolder "C:\Users\Username"
:: %WINDIR% -> Points to windows directory, "C:\Windows"
:: %ALLUSERSPROFILE% -> Windows Directory, typically "C:\Program Data"
:: %COMPSEC% -> "C:\Windows\system32\cmd.exe"

:: System Information, can also use "ver"
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" 
echo:

:: Updates and Security Patches  
wmic qfe get Caption, Description, HotFixID, InstalledOn 
echo:

:: OS Architecture, 32-bit or 64-bit
wmic os get osarchitecture 
echo:

:: Environmental Variables
set 
echo:

::Current User Permissions
whoami /all 

:: Users
net user 
echo:

:: Groups
net localgroup
echo:

:: Auditing and logging
reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System\Audit
echo:

:: WDiget for plain-text passwords in LSASS
reg query HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential
echo:

:: LSA Protection, Windows 8.1+
reg query HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\LSA /v RunAsPPL
echo:

:: Credentials Guard, Windows 10+ (Enterprise and Education Only)
reg query HKLM\System\CurrentControlSet\Control\LSA /v LsaCfgFlags
echo:

:: Show Shares
net share 
echo:

:: Show sessions, requires admin privileges
::net session
::echo

:: Search for any file beginning with "pass, recusively starting at C:\ directory"
forfiles /P C:\ /s /m pass* -c "cmd /c echo @isdir @fdate @ftime @relpath @path @fsize"
echo:

:: Search for any PDF or "PDF in name" files on C: drive
dir /a /s /b C:\*pdf*
echo:

:: Search for any txt documents with "password" in them in current and sub directories
findstr /SI password *.txt
echo:

:: Find any recently opened files
dir C:\Users\%USERNAME%\AppData\Roaming\Microsoft\Windows\Recent 

:: Powershell History
type %userprofile%\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt