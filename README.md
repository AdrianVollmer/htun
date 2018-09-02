htun
====

htun is a layer 2 tunnel over HTTP or TCP. It was developed with situations
in mind where traffic to the internet is restricted. For instance, some
networks don't allow traffic to the internet at all and require you to go
through an HTTP proxy. htun enables you to get full internet access in those
situations (all ports, all protocols). It also supports using a SOCKS proxy.

Obviously, performance takes a huge it. So it is meant for some light
browsing or downloading small files sporadically. Expect transfer rates to
be cut by a factor of 100.

Also, it is not encrypted by default. It is recommended to put another
tunnel on top, such as Wireguard.

Since python-pytun is required, which is a non-portable module, this will
only run on Linux.


Usage
-----

The script needs to be run with root privileges both on the server and the
client. On the server, run:

    ./htun.py --server

On the client, run:

    ./htun.py --uri <SERVER URI>

By default, it uses HTTP on port 80 and the IP addresses 10.13.37.1 and
10.13.37.2 for the client and the server, respectively.

For all options, run `./htun.py --help`:

    usage: htun.py [-h] [--debug] [--client-addr CADDR] [--server-addr SADDR]
                   [--tun-netmask TMASK] [--tun-mtu TMTU] [--tun-timeout TIMEOUT]
                   [--route-subnet RSUBNET] [--proxy PROXY] [--username USERNAME]
                   [--password PASSWORD] [--listen-port LPORT] [--bind-ip BINDIP]
                   (--server [SERVER] | --uri URI)

    htun is a TCP and HTTP tunnel on layer 2 (author: Adrian Vollmer)

    optional arguments:
      -h, --help            show this help message and exit
      --debug, -d           debug flag to true (default: False)
      --client-addr CADDR, -c CADDR
                            tunnel local address (default: 10.13.37.1)
      --server-addr SADDR, -s SADDR
                            tunnel destination address (default: 10.13.37.2)
      --tun-netmask TMASK, -m TMASK
                            tunnel netmask (default: 255.255.255.0)
      --tun-mtu TMTU        tunnel MTU (default: 1500)
      --tun-timeout TIMEOUT
                            r/w timeout in seconds (default: 1)
      --route-subnet RSUBNET, -n RSUBNET
                            subnet to be routed via tunnel (default: None)
      --proxy PROXY, -P PROXY
                            proxy URI (<proto>://<host>:<port>) (default: None)
      --username USERNAME, -u USERNAME
                            username for proxy authentication (default: None)
      --password PASSWORD, -W PASSWORD
                            password for proxy authentication (default: None)
      --listen-port LPORT, -p LPORT
                            listen port of the server component (default: 80)
      --bind-ip BINDIP, -b BINDIP
                            bind IP address of the server component (default:
                            0.0.0.0)
      --server [SERVER]     local port and bind address (http, tcp)
                            (default: http)
      --uri URI             remote URI (<proto>://<host>[:<port>]) (default: None)


Examples
--------

### TCP Tunnel

To use a TCP tunnel on port 443, run

    ./htun.py --server tcp -p 443

on the server side and

    ./htun.py --uri tcp://<host>:443

on the client side. Now the client can reach the server via the IP address
10.13.37.2

### SOCKS Proxy

To use HTTP over a SOCKS5 proxy on port 5000, run

    ./htun.py --server

on the server side and

    ./htun.py --uri http://<host> --proxy socks5://<proxy-host>:5000

on the client side.

### Proxy Authentication

Proxies using basic authentication are supported (but yet untested).

A proxy requiring NTLM authentication is not supported because
`python-urllib3` does not support NTLM. It is suggested to use `cntlm` as an
additional SOCKS proxy.


Performance
-----------

Performance over a TCP tunnel is much better than over an HTTP tunnel.
Expect several orders of magnitude in degradation of the connection when
using HTTP.

Example downloading 713k bytes without the tunnel:

	$ curl https://example.com/example.png  > /dev/null
	  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
									 Dload  Upload   Total   Spent    Left  Speed
	100  713k  100  713k    0     0  2680k      0 --:--:-- --:--:-- --:--:-- 2680k

Downloading the same file with an HTTP tunnel:

	$ curl https://example.com/example.png  > /dev/null
	  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
									 Dload  Upload   Total   Spent    Left  Speed
    100  713k  100  713k    0     0  12177      0  0:00:59  0:00:59 --:--:-- 16590

With a TCP tunnel it's at least around 3% of the original speed:

    $ curl https://i.imgur.com/8jDGnXB.png  > /dev/null
      % Total    % Received % Xferd  Average Speed   Time    Time     Time Current
                                   Dload  Upload   Total   Spent    Left
                                   Speed
    100  713k  100  713k    0     0  37640      0  0:00:19  0:00:19 --:--:-- 41086



To do
-----

* Make performance improvements when using HTTP
* Experiment with threaded requests


Disclaimer
----------

Keep in mind that the administrator of the network most likely did not want
you to bypass the restriction that were set up. The restriction is probably
there for a reason, you need to respect that. Using this tool may violate
terms and conditions or company rules and possibly even get you in legal
trouble and/or fired from your job.

Use this only if you know that you have permission to use it by everyone
involved.


Author
------

Adrian Vollmer, 2018
