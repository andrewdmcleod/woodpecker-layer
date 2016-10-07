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
        self.d.sentry.wait_for_messages({'woodpecker': re.compile('peer|host')}, timeout=120)

    # following test is commented out until this bug is resolved;
    # https://bugs.launchpad.net/juju/+bug/1623480
    #def test_check_local_hostname(self):
    #   self.d.sentry.wait_for_messages({'woodpecker': {re.compile('.*hostname ok.*'}}, timeout=60)
        
    def test_break_dns_single(self):
        print ('Test break dns single...')
        """Break DNS on one unit, make sure DNS check fails, fix DNS, toggle back"""
        self.d.sentry.wait_for_messages({'woodpecker': 'icmp ok, dns ok'}, timeout=60)
        self.woodpecker_0.run("sudo mv /etc/resolv.conf /etc/resolv.conf.bak")
        self.woodpecker_0.run("hooks/update-status")
        self.d.sentry.wait_for_messages({'woodpecker': {re.compile('.*dns failed.*')}}, timeout=60)
        self.woodpecker_0.run("sudo mv /etc/resolv.conf.bak /etc/resolv.conf")
        self.woodpecker_0.run("hooks/update-status")
        self.d.sentry.wait_for_messages({'woodpecker': 'icmp ok, dns ok'}, timeout=60)

    def test_break_dns_all(self):
        print ('Test break dns all...')
        """Set DNS with action to 255.255.255.255 - All units should fail DNS."""
        self.d.configure('woodpecker', {'dns_server': '255.255.255.255'})
        self.woodpecker_0.run("hooks/update-status")
        self.woodpecker_1.run("hooks/update-status")
        self.d.sentry.wait_for_messages({'woodpecker': re.compile('icmp ok,.*dns failed.*')})
        self.d.configure('woodpecker', {'dns_server': ''})
        self.woodpecker_0.run("hooks/update-status")
        self.woodpecker_1.run("hooks/update-status")
        self.d.sentry.wait_for_messages({'woodpecker': 'icmp ok, dns ok'})

    def test_break_ping_single(self):
        print ('Test break ping single')
        """Take primary interface down and make sure ICMP fails."""
        self.woodpecker_1.run("(sudo service networking stop; sleep 60 ; sudo service networking start)&")
        self.woodpecker_1.run("hooks/update-status")
        self.d.sentry.wait_for_messages({'woodpecker': {re.compile('icmp failed.*')}}, timeout=120)
        self.woodpecker_1.run("hooks/update-status")
        self.d.sentry.wait_for_messages({'woodpecker': {re.compile('icmp ok.*')}}, timeout=120)

if __name__ == '__main__':
    unittest.main()
