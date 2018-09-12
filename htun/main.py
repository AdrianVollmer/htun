from htun.args import args
from htun.tools import stop_running, clean_up
from htun.http_server import run_server
from htun.tun_iface import TunnelServer

if args.uri:
    is_server = False
    proto = args.uri["proto"]
    if proto == "http":
        from htun.http_client import server_socket
        reconnect = None
    elif proto == "tcp":
        from htun.tcp_client import server_socket, create_socket
        reconnect = create_socket
    else:
        print("Unknown URI protocol: %s (must be one of tcp or http)" %
              args.server)
        exit(1)
else:
    is_server = True
    if args.server == "http":
        from htun.http_server import server_socket
        run_server()
        reconnect = None
    elif args.server == "tcp":
        from htun.tcp_server import server_socket, create_socket
        reconnect = create_socket
    else:
        print("Unknown URI protocol: %s (must be one of tcp or http)" %
              args.server)
        exit(1)


def main():
    if is_server:
        server = TunnelServer(server_socket, args.saddr, args.caddr, reconnect)
    else:
        server = TunnelServer(server_socket, args.caddr, args.saddr,
                              reconnect)
    # drop privs?
    try:
        server.run()
    except KeyboardInterrupt:
        print("CTRL-c caught, exiting...")
        stop_running()
    clean_up()
