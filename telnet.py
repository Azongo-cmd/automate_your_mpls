from telnetlib import Telnet


def reloadRouter(ip, hostname):
    with Telnet(ip, 23) as tn:
        tn.read_until(b"")