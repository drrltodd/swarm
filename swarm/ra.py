#! /usr/bin/env python
#
# Copyright (C) 2013 by R. Lindsay Todd.
# All rights reserved.
#

"""Resource agents"""

__all__ = [ 'ResourceAgent',
            'OcfResourceAgent', 'ServiceResourceAgent',
            'open_resource_agent' ]

class RC:
    success = 0
    err_generic = 1
    err_args = 2
    err_unimplemented = 3
    err_perm = 4
    err_installed = 5
    err_configured = 6
    not_running = 7
    running_master = 8
    failed_master = 9


class ResourceAgentError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ResourceAgent(object):

    def __init__(self, sb, name, resloc):
        """Initialize the resource agent object.
        Parameters:
            sb = Command object
            name = Name of the resource agent
            resloc = Location of the resource agent
        """
        self.sb = sb
        self.name = name
        self.resloc = resloc
        self.parameters = {}
        self.allowed_actions = {}

    def invoke(self, op, params, meta, timeout):
        """Invoke a method on the resource agent."""
        # Make sure the operation is supported
        sb = self.sb
        logger = sb.logger
        adict = self.allowed_actions
        if op not in adict:
            logger.error('Operation %s not implemented by resource %s',
                         op, self.name)
            return RC.err_unimplemented
        if timeout is None and 'timeout' in adict[op]:
            try:
                timeout = int(adict[op]['timeout'])
            except:
                logger.error('Invalid timeout specified for operation %s by resource %s',
                             op, self.name)
                return RC.err_generic
        # Make sure each parameter is supported
        p = {}
        pdict = self.parameters
        for pn in params:
            if pn in pdict:
                # FIXME: Check type, etc.
                p[pn] = params[pn]
            else:
                return RC.err_args
        for pn in pdict:
            if pn not in p:
                dv = pdict[pn]['default']
                if dv is not None:
                    p[pn] = dv
        return self._invoke(op, p, meta, timeout)


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
        so,se,rc = self._invoke_get_results('meta-data', {})
        if rc == 0:
            import xml.etree.ElementTree as ET
            eroot = ET.fromstring(so)
            for E in eroot:
                if E.tag == 'parameters':
                    pdict = self.parameters
                    for P in E:
                        pname = P.attrib['name']
                        punique = int(P.attrib.get('unique', 0))
                        prequired = int(P.attrib.get('required', 0))
                        pshortdesc = ''
                        plongdesc = ''
                        ptype = 'string'
                        pdefault = None
                        for PA in P:
                            if PA.tag == 'shortdesc':
                                # FIXME: Need to handle language
                                pshortdesc = PA.text
                            elif PA.tag == 'longdesc':
                                # FIXME: Need to handle language
                                plongdesc = PA.text
                            elif PA.tag == 'content':
                                # FIXME: default 'default' depends on 'type'
                                ptype = PA.attrib.get('type', 'string')
                                pdefault = PA.attrib.get('default', None)
                        pdict[pname] = {
                            'name': pname,
                            'unique': punique,
                            'required': prequired,
                            'shortdesc': pshortdesc,
                            'longdesc': plongdesc,
                            'type': ptype,
                            'default': pdefault }
                elif E.tag == 'actions':
                    adict = self.allowed_actions
                    for A in E:
                        adict[A.attrib['name']] = A.attrib


    def _genEnv(self, params, meta):
        """Generate environment mapping for OCF resources"""
        import os
        env = dict(os.environ)
        for k,v in params.items():
            env['OCF_RESKEY_'+k] = v
        for k,v in meta.items():
            k1 = k.replace('-', '_')
            env['OCF_RESKEY_CRM_meta_'+k1] = v
        env['OCF_RA_VERSION_MAJOR'] = "1"
        env['OCF_RA_VERSION_MINOR'] = "0"
        env['OCF_ROOT'] = self._radir
        env['OCF_RESOURCE_INSTANCE'] = self.name
        # FIXME: OCF_RESOURCE_TYPE
        # FIXME: OCF_CHECK_LEVEL
        return env

    def _invoke(self, methname, params, meta, timeout):
        import subprocess
        kw = {}
        if timeout is not None:
            kw['timeout'] = timeout
        rc = subprocess.call([self._rapath, methname],
                             env=self._genEnv(params, meta),
                             **kw)
        return rc

    def _invoke_get_results(self, methname, params, meta={}):
        import subprocess
        P = subprocess.Popen([self._rapath, methname],
                             env=self._genEnv(params, meta),
                             close_fds=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        (so,se) = P.communicate(None)
        return so,se,P.returncode

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
    """Open a resource agent from its specification.
    Parameters:
        sb = Command object
        name = Name of the resource agent
        resloc = Location of the resource agent
    Returns:
        - Handle to the resource agent object
    """
    
    namespace = resloc.split(':')[0]
    if namespace == 'ocf':
        rah = OcfResourceAgent(sb, name, resloc)
    elif namespace == 'lsb':
        rah = ServiceResourceAgent(sb, name, resloc)
    else:
        sb.logger.error('Unknown resource class %s for %s', namespace, resloc)
        raise ResourceAgentError('oops')

    return rah
