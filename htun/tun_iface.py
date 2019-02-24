import logging
import select
import socket
import pytun
import errno
import time
#  import base64

from htun.tools import dump, add_route, is_running, print_stats
from htun.args import args


class TunnelServer(object):
    def __init__(self, sock, addr, dstaddr, create_socket=None):
        logging.debug("Initiate Tunnel object")
        self._tun = pytun.TunTapDevice(
            name="htun",
            flags=pytun.IFF_TUN | pytun.IFF_NO_PI
        )
        self._tun.addr = addr
        self._tun.dstaddr = dstaddr
        self._tun.netmask = args.tmask
        self._tun.mtu = args.tmtu
        self._tun.up()
        self.threshold = 5*self._tun.mtu
        self.loop_times = []
        self.last_flush_time = time.time()
        self.timeout = 1
        if args.rsubnet and args.uri:
            add_route(args.rsubnet, args.saddr, self._tun.name)
        self._sock = sock
        self._create_socket = create_socket
        self.r = [self._tun, self._sock]
        self.w = []
        self.to_tun = self.to_sock = b''

    def reconnect(self):
        logging.debug("Reconnecting...")
        if self._create_socket:
            self._sock.close()
            self._sock = self._create_socket()
            self.r = [self._tun, self._sock]
            self.w = []
            self.to_tun = self.to_sock = b''

    def time_to_flush(self):
        if ((len(self.to_sock) > self.threshold) or
                ((time.time()-self.last_flush_time) > self.timeout)):
            print(len(self.to_sock), time.time()-self.last_flush_time)
            self.loop_times.append(time.time() - self.last_flush_time)
            self.last_flush_time = time.time()
            return True
        return False

    def read_data_from_tun(self):
        if self._tun in self.r:
            data = self._tun.read(self._tun.mtu)
            self.to_sock += data
            dump("from_tun <<<", data)

    def read_data_from_socket(self):
        if self._sock in self.r:
            data = self._sock.recv(65535)
            if data:
                self.to_tun += data
                dump("from_sock <<<", data)
            else:
                logging.info("Connection closed")
                return False
        return True

    def write_data_to_tun(self):
        if self._tun in self.w and self.to_tun:
            try:
                write_len = self._tun.write(self.to_tun)
                self.count_in += write_len
                dump("to_tun <<<", self.to_tun)
                self.to_tun = b""
            except OSError as e:
                if e.errno == errno.EINVAL:
                    # this is a transmission error. just drop it
                    dump("Illegal argument", self.to_tun)
                    self.to_tun = b''
                    self.count_err += 1
                else:
                    raise e

    def write_data_to_socket(self):
        if ((self._sock in self.w and self.to_sock) and
                self.time_to_flush()):
            sent_len = self._sock.send(self.to_sock)
            self.count_out += sent_len
            dump("to_sock >>>", self.to_sock)
            self.to_sock = b""

    def select_fds(self):
        try:
            self.r, self.w, _ = select.select(self.r, self.w, [])
        except ValueError:
            logging.info("Connection reset by peer")
            return False
        return True

    def prepare_fds(self):
        self.r = [self._tun, self._sock]
        self.w = []
        # only put in the object we really want to write to, or
        # else we cause high CPU load
        if self.to_tun:
            self.w.append(self._tun)
        if self.to_sock:
            self.w.append(self._sock)

    def forward_data(self):
        if not self.select_fds():
            return False

        if not self.read_data_from_socket():
            return False
        self.read_data_from_tun()
        self.write_data_to_tun()
        self.write_data_to_socket()

        self.prepare_fds()
        return True

    def run(self):
        self.count_in = self.count_out = self.count_err = 0
        last_print_time = time.time()
        while is_running():
            try:
                now = time.time()
                if not self.forward_data():
                    self.reconnect()
                else:
                    # only print every 1s for efficiency
                    if now - last_print_time > 1:
                        print_stats(self.count_in,
                                    self.count_out,
                                    self.count_err)
                        last_print_time = now
            except (select.error, socket.error, pytun.Error) as e:
                logging.warning(str(e))
                time.sleep(1)
        self._sock.close()
