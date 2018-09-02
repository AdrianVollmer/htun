import socket
from htun.args import args


def create_socket():
    print("Waiting for connection... ", end='')
    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    _sock.bind((args.bindip, args.lport))
    _sock.listen(1)
    server_socket, a = _sock.accept()
    print("Incoming connection: %s:%d" % a)
    return server_socket


server_socket = create_socket()
