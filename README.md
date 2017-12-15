Table of Contents
=================

  * [solvpscli](#vpn-slice)
    * [Usage](#usage)
  * [License](#license)
  * [TODO](#todo)

# vpn-slice

This is a command-line tool for managing virtual private servers
from [SolVPS](https://www.solvps.com).  It works by scraping the
web-based user interface.

# Usage

```
usage: solvpscli [-h] [-u USERNAME] [-p PASSWORD]
                 [id] [{status,browse,boot,reboot,shutdown,ssh}]

This is a tool to manage SolVPS virtual private servers directly from the
command line. It works by scraping the web-based user interface at
https://www.solvps.com/secure/clientarea.php

positional arguments:
  id                    SolVPS numeric ID, or domain name
  {status,browse,boot,reboot,shutdown,ssh}
                        Action to perform on the VPS (ssh to console is only
                        available for Linux systems)

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
  -p PASSWORD, --password PASSWORD
```

# License

GPLv3 or later.

## TODO

* Scrape console interface for Windows systems as well
