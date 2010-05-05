# -*- coding: utf-8 -*-
"""Controllers for the tgext.xmlrpc application."""

__all__ = ['XmlRpcController', 'xmlrpc', 'InvalidXmlRpcType']

import xmlrpclib
import urllib

from tg import request
from tg.controllers import TGController

class InvalidXmlRpcType(Exception):
    pass

class xmlrpc(object):
    def __init__(self, signatures, helpstr=""):
        self.signatures = signatures
        self.helpstr = helpstr
        
    def __call__(self, func):
        func.signatures = self.signatures
        func.helpstr = self.helpstr
        # TODO: wrap func such that the content-type will always be set properly, and the xml dump will always happen automatically
        
class XmlRpcController(TGController):
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
            if subcon and isinstance(subcon, XmlRpcController):
                return subcon._dispatch(state, remainder, parms, "".join(method[1:]))
        else:
            method = getattr(self, mvals[0], None)
            # TODO: Finish here. Need to set state/remainder properly to handle the existing method, or 404 if it doesn't exist/isn't exposed
        return "goodbye cruel world"
    
