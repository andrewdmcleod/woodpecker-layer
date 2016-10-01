# pylint: disable=unused-argument
from charms.reactive import when, when_not, set_state, remove_state
from charms.reactive.bus import get_states
from charmhelpers.core import hookenv
from charms.layer.woodpecker_tools import check_peers, check_remote_hosts, safe_status, woodpecker_listen


config = hookenv.config()
check_hosts = config.get('check_list')
if check_hosts:
        set_state('check_hosts')
else:
        remove_state('check_hosts')

def _set_states(check_result):
    if 'fail' in check_result['icmp']:
        set_state('woodpecker-peer.failed')
    else:
        remove_state('woodpecker-icmp.failed')
    if 'fail' in check_result['dns']:
        set_state('woodpecker-dns.failed')
    else:
        remove_state('woodpecker-dns.failed')


@when_not('woodpecker.listening')
def open_woodpecker_port():
    woodpecker_listen()
    set_state('woodpecker.listening')

@when_not('woodpecker.joined', 'check_hosts')
def no_peers():
    safe_status('waiting', 'No TCP checks configured, Waiting for peers...')


@when('woodpecker.joined')
def check_peers_joined(woodpecker):
    '''
    We do not dismiss joined here so that this check reruns
    every time we do an update-status
    '''

    nodes = woodpecker.get_nodes()
    _set_states(check_peers(nodes))

@when('check_hosts')
def check_hosts(woodpecker):
    check_results = check_remote_hosts()
    active_states = get_states()
    for result in check_results:
        result_string = result.split(":")
        result_label = result_string[0]
        for state in active_states:
            if state not in check_results:
                remove_state(state)
        set_state(result)

