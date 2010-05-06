# -*- coding: utf-8 -*-
"""Controllers for the tgext.xmlrpc application."""

__all__ = ['XmlRpcController', 'xmlrpc', 'InvalidXmlRpcType']

import xmlrpclib
import urllib

from decorator import decorator

from pylons import config

from tg import request, response, expose
from tg.controllers import TGController
from tg.decorators import Decoration

class InvalidXmlRpcType(Exception):
    pass

class xmlrpc(object):
    def __init__(self, signatures, helpstr=""):
        self.signatures = signatures
        self.helpstr = helpstr
        
    def __call__(self, func):
        deco = decorator(self.wrap, func)
        exposed = Decoration.get_decoration(deco)
        deco.signatures = self.signatures
        deco.helpstr = self.helpstr
        exposed.register_template_engine(\
            'text/xml', config.get('default_renderer', ['mako'])[0],
            '', [])
        return deco
    
    def wrap(self, func, *p, **kw):
        try:
            try:
                parms, method = xmlrpclib.loads(request.body)
            except:
                parms, method = xmlrpclib.loads(urllib.unquote_plus(request.body))
            rpcresponse = xmlrpclib.dumps((func(p[0], *parms),), methodresponse=1)
        except xmlrpclib.Fault, fault:
            rpcresponse = xmlrpclib.dumps(fault)
        except Exception, e:
            rpcresponse = xmlrpclib.dumps(xmlrpclib.Fault(1, "%s:%s" % (str(type(e)), str(e))))
        return rpcresponse
        
class XmlRpcController(TGController):
    @expose()
    def index(self):
        return "hello world"
    
    @expose(content_type='text/xml')
    def rpcfault(self, *p, **kw):
        return xmlrpclib.dumps(xmlrpclib.Fault(1, p[0]))
    
    def _dispatch(self, state, remainder, parms=None, method=None):
        if remainder:
            return self._dispatch_first_found_default_or_lookup(state, remainder)
        
        if not parms and not method:
            try:
                parms, method = xmlrpclib.loads(request.body)
            except:
                try:
                    parms, method = xmlrpclib.loads(urllib.unquote_plus(request.body))
                except:
                    state.add_method(self.rpcfault, ['Unable to decode request body "||%s||"' % (request.body)])
                    return state
            
        # TODO: Check for special methods (help/etc) and return them when appropriate
        mvals = method.split('.')
        if len(mvals) > 1:
            subcon = getattr(self, mvals[0], None)
            if subcon:
                if isinstance(subcon, XmlRpcController):
                    return subcon._dispatch(state, remainder, parms, "".join(mvals[1:]))
                else:
                    return subcon._dispatch_controller(mvals[0], self, state, mvals[1:])
            else:
                return self._dispatch_first_found_default_or_lookup(state, remainder)
        else:
            method = getattr(self, mvals[0], None)
            if method:
                if getattr(method, 'signatures', None) is not None:
                    state.add_method(method, [])
                    return state
                else:
                    state.add_method(self.rpcfault, ['Invalid XMLRPC Method'])
                    return state
        return self._dispatch_first_found_default_or_lookup(state, remainder)
