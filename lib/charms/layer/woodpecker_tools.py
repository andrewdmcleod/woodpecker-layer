#!/usr/bin/env python

import shlex
import subprocess
from charmhelpers.core import hookenv


def safe_status(workload, status):
    cfg = hookenv.config()
    if not cfg.get('supress_status'):
        hookenv.status_set(workload, status)


def woodpecker_listen():
    cfg = hookenv.config()
    ports = cfg.get('check_ports').split(',')
    for port in ports:
        hookenv.log('Opening local port: {}'.format(port))
        open_local_port(port)


def open_local_port(port):
    try:
        exec_string = "/bin/nc -k -l {}".format(port)
        exec_string = shlex.split(exec_string)
        subprocess.Popen(exec_string, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as msg:
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
        hookenv.log('Port check, label: {}, host: {}, port: {}, send: {}, receive: {}'.format(label, host, port, send, receive))
        result = _nc_method(send_string) + receive
    else:
        send_string = 'nc {} {}'.format(host, port)
        hookenv.log('Port check, label: {}, host: {}, port: {}'.format(label, host, port))
        result = _nc_method(send_string)
    hookenv.log('nc command: {}, result: {}'.format(send_string, result), 'DEBUG')
    return result


def check_peers(peers):
    cfg = hookenv.config()
    ports = cfg.get('check_ports').split(',')
    try:
        peer_fail
    except NameError:
        peer_fail = []
    for peer in peers:
        for port in ports:
            hookenv.log('Checking Peer: {}, {}, Port: {}'.format(peer[0], peer[1], port), 'INFO')
            peer_check = check_port('peer', peer[1], port)
        if peer_check[1] == 1:
            if peer[0].split('/')[1] not in peer_fail:
                peer_fail.append(peer[0].split('/')[1])
        else:
            if peer[0].split('/')[1] in peer_fail:
                peer_fail.remove(peer[0].split('/')[1])
    return peer_fail


def check_remote_hosts():
    try:
        hosts_failed
    except NameError:
        hosts_failed = []
    cfg = hookenv.config()
    remote_checks = cfg.get('check_list').split(',')
    hookenv.log('REMOTE CHECKS: {}'.format(remote_checks))
    if remote_checks != '':
        for check in remote_checks:
            check_list = check.split(':')
            result = check_port(check_list[0], check_list[1], check_list[2])
            hookenv.log('RESULT: {}'.format(result))
            if len(check_list) == 3:
                # Send is not defined
                if result[1] == 0:
                    if check_list[0] in hosts_failed:
                        hosts_failed.remove(check_list[0])
                else:
                    if check_list[0] not in hosts_failed:
                        hosts_failed.append(check_list[0])
            elif len(check_list) > 3:
                # this definitely wont work yet...
                if check.split(':')[3] in result:
                    if check.split(':')[0] in hosts_failed:
                        hosts_failed.remove(check.split(':')[0])
                else:
                    if check.split(':')[0] not in hosts_failed:
                        hosts_failed.append(check.split(':')[0])
    return hosts_failed
