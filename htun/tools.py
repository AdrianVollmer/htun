from htun.args import args
import subprocess
import random
import datetime
if args.debug:
    try:
        import hexdump
    except ImportError:
        print("Debug mode impossible without the python module 'hexdump'. "
              "Install it first.")
        args.debug = False


RUNNING = True
ROUTE = None


def stop_running():
    global RUNNING
    RUNNING = False


def is_running():
    return RUNNING


def dump(comment, data):
    if args.debug:
        print(comment)
        hexdump.hexdump(data)


def add_route(subnet, via_ip, devname, peer_ip):
    route = subprocess.check_output([
        'ip',
        'route',
        'get',
        peer_ip,
    ])
    route = route.splitlines()[0].decode()
    route = route.strip().split(' ')
    global ROUTE
    ROUTE = route

    subprocess.check_call([
        'ip',
        'route',
        'add',
    ] + ROUTE)

    subprocess.check_call([
        'ip',
        'route',
        'add',
        subnet,
        'via',
        via_ip,
    ])


def clean_up():
    if ROUTE:
        subprocess.check_call([
            'ip',
            'route',
            'del',
        ] + ROUTE)



def temp_filename(basename):
    suffix = int(datetime.datetime.now().timestamp()*1000)
    return "%s_%s_%d" % (basename, suffix, random.random()*1000)


def print_stats(count_in, count_out, count_err):
    if not args.debug:
        msg = "Bytes received: %d   Bytes sent: %d   Packets dropped: %d"\
                % (count_in, count_out, count_err)
        print('\r' + msg, end='')
