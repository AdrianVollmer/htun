import threading
import socket
import select
import os

from http.server import BaseHTTPRequestHandler, HTTPServer
#  import SocketServer

from htun.tools import dump, temp_filename
from htun.args import args

SOCK_FILE_SERVER = temp_filename("/tmp/htun_s_")
SOCK_FILE_CLIENT = temp_filename("/tmp/htun_c_")

# data from the htun interface is sent to the server socket
server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
server_socket.bind(SOCK_FILE_SERVER)
os.chmod(SOCK_FILE_SERVER, 0o700)

# client socket is connected to the server socket. data from the client socket
# is sent to the remote instance via reverse http requests
client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
client_socket.bind(SOCK_FILE_CLIENT)
os.chmod(SOCK_FILE_CLIENT, 0o700)

# connect the sockets
client_socket.connect(SOCK_FILE_SERVER)
server_socket.connect(SOCK_FILE_CLIENT)


def data_response():
    r, _, _ = select.select([client_socket], [], [], 0.)
    if r:
        data = r[0].recv(65535)
        dump("http_out >>>", data)
    else:
        data = b""
    return data


class S(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def _set_headers(self, content_length):
        self.send_response(200)
        self.send_header('Content-Length', content_length)
        self.end_headers()

    def do_GET(self):
        data_out = data_response()

        self._set_headers(len(data_out))
        self.wfile.write(data_out)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)

        dump("http_in <<<", data)
        _, w, _ = select.select([], [client_socket], [], 0.)
        if w and data:
            w[0].send(data)
        data_out = data_response()

        self._set_headers(len(data_out))
        self.wfile.write(data_out)

    def log_message(self, format, *kwargs):
        if args.debug:
            return super(S, self).log_message(format, *kwargs)
        else:
            return


def run():
    server_address = (args.bindip, args.lport)
    handler = S
    handler.server_version = "Server: "
    handler.sys_version = ""
    httpd = HTTPServer(server_address, S)
    httpd.serve_forever()


def run_server():
    t = threading.Thread(target=run)
    t.setDaemon(True)
    t.start()
