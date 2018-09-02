import select
import time

from htun.tools import dump, is_running
from htun.args import args


class TunnelServer(object):
    def __init__(self, sock, addr, dstaddr):
        self._rsock = sock
        self._lsock = None

    def run(self):
        r = w = [self._lsock, self._rsock]
        to_lsock = to_rsock = b''
        while is_running():
            time.sleep(.01)  # to avoid high CPU load
            try:
                r, w, _ = select.select(r, w, [])

                if self._lsock in r:
                    to_rsock = self._lsock.recv(65535)
                if self._rsock in r:
                    to_lsock = self._rsock.recv(65535)

                if self._lsock in w and to_lsock:
                    dump("to_lsock <<<", to_lsock)
                    self._lsock.send(to_lsock)
                    to_lsock = b''
                if self._rsock in w and to_rsock:
                    dump("to_rsock >>>", to_rsock)
                    self._rsock.send(to_rsock)
                    to_rsock = b''

                r = w = []
                if to_lsock:
                    w.append(self._lsock)
                else:
                    r.append(self._rsock)
                if to_rsock:
                    w.append(self._rsock)
                else:
                    r.append(self._lsock)
            except Exception as e:
                if args.debug:
                    print(str(e))
                #  stop_running()
