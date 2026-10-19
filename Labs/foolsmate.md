---
lab: "Foolsmate"
date: "2026-10-14"
platform: "TryHackMe"
difficulty: "Easy"
---
# Room link: https://tryhackme.com/room/foolsmate

![](Labs/Attachments/Pasted%20image%2020261014022806.png)

# Nmap scan

```bash
$ sudo nmap -sCVT -p- --min-rate 1000 -T4 -oN nmap.txt foolsmate.thm 
[sudo] password for zephyr: 
Starting Nmap 7.99 ( https://nmap.org ) at 2026-10-14 02:18 +0800
Stats: 0:00:19 elapsed; 0 hosts completed (1 up), 1 undergoing Connect Scan
Connect Scan Timing: About 27.87% done; ETC: 02:19 (0:00:49 remaining)
Nmap scan report for foolsmate.thm (10.145.172.128)
Host is up (0.21s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 40:3e:4d:67:0d:8c:d5:5b:d4:cc:c8:24:da:67:df:43 (ECDSA)
|_  256 35:d2:ee:30:5f:e3:a7:14:91:85:be:dc:55:27:b8:3a (ED25519)
80/tcp open  http    Node.js Express framework
|_http-title: Endgame Trainer
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Website shows a Mate in one chess puzzle. The problem is that when I move the obvious choice, Rook to A8, a prompt appears that doesn't allow me to finish the puzzle. 

![](Labs/Attachments/Pasted%20image%2020261014023104.png)

I used `Burpsuite` to see if I can modify some request. I moved the Rook from A1 to B1 and capture the request `/api/move` to the repeater.

![](Labs/Attachments/Pasted%20image%2020261014023501.png)

I simply changed `b1` to `a8` which is the move to win the game and send it.

![](Labs/Attachments/Pasted%20image%2020261014023718.png)

Flag obtained. 