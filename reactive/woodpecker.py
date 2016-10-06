# pylint: disable=unused-argument
from charms.reactive import when, when_not, set_state, remove_state
from charmhelpers.core import hookenv
from charms.layer.woodpecker_tools import (check_peers, check_remote_hosts,
                                           safe_status, woodpecker_listen,
                                           _set_states)


config = hookenv.config()
check_hosts = config.get('check_list')
if check_hosts:
        set_state('check_hosts')
else:
        remove_state('check_hosts')


@when_not('woodpecker.listening')
def open_woodpecker_port():
    woodpecker_listen()
    set_state('woodpecker.listening')


@when_not('woodpecker.joined', 'check_hosts')
def no_peers():
    safe_status('waiting', 'waiting for peers, no host checks defined')


@when('woodpecker.joined', 'woodpecker.listening')
def check_peers_joined(woodpecker):
    '''
    We do not dismiss joined here so that this check reruns
    every time we do an update-status
    '''

    nodes = woodpecker.get_nodes()
    _set_states(check_peers(peers=nodes))


@when('check_hosts')
def check_remote_hosts_labels():
    check_results = check_remote_hosts()
    _set_states(hosts=check_results)
