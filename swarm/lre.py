#! /usr/bin/env python
#
# Copyright (C) 2014 by R. Lindsay Todd.
# All rights reserved.
#

"""Local resource engine"""

__all__ = [ 'SwarmLocalApp' ]

from swarm.common import *

class SwarmLocalApp(SwarmBase):

    def __init__(self, p=None):
        SwarmBase.__init__(self, p)
        p = self.p
        p.add_argument('--daemon', help='Run as a daemon',
                       action='store_true')

    def parse_args(self):
        SwarmBase.parse_args(self)
        self.process_options()

    def process_options(self):
        """Process options, reference config file."""

        args = self.args
        cfg = self.cfg

        import os.path
        raListFile = cfg['Paths']['ra-list']
        raListFile = os.path.expanduser(raListFile)

        # FIXME: What if the file doesn't exist?
        # FIXME: Need to do MUCH more, and have options, etc.
        raList = []
        with open(raListFile) as f:
            for L in f:
                raList.append(L)
        self.raList = raList

        #
        self.daemon = self.args.daemon
