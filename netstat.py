#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
A netstat -nlp[t|u] python script
'''

import os
import sys
import re
import glob
import argparse


def _ip(hex):
    ''' Return IP from hex '''

    ip_hex = [hex[i:i+2] for i in range(0, len(hex), 2)][::-1]
    ip_dec = []
    for iph in ip_hex:
        ip_dec.append(str(int(iph, 16)))
    return '.'.join(ip_dec)


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
    return STAT[int(state, 16)]


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
                    int(l['lport'], 16), _ip(l['raddr']),
                    int(l['rport'], 16), _state(l['state']),
                    p[0], p[1])
            else:
                print "{}\t{}\t{}:{}\t{}:{}\t{}\t{}\t{}".format(
                    _owner(l['uid']), pro, _ip(l['laddr']),
                    int(l['lport'], 16), _ip(l['raddr']),
                    int(l['rport'], 16), '',
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
