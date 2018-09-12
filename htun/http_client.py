import urllib3
import socket
import select
import threading
import os
from htun.args import args
from htun.tools import dump, temp_filename, is_running

from urllib3.contrib.socks import SOCKSProxyManager


SOCK_FILE_SERVER = temp_filename("/tmp/htun_s_")
SOCK_FILE_CLIENT = temp_filename("/tmp/htun_c_")

# data from the htun interface is sent to the server socket
server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
server_socket.bind(SOCK_FILE_SERVER)

# client socket is connected to the server socket. data from the client socket
# is sent to the remote instance via http requests
client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
client_socket.bind(SOCK_FILE_CLIENT)

# connect the sockets
client_socket.connect(SOCK_FILE_SERVER)
server_socket.connect(SOCK_FILE_CLIENT)


def connect():
    if args.proxy:
        proto, _ = args.proxy.split("://")
        if proto == "http":
            default_headers = urllib3.make_headers(
                proxy_basic_auth='%s:%s' % (args.username, args.password),
            )
            http_proxy = urllib3.ProxyManager(
                args.proxy,
                headers=default_headers
            )
            http = http_proxy.connection_from_url(args.uri["uri"])
        elif proto in ["socks4", "socks5"]:
            http = SOCKSProxyManager(args.proxy)
        else:
            print("Invalid proxy protocol. It must start with 'http://' or "
                  "'socks[45]://'.")
            exit(1)
    else:
        http = urllib3.connection_from_url(args.uri["uri"])
    return http


http = connect()


def transmit(data):
    try:
        r = http.urlopen(
            'POST',
            args.uri["uri"],
            body=data,
            assert_same_host=(args.proxy is None),
        )
    except urllib3.exceptions.MaxRetryError as e:
        print("Could not connect to %s" % args.uri["uri"])
        if args.debug:
            print(e)
        exit(1)
    dump("transmit >>>", data)
    return r.data


def receive():
    try:
        r = http.urlopen(
            'GET',
            args.uri["uri"],
            assert_same_host=(args.proxy is None),
        )
    except urllib3.exceptions.MaxRetryError as e:
        print("Could not connect to %s" % args.uri["uri"])
        if args.debug:
            print(e)
        exit(1)
    if r.data:
        dump("receive >>>", r.data)
    return r.data


def handle_data():
    data_in = data_out = b""
    while is_running():
        r, w, _ = select.select([client_socket],
                                [client_socket],
                                [],
                                args.timeout
                                )
        if client_socket in r:
            data_out = client_socket.recv(65535)
            data_in = transmit(data_out)
        if not data_in:
            data_in = receive()
        if client_socket in w and data_in:
            client_socket.send(data_in)
            data_in = b''
    os.remove(SOCK_FILE_SERVER)
    os.remove(SOCK_FILE_CLIENT)


t = threading.Thread(target=handle_data)
t.start()
