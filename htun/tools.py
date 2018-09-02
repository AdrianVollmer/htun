from htun.args import args
import subprocess
import random
import datetime
try:
    import hexdump
except ModuleNotFoundError:
    print("Debug mode impossible without the python module 'hexdump'. "
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
        print(comment)
        hexdump.hexdump(data)


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
