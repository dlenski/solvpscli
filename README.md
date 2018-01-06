Table of Contents
=================

  * [solvpscli](#vpn-slice)
    * [Usage](#usage)
      * [List active VPS](#list-active-vps)
      * [`status`](#status)
      * [`ssh` console](#ssh-console)
      * [Change password](#change-password)
      * [Other actions](#other-actions)
  * [License](#license)
  * [TODO](#todo)

# vpn-slice

This is a command-line tool for managing virtual private servers
from [SolVPS](https://www.solvps.com).  It works by scraping the
web-based user interface.

# Usage

```
usage: solvpscli [-h] [vpsid] [{status,browse,boot,reboot,shutdown,ssh}]

This is a tool to manage SolVPS virtual private servers directly from the
command line. It works by scraping the web-based user interface at
https://www.solvps.com/secure/clientarea.php

positional arguments:
  vpsid                 SolVPS numeric ID, or domain name
  {status,browse,boot,reboot,shutdown,ssh}
                        Action to perform on the VPS (ssh to console is only
                        available for Linux systems)

optional arguments:
  -h, --help            show this help message and exit
```

In order to avoid being prompted for your username and password on every invocation,
add your SolVPS username and password to the file `~/.solvps_credentials`:

```
user.name@company.com
SecretPassword321
```

## List active VPS

If no specific system is given on the command line, `solvpscli` will
list the numeric IDs and domain names of all the active VPS accessible by
your account:

```sh
$ solvpscli
Logging in to SolVPS...
No VPS ID or domain name specified. List:
[12345]	linuxbox1.company.com
	Linux VPS - Custom VPS
[12346]	windoze2.company.com
	Windows VPS - Custom Windows VPS
```

## `status`

The `status` action is the default if no other action is specified. It
displays status and configuration information on a VPS:

```sh
$ solvpscli linuxbox1
Logging in to SolVPS...
Found domain linuxbox1.company.com (Linux VPS - Custom Linux VPS) with VPS ID 12345
VM status:
	Status               : online
	Type                 : xen
	Hostname             : linuxbox1.company.com
	Main IP Address      : 101.102.103.104
	IP Addresses         :
	Root Password        :
	Bandwidth            : 13.43 GB of 100 TB Used / 99.99 TB Free 0%
	HDD                  : 27.74 GB of 50 GB Used / 22.26 GB Free 55%
Remote access credentials:
	Access Protocol:     : SSH (Secure Shell) How to Connect ›
	Server Address:      : 101.102.103.104
	Username:            : root
	Password:            : deadbeef0x
	SSH Port:            : 22
Options:
	Processor - CPU      : 1 Core $1.00 USD
	Memory - RAM         : 4 GB $1.00 USD
	SSD Storage          : 25 GB $1.00 USD
	Bandwidth - Data     : Unlimited Data Transfer
	Bandwidth - Speed    : 1Gbps Port Capacity
	Operating System     : Ubuntu 17.04
	Server Location      : Europe - London
```

## `ssh` console

For Linux VPS systems, it's possible to access the
[kernel console](https://en.wikipedia.org/wiki/Linux_console) which may be useful for
troubleshooting an otherwise non-responsive system. Invoking `solvpscli [vpsid] ssh`
provisions an SSH console and displays a shortcut to connect with no password prompt,
using [sshpass](https://sourceforge.net/projects/sshpass/) and OpenSSH:

```sh
$ solvpscli linuxbox1 ssh
Logging in to SolVPS...
Found domain linuxbox1 (Linux VPS - Custom Linux VPS) with VPS ID 12345
Linux system console can now be accessed via ssh:

        sshpass -p 'F0o0BarBz1' ssh -o StrictHostKeyChecking=no console-foO0BR@12.34.56.78

```

(The credentials for the SSH console will expire after about one hour.)

## Change password

For Linux VPS systems, it's possible to change the `root` password via the management interface.

```sh
$ solvpscli linuxbox1 passwd
Logging in to SolVPS...
Found domain linuxbox1 (Linux VPS - Custom Linux VPS) with VPS ID 12345
Enter new password: ****
Retype new password: ****
Success.
```

(The credentials for the SSH console will expire after about one hour.)


## Other actions

The `boot`, `reboot`, and `shutdown` actions should be self-explanatory. They display a short
JSON response from the web service:

```sh
$ solvpscli linuxbox1 boot
Logging in to SolVPS...
Found domain linuxbox1.company.com with VPS ID 12345
Success.
```

The `browse` action opens the web view for the server in question, in your default web browser:

```sh
$ solvpscli windoze2 browse
Logging in to SolVPS...
Found domain windoze2.company.com with VPS ID 12346
Opening in browser: https://www.solvps.com/secure/clientarea.php?action=productdetails&id=12345 ...
```

# License

GPLv3 or later.

## TODO

* Scrape console interface for Windows systems as well
