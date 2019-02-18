from htun.args import args
import logging
import subprocess
import random
import datetime
if args.debug:
    try:
        import hexdump
    except ImportError:
        logging.error("Debug mode impossible without the python module 'hexdump'. "
              "Install it first.")
        args.debug = False


RUNNING = True


def stop_running():
    global RUNNING
    RUNNING = False


def is_running():
    return RUNNING


def dump(comment, data):
    if args.debug:
        logging.debug(comment+hexdump.hexdump(data))


def add_route(subnet, via_ip, devname):
    subprocess.check_call([
        'ip',
        'route',
        'add',
        subnet,
        'via',
        via_ip,
    ])


def temp_filename(basename):
    suffix = int(datetime.datetime.now().timestamp()*1000)
    return "%s_%s_%d" % (basename, suffix, random.random()*1000)


def print_stats(count_in, count_out, count_err):
    if not args.debug:
        msg = "Bytes received: %d   Bytes sent: %d   Packets dropped: %d"\
                % (count_in, count_out, count_err)
        print('\r' + msg, end='')


def create_iptables_rules():
    global old_ipforward
    if args.ifaceout:
        with open('/proc/sys/net/ipv4/ip_forward', 'r') as f:
            old_ipforward = f.read()
        with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
            f.write('1')
        subprocess.check_call(
            'iptables -t nat -A POSTROUTING -o'.split() +
            [args.ifaceout] +
            '-j MASQUERADE'.split()
        )


def delete_ip_tables_rules():
    if args.ifaceout:
        with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
            f.write(old_ipforward)
        subprocess.check_call(
            'iptables -t nat -D POSTROUTING -o'.split() +
            [args.ifaceout] +
            '-j MASQUERADE'.split()
        )
