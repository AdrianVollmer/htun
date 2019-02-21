import socket
import socks
from htun.args import args


def create_socket():
    if args.proxy:
        server_socket = socks.socksocket()
        proto, rest = args.proxy.split('://')
        host, port = rest.split(':')
        port = int(port)
        if proto == "socks4":
            server_socket.set_proxy(socks.SOCKS4, host, port)
        elif proto == "socks5":
            server_socket.set_proxy(socks.SOCKS5, host, port)
        else:
            print("Invalid protocol: %s (must be one of socks4 or socks5)" %
                  proto)
    else:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #  server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server_socket.connect((args.uri["peer_ip"], args.uri["port"]))

    return server_socket


server_socket = create_socket()
