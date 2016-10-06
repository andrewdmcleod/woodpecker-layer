# Overview

Woodpecker is a charm used for testing the networking between peers, or 
to arbitrary host:port combinations, e.g. www.google.com:80.

All actions, strings, queries and actions are logged in the juju logs.


# Configuration

By default, port 31337 will be opened on each peer, and connectivity
validated between each peer on that port with an OK string response.
This can be modified to another port by providing a comma separated list
to the check_ports configuration key._ 

Additionally, tcp port and ip combinations can be provided to the check_list
string. A send string and receive string can be defined to provide further
testing, e.g.:

        juju set config woodpecker \
        check_list='google:www.google.com:80:get /:302,ubuntu_ftp:ftp.ubuntu.com:21:test:503'

This will cause woodpecker to connect to www.google.com, send "get /", and
only return true if "302" is in the response. 

check_list access the following check formats:

* **`label:host:port`** Will just check that the port is open
* **`label:host:port:send:receive`** Will send 'send' and set OK only if 'receive' is found
in the response string.

All labels must be unique, and all checks must be specified each time the config value is set,
i.e. labels do not persist if you do not include them in the config value.


# Workload Status

In addition to ICMP and DNS status messages, if a networking problem is
detected, the workload status of the agent which has found the issues
will be set to blocked. 


# Reactive States

This layer will set the following states:

* **`something something`** Something.


# Usage

```
juju deploy woodpecker -n 2
juju deploy woodpecker -n 1 --to lxc:1
juju set woodpecker check_ports='80, 22, 21'
juju set woodpecker check_list='www.google.com:80, 8.8.8.8:80, www.canonical.com:443'
```
