#!/usr/bin/env python3

import unittest
import amulet


class TestDeploy(unittest.TestCase):
    """
    Trivial deployment test for Woodpecker
    """

    def test_deploy(self):
        self.d = amulet.Deployment(series='xenial')
        #self.d.add('woodpecker', charm='woodpecker')
        self.d.add('woodpecker', charm='~admcleod/woodpecker')
        self.d.setup(timeout=900)
        self.d.sentry.wait_for_messages({'woodpecker': 'waiting for peers, no host checks defined'}, timeout=3600)

if __name__ == '__main__':
    unittest.main()
