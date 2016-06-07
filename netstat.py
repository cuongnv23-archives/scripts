#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
A netstat -nlp[t|u] python script
'''

import os
import sys
import math
import re
import glob
import argparse


HEX = {'F': 15, 'E': 14, 'D': 13, 'C': 12, 'B': 11, 'A': 10,
       '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4,
       '3': 3, '2': 2, '1': 1, '0': 0}


def _hex2dec(hex):
    ''' Return decimal of hex '''
    dec = 0
    for h in range(0, len(hex)):
        tmp = int(HEX[hex[h]] * math.pow(16, len(hex) - h - 1))
        dec += tmp
    return dec


def _ip(hex):
    ''' Return IP from hex '''

    ip_hex = [hex[i:i+2] for i in range(0, len(hex), 2)][::-1]
    ip_dec = []
    for iph in ip_hex:
        tmp = int(HEX[iph[0]] * math.pow(16, 1) +
                  HEX[iph[1]] * math.pow(16, 0))
        ip_dec.append(str(tmp))
    return '.'.join(ip_dec)


def _port(hex):
    ''' Return port from hex '''
    return _hex2dec(hex)


def _owner(uid):
    ''' Return username of uid '''
    with open('/etc/passwd') as f:
        for line in f.readlines():
            if line.split(':')[2] == str(uid):
                return line.split(':')[0]


def _state(state):
    ''' Return status of socket based on state code '''
    STAT = {1: 'ESTABLISHED',
            2: 'SYN_SENT',
            3: 'SYN_RECV',
            4: 'FIN_WAIT1',
            5: 'FIN_WAIT2',
            6: 'TIME_WAIT',
            7: 'CLOSE',
            8: 'CLOSE_WAIT',
            9: 'LAST_ACK',
            10: 'LISTEN',
            11: 'CLOSING',
            12: 'NEW_SYN_RECV'
            }
    return STAT[_hex2dec(state)]


def _cmdline(inode):
    ''' Return list of pid and cmdline '''
    real_paths = [os.path.realpath(i) for i in glob.glob('/proc/*/fd/*')]
    for rp in real_paths:
        if re.search(inode, rp):
            pid = rp.split('/')[2]
            try:
                with open('/proc/' + str(pid) + '/cmdline') as f:
                    return [pid, f.read()]
            except IOError:
                continue


def parse_line(line):
    ''' parse line structure and store to dict '''
    l = line.split()
    laddr = l[1].split(':')[0]
    lport = l[1].split(':')[1]
    raddr = l[2].split(':')[0]
    rport = l[2].split(':')[1]
    state = l[3]
    uid = l[7]
    inode = l[9]
    return {'laddr': laddr,
            'lport': lport,
            'raddr': raddr,
            'rport': rport,
            'state': state,
            'uid': uid,
            'inode': inode}


def netstat(pro):
    ''' Read pro(tcp/udp) socket file '''
    print "User\tProto\tLocal Address\tRemote Address\tState\tPID\tCommand"
    with open('/proc/net/' + pro) as f:
        for line in f.read().splitlines()[1:]:
            l = parse_line(line)
            p = _cmdline(l['inode'])
            # tricky
            if not p:
                p = [None, None]

            if pro == 'tcp':
                print "{}\t{}\t{}:{}\t{}:{}\t{}\t{}\t{}".format(
                    _owner(l['uid']), pro, _ip(l['laddr']),
                    _port(l['lport']), _ip(l['raddr']),
                    _port(l['rport']), _state(l['state']),
                    p[0], p[1])
            else:
                print "{}\t{}\t{}:{}\t{}:{}\t{}\t{}\t{}".format(
                    _owner(l['uid']), pro, _ip(l['laddr']),
                    _port(l['lport']), _ip(l['raddr']),
                    _port(l['rport']), '',
                    p[0], p[1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--udp", help="Netstat for UDP",
                        action="store_true")
    parser.add_argument("-t", "--tcp", help="Netstat for TCP",
                        action="store_true")
    if len(sys.argv) != 2:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    if args.tcp:
        netstat('tcp')
    elif args.udp:
        netstat('udp')
    else:
        parser.print_help()
        sys.exit(1)
