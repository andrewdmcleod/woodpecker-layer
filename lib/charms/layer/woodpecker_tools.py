#!/usr/bin/env python

import os
import subprocess
import re
from charmhelpers.core import hookenv


def safe_status(workload, status):
    cfg = hookenv.config()
    if not cfg.get('supress_status'):
        hookenv.status_set(workload, status)


def open_local_port(port):
    try:
        os.spawnl(os.P_NOWAIT, '/bin/nc -k -l {}'.format(port))
    except os.error as msg:
        hookenv.log('something went wrong with netcat listening: {}'.format(msg))


def _nc_method(send_string):
    try:
        result = subprocess.check_output(send_string, shell=True)
        stderr = 0
    except subprocess.CalledProcessError as msg:
        result = 'FAILED: {}, output: {}'.format(send_string, msg)
        stderr = 1
    return result, stderr


def check_port(label, host, port, send='', receive=''):
    if receive != '':
        send_string = 'echo {} | nc {} {}'.format(send, host, port)
        result = _nc_method(send_string) + receive
    else:
        send_string = 'nc {} {}'.format(host, port)
        result = _nc_method(send_string) 
    hookenv.log('nc command: {}, result: {}'.format(send_string, result), 'DEBUG')
    return result


def check_peers(peers):
    cfg = hookenv.config()
    ports = cfg.get('check_ports')
    try:
        peer_fail
    except NameError:
        peer_fail = []
    for peer in peers:
        for port in ports
            hookenv.log('Checking Peer: {}, Port: {}'.format(peer[0], port), 'INFO')
            peer_check = check_port('peer', peer[1], port)
    if peer_check[1] == 1:
        peer_fail = peer[1] + peer_fail
    if peer_fail != []:
        safe_status('peers failed: ' + str(peer_fail))
    else:
        safe_status('peers ok')


def check_remote_hosts():
    cfg = hookenv.config()
    remote_checks = cfg.get('check_list')
    if remote_checks != '':
        for check in remote_checks:
            result = check_port(check.split(':')).strip('[]')
            if len(check.split(':')) == 3:
                # Send is not defined
                if check.split(':')[3] in result:
                    return 'OK'
                else:
                    return 'FAILED'
            if check.split(':')[4] in result:
                return 'OK'
            else:
                return 'FAILED'
