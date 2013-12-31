#! /usr/bin/env python
#
# Copyright (C) 2013 by R. Lindsay Todd.
# All rights reserved.
#

"""Invoke a resource agent.

This command may be useful in an application, but its most first use
was to quickly get some code working for parsing and running resource
agent methods."""

import argparse
import logging
#
from swarm.common import *
from swarm import ra

def _main():

    # Define command line parser.
    p = argparse.ArgumentParser(description='Invoke a method on a resource agent.')
    sb = SwarmBase(p)
    p.add_argument('ra', help='Name of resource agent')
    p.add_argument('method', help='Name of method to invoke')
    p.add_argument('--name', help='Name of resource')

    # Parse, handling common operations.
    sb.parse_args()
    args = sb.args
    logger = sb.logger

    # Handle some defaulting.
    if args.name is None:
        args.name = args.ra.split(':')[-1]

    # Get a resource agent handle.
    rah = ra.open_resource_agent(sb, args.name, args.ra)
    print(rah)

if __name__ == '__main__':
    _main()
