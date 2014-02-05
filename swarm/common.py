"""Common operations for all Swarm commands and tools."""
#
# Copyright (C) 2013 by R. Lindsay Todd.
# All rights reserved.
#

import argparse
from configparser import ConfigParser, ExtendedInterpolation
import logging, logging.handlers

__all__ = [ 'SwarmBase' ]

class SwarmBase(object):

    def __init__(self, p=None):
        if p is None:
            p = argparse.ArgumentParser()
        self.p = p
        self.prepare_common_options()

    def parse_args(self):
        """Parse the arguments."""
        self.args = self.p.parse_args()
        self.process_common_options()

    def prepare_common_options(self):
        """Add common options to the parser."""

        p = self.p
        p.add_argument('--config', type=argparse.FileType('rt'),
                       help="Configuration file for local swarm installation",
                       default="swarm.cfg")
        p.add_argument('--log', help='Location for logging', nargs='?')
        p.add_argument('--verbosity', type=int, choices=range(4), default=1)


    def process_common_options(self):
        """Process arguments affecting configuration, logging, etc."""

        args = self.args
        cfg = ConfigParser(interpolation=ExtendedInterpolation())
        if args.config is not None:
            cfg.read_file(args.config)
            args.config.close()
        # FIXME: Other files, e.g., in home directory

        # Start the logging.
        logger = logging.getLogger('swarm')
        logfile = args.log
        if logfile is None:
            handler = logging.handlers.SysLogHandler(address='/dev/log')
        elif logfile in ('-', 'stderr'):
            handler = logging.StreamHandler()
        else:
            handler = logging.FileHandler(logfile)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        verbosity = args.verbosity
        if verbosity >= 3:
            logger.setLevel(logging.DEBUG)
        elif verbosity >= 2:
            logger.setLevel(logging.INFO)
        elif verbosity >= 1:
            logger.setLevel(logging.WARN)
        else:
            logger.setLevel(logging.ERROR)

        self.logger = logger
        self.cfg = cfg
