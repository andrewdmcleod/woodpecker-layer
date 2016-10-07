#!/usr/bin/env python3

import re
import unittest
import amulet


class TestDeploy(unittest.TestCase):
    """
    Deploy 2 peers, test peering and remote checks with peers 
    """

    @classmethod
    def setUpClass(cls):
        cls.d = amulet.Deployment(series='xenial')
        #self.d.add('woodpecker', charm='woodpecker', units=2)
        cls.d.add('woodpecker', charm='~admcleod/woodpecker', units=2)
        cls.d.setup(timeout=900)
        cls.woodpecker_0 = cls.d.sentry['woodpecker'][0]
        cls.woodpecker_1 = cls.d.sentry['woodpecker'][1]

    def test_peering(self):
        self.d.configure('woodpecker', {'check_ports': '31337,31338'})
        self.d.sentry.wait_for_messages({'woodpecker': 'all peer checks ok, no host checks defined'}, timeout=120)

    # following test is commented out until this bug is resolved;
    # https://bugs.launchpad.net/juju/+bug/1623480
    #def test_check_local_hostname(self):
    #   self.d.sentry.wait_for_messages({'woodpecker': {re.compile('.*hostname ok.*'}}, timeout=60)
        
    def test_config_break_remote_check(self):
        print ('Test break remote check, then fix it...')
        """
        Set a bad test string, make sure its broken, and then set a good string
        """
        test_string = 'label:no_such_hostname:65534'
        self.d.configure('woodpecker', {'check_list': test_string})
        self.d.sentry.wait_for_messages({'woodpecker': {re.compile('.*host check failed.*')}}, timeout=60)
        test_string = 'label:{}:31338'.format(self.woodpecker_0.info['public_address'])
        self.d.configure('woodpecker', {'check_list': test_string})
        self.d.sentry.wait_for_messages({'woodpecker': {re.compile('.*all host checks ok')}}, timeout=60)

    def test_break_peering(self):
        print ('Test break peering...')
        """
        Peering will already have passed "ok" at this point, and listening on 2 ports
        SSH in and kill the process listening on one peer on one port
        """
        self.woodpecker_0.run("sudo pkill nc")
        self.woodpecker_1.run("sudo pkill nc")
        self.d.sentry.wait_for_messages({'woodpecker': re.compile('.*peer check failed.*')})

    def test_teardown(self):
        """
        Make sure teardown hooks work cleanly
        """
        self.d.destroy_service('woodpecker')

if __name__ == '__main__':
    unittest.main()
