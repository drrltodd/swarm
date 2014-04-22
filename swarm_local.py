#! /usr/bin/env python
#
# Copyright (C) 2014 by R. Lindsay Todd.
# All rights reserved.
#

"""Main program for local swarm."""

import argparse
#
from swarm.common import *

def _main():

    # Define command line parser.
    p = argparse.ArgumentParser(description='Swarm local')
    sb = SwarmBase(p)
    p.add_argument('--daemon', help='Run as a daemon',
                   action='store_true')

    # Parse
    sb.parse_args()
    args = sb.args
    logger = sb.logger



if __name__ == '__main__':
    _main()
