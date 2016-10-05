# pylint: disable=unused-argument
from charms.reactive import when, when_not, set_state, remove_state
from charmhelpers.core import hookenv
from charms.layer.woodpecker_tools import check_peers, check_remote_hosts, safe_status, woodpecker_listen


config = hookenv.config()
check_hosts = config.get('check_list')
if check_hosts:
        set_state('check_hosts')
else:
        remove_state('check_hosts')


def _set_states(peers=None, hosts=None):
    # if peers calls this, hosts is none
    # if hosts calls its, peers is none
    # clearly i need a way to store values somewhere outside of the function
    # i will call a 'check all' function which will do so
    # it will just not rely on reactive states

    hookenv.log('_set_states PEERS: {}'.format(peers))
    hookenv.log('_set_states HOSTS: {}'.format(hosts))
    if peers is None:
        peer_status = 'waiting for peers'
    elif peers != []:
        set_state('woodpecker-peer.failed')
        peer_status = 'peer check failed: ' + str(peers)
    else:
        remove_state('woodpecker-peer.failed')
        peer_status = 'peer check ok'
    if hosts is None:
        hostcheck_status = ', no host checks defined'
    elif hosts != []:
        set_state('woodpecker-hosts.failed')
        hostcheck_status = ', host check failed: ' + str(hosts)
    else:
        remove_state('woodpecker-hosts.failed')
        hostcheck_status = ', host check ok'
    if 'failed' in peer_status or 'failed' in hostcheck_status:
        workload = 'blocked'
    else:
        workload = 'active'
    safe_status(workload, peer_status + hostcheck_status)


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
    _set_states(check_hosts(hosts=check_results))
    #for result in check_results:
    #    result_string = result.split(":")
    #    result_label = result_string[0]
    #    for state in active_states:
    #        if state not in check_results:
    #            remove_state(state)
    #    set_state(result)

