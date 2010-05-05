# -*- coding: utf-8 -*-
"""Controllers for the tgext.xmlrpc application."""

__all__ = ['XmlRpcController', 'xmlrpc', 'InvalidXmlRpcType']

import xmlrpclib
import urllib

from decorator import decorator

from tg import request, response, expose
from tg.controllers import TGController
from tg.decorators import Decoration

class InvalidXmlRpcType(Exception):
    pass

#def xmlrpc(signatures, helpstr=""):
    #def call(func, *p, **kw):
        #response.content_type="text/xml"
        #try:
            #parms, method = xmlrpclib.loads(request.body)
        #except:
            #parms, method = xmlrpclib.loads(urllib.unquote_plus(request.body))
        #return xmlrpclib.dumps(func(p[0], *parms))
    #deco = decorator(call)
    #Decoration.get_decoration(deco)
    #deco.signatures = signatures
    #deco.helpstr = helpstr
    #return deco

class xmlrpc(object):
    def __init__(self, signatures, helpstr=""):
        self.signatures = signatures
        self.helpstr = helpstr
        
    def __call__(self, func):
        deco = decorator(self.wrap, func)
        Decoration.get_decoration(deco)
        deco.signatures = self.signatures
        deco.helpstr = self.helpstr
        return deco
    
    def wrap(self, func, *p, **kw):
        response.headers['Content-Type'] = "text/xml"
        try:
            parms, method = xmlrpclib.loads(request.body)
        except:
            parms, method = xmlrpclib.loads(urllib.unquote_plus(request.body))
        x=func(p[0], *parms)
        return xmlrpclib.dumps(x)
        # TODO: wrap func such that the content-type will always be set
        # properly, and the xml dump will always happen automatically
        
class XmlRpcController(TGController):
    @expose()
    def index(self):
        return "hello world"
    
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
                    # TODO: Generate XMLRPC Fault here
                    pass
            
        # TODO: Check for special methods (help/etc) and return them when appropriate
        mvals = method.split('.')
        if len(mvals) > 1:
            subcon = getattr(self, mvals[0], None)
            if subcon:
                if isinstance(subcon, XmlRpcController):
                    return subcon._dispatch(state, remainder, parms, "".join(method[1:]))
                else:
                    return subcon._dispatch_controller(mvals[0], state.controller, state, mvals[1:])
            else:
                return self._dispatch_first_found_default_or_lookup(state, remainder)
        else:
            method = getattr(state.controller, mvals[0], None)
            if method:# and getattr(method, 'signatures', None) is not None:
                state.add_method(method, [])
                return state
            # TODO: Finish here. Need to set state/remainder properly to handle the existing method, or 404 if it doesn't exist/isn't exposed
        return self._dispatch_first_found_default_or_lookup(state, remainder)
