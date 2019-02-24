import logging
import socket
from htun.args import args


def create_socket():
    logging.info("Waiting for connection... ")
    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _sock.bind((args.bindip, args.lport))
    _sock.listen(1)
    server_socket, a = _sock.accept()
    logging.info("Incoming connection: %s:%d" % a)
    return server_socket


server_socket = create_socket()
