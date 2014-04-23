#! /usr/bin/env python
#
# Copyright (C) 2014 by R. Lindsay Todd.
# All rights reserved.
#

"""Main program for local swarm."""

import argparse
#
from swarm.lre import *

def _main():

    # Define command line parser.
    p = argparse.ArgumentParser(description='Swarm local')
    sla = SwarmLocalApp(p)

    # Parse
    sla.parse_args()
    args = sla.args
    logger = sla.logger

    print (sla.daemon)



if __name__ == '__main__':
    _main()
