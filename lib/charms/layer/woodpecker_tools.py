#!/usr/bin/env python

import shlex
import subprocess
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv


def _set_states(peers=None, hosts=None):
    hookenv.log('_set_states PEERS: {}'.format(peers))
    hookenv.log('_set_states HOSTS: {}'.format(hosts))
    current_status = hookenv.status_get()
    peer_status = current_status[1].split(',')[0]
    hostcheck_status = current_status[1].split(',')[1]
    if peers is None:
        peer_status = 'waiting for peers'
    elif peers != []:
        set_state('woodpecker-peer.failed')
        peer_status = 'peer check failed: ' + str(peers)
    else:
        remove_state('woodpecker-peer.failed')
        peer_status = 'all peer checks ok'
    if hosts is None:
        hostcheck_status = ', no host checks defined'
    elif hosts != []:
        set_state('woodpecker-hosts.failed')
        hostcheck_status = ', host check failed: ' + str(hosts)
    else:
        remove_state('woodpecker-hosts.failed')
        hostcheck_status = ', all host checks ok'
    if 'failed' in peer_status or 'failed' in hostcheck_status:
        workload = 'blocked'
    else:
        workload = 'active'
    safe_status(workload, peer_status + hostcheck_status)


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



def check_port(label, host, port, *args):
    hookenv.log('parameters: {}'.format(label, host, port, args)
    send = args[0]
    receive = args[1]
    if receive != '':
        send_string = 'echo {} | nc {} {}'.format(send, host, port)
        hookenv.log('Port check, label: {}, host: {}, port: {}, send: {}, receive: {}'.format(label, host, port, send, receive))
        result = str(_nc_method(send_string)) #+ str(receive)
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
            if len(check_list) < 5:
                # Send is not defined
                if len(check_list) != 3:
                    hookenv.log('Your check, {}, is not formatted correctly: \
                                label:host:port:send_string:receive_string'.format(check))
                    continue
                result = check_port(*check_list)
                hookenv.log('RESULT: {}'.format(result))
                if result[1] == 0:
                    if check_list[0] in hosts_failed:
                        hosts_failed.remove(check_list[0])
                else:
                    if check_list[0] not in hosts_failed:
                        hosts_failed.append(check_list[0])
            elif len(check_list) == 5:
                hookenv.log('if check.split ({}) in test for test in result: '.format(check.split(':')[4]))
                result = check_port(*check_list)
                hookenv.log('RESULT: {}'.format(result))
                if check.split(':')[4] in str(result):
                    if check.split(':')[0] in hosts_failed:
                        hosts_failed.remove(check.split(':')[0])
                else:
                    if check.split(':')[0] not in hosts_failed:
                        hosts_failed.append(check.split(':')[0])
    return hosts_failed

