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
        self.daemon = self.args.daemon
