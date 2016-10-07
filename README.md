# Overview

Woodpecker is a charm for testing networking between peers, and/or 
to arbitrary host:port combinations, e.g. www.google.com:80, with or
without a 'send' string and a 'receive' string.

Status messages will either display an error with a check, or all ok.
For detailed information see the juju logs.

Example usage for woodpecker could be to deploy one unit to bare metal,
one to an lxc container - this would validate connection between the two.

Another example would be to use woodpecker to check all API endpoints 
in a particular bundle deployment, e.g. openstack, bigdata, etc.

# Configuration

By default, port 31337 will be opened on each peer, and connectivity
validated between each peer on that port.
This can be modified to another port by providing a comma separated list
to the check_ports configuration key. 

Additionally, tcp port and ip combinations can be provided to the check_list
string. A send string and receive string can also be defined to provide further
testing, e.g.:

        juju set config woodpecker \
        check_list='
        google:www.google.com:80:get /:302,
        ubuntu_ftp:ftp.ubuntu.com:21:test:503,
        canonical:www.canonical.com:80'

This will cause woodpecker to connect to www.google.com, send "get /", and
only return true if "302" is in the response string. 

check_list access the following check formats:

* **`label:host:port`** Will just check that the tcp port is open
* **`label:host:port:send:receive`** Will send 'send' and check 'receive' 
is found in the response string.

All labels must be unique, and all checks must be specified each time 
the config value is set.


# Workload Status

In addition to basic status messages, if a peer or remote host connection
failure is detected, the workload status of the agent which has found the 
issue will be set to blocked. 


# Reactive States

This layer will set the following states:

* **`woodpecker-peer.failed`** Connection to the tcp port on its peer has failed
* **`woodpecker-hosts.failed`** One or more remote host checks have failed


# Usage

```
juju deploy woodpecker 
juju add-unit woodpecker -n 1 --to lxc:1
juju set woodpecker check_ports='31337,1337'
juju set woodpecker check_list='google_simple:www.google.com:80,google_advanced:www.google.com:80:GET /:302'
```
