# pylint: disable=unused-argument
from charms.reactive import when, when_not, set_state, remove_state, 
from charms.reactive.bus import get_states
from charmhelpers.core import hookenv
from charms.layer.woodpecker_tools import check_peers, check_hosts


config = hookenv.config()
check_hosts = config.get('check_ip_port_tcp')
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


@when_not('woodpecker.joined', 'check_hosts')
def no_peers():
    hookenv.status_set('waiting', 'Waiting for peers...')


@when('woodpecker.joined')
def check_peers_joined(woodpecker):
    '''
    We do not dismiss joined here so that this check reruns
    every time we do an update-status
    '''

    nodes = woodpecker.get_nodes()
    _set_states(check_peers(nodes))

@when('check_hosts')
def check_tcp_remote(woodpecker):
    check_results = check_hosts()
    active_states = get_states()
    for result in check_results:
        result_string = result.split(":")
        result_label = result_string[0]
        set_state(result)

