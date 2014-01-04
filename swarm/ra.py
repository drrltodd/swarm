#! /usr/bin/env python
#
# Copyright (C) 2013 by R. Lindsay Todd.
# All rights reserved.
#

"""Resource agents"""

__all__ = [ 'ResourceAgent',
            'OcfResourceAgent', 'ServiceResourceAgent',
            'open_resource_agent' ]

class ResourceAgentError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ResourceAgent(object):

    def __init__(self, sb, name, resloc):
        self.sb = sb
        self.name = name
        self.resloc = resloc


class OcfResourceAgent(ResourceAgent):

    def __init__(self, sb, name, resloc):
        ResourceAgent.__init__(self, sb, name, resloc)

        # Attempt to open the resource agent.
        import os.path
        rd = sb.cfg['Paths']['ocf-resource-agents']
        rd = os.path.expanduser(rd)
        #
        self._radir = rd
        self._rapath = os.path.join(rd, 'resource.d', *(resloc.split(':')[1:]))
        #
        self._invoke('meta-data', {})


    def _genEnv(self, params):
        """Generate environment mapping for OCF resources"""
        env = {}
        for k,v in params.items():
            env['OCF_RESKEY_'+k] = v
        env['OCF_RA_VERSION_MAJOR'] = "1"
        env['OCF_RA_VERSION_MINOR'] = "0"
        #env['OCF_ROOT'] = "/usr/lib/ocf"
        env['OCF_ROOT'] = self._radir
        env['OCF_RESOURCE_INSTANCE'] = self.name
        # FIXME: OCF_RESOURCE_TYPE
        # FIXME: OCF_CHECK_LEVEL
        return env

    def _invoke(self, methname, params):
        import subprocess
        rc = subprocess.call([self._rapath, methname],
                             env=self._genEnv(params))

    def status(self, params):
        rc = subprocess('%s status' % (self.resloc,),
                        env=self._genEnv(params))

    def start(self, params):
        rc = subprocess('%s start' % (self.resloc,),
                        env=self._genEnv(params))

    def stop(self, params):
        rc = subprocess('%s stop' % (self.resloc,),
                        env=self._genEnv(params))



class ServiceResourceAgent(ResourceAgent):

    def __init__(self, sb, name, resloc):
        ResourceAgent.__init__(self, sb, name, resloc)

    def status(self, params):
        # FIXME: Do what with params?
        rc = subprocess('service %s status' % (self.resloc,), shell=True)

    def start(self, params):
        # FIXME: Do what with params?
        rc = subprocess('service %s start' % (self.resloc,), shell=True)

    def stop(self, params):
        # FIXME: Do what with params?
        rc = subprocess('service %s stop' % (self.resloc,), shell=True)


def open_resource_agent(sb, name, resloc):
    """Open a resource agent from its specification."""
    
    namespace = resloc.split(':')[0]
    if namespace == 'ocf':
        rah = OcfResourceAgent(sb, name, resloc)
    elif namespace == 'lsb':
        rah = ServiceResourceAgent(sb, name, resloc)
    else:
        sb.logger.error('Unknown resource class %s for %s', namespace, resloc)
        raise ResourceAgentError('oops')

    return rah
