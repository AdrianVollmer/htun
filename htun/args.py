import argparse


parser = argparse.ArgumentParser(
    description="htun is a TCP and HTTP tunnel on layer 2 "
    "(author: Adrian Vollmer)",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument('--debug', '-d', dest='debug', default=False,
                    action='store_true', help='debug flag to true')

parser.add_argument('--client-addr', '-c', dest='caddr', default='10.13.37.1',
                    help='tunnel local address')
parser.add_argument('--server-addr', '-s', dest='saddr', default='10.13.37.2',
                    help='tunnel destination address')
parser.add_argument('--tun-netmask', '-m', default='255.255.255.0',
                    dest='tmask', help='tunnel netmask')
parser.add_argument('--tun-mtu', type=int, default=1500, dest='tmtu',
                    help='tunnel MTU')
parser.add_argument('--tun-timeout', type=int, default=1, dest='timeout',
                    help='r/w timeout in seconds')
parser.add_argument('--route-subnet', '-n', type=str, dest='rsubnet', default='default',
                    help='subnet to be routed via tunnel')
parser.add_argument('--iface-out', '-i', type=str, dest='ifaceout',
                    help='interface to which the server should route traffic')

parser.add_argument('--proxy', '-P', dest='proxy',
                    help='proxy URI (<proto>://<host>:<port>)')
parser.add_argument('--username', '-u', dest='username',
                    help='username for HTTP proxy basic authentication')
parser.add_argument('--password', '-W', dest='password',
                    help='password for HTTP proxy basic authentication')
# TODO
#  parser.add_argument('--creds-file', '-A', dest='creds_file',
#                      help='path to file containing credentials')


parser.add_argument('--listen-port', '-p', dest='lport',
                    type=int, default=80,
                    help='listen port of the server component')
parser.add_argument('--bind-ip', '-b', dest='bindip',
                    type=str, default='0.0.0.0',
                    help='bind IP address of the server component')

serverclient = parser.add_mutually_exclusive_group(required=True)
serverclient.add_argument('--server', default='http',
                          dest='server', type=str, choices=["http", "tcp"],
                          help='server protocol')
serverclient.add_argument('--uri', dest='uri',
                          type=str, action='store',
                          help='remote URI (<proto>://<host>[:<port>])')

args = parser.parse_args()
