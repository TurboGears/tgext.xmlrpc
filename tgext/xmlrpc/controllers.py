# -*- coding: utf-8 -*-
"""Controllers for the tgext.xmlrpc application."""

__all__ = ['XmlRpcController', 'xmlrpc']

import xmlrpclib
import urllib

from decorator import decorator

from pylons import config

from tg import request, response, expose
from tg.controllers import TGController
from tg.decorators import Decoration

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
        header = '<html>\n<head>\n<title>XMLRPC Index Page</title>\n'
        style = '<style type="text/css">dt {font-weight:bold}</style>\n</head>\n</body>\n<dl>\n'
        footer = '</dl>\n</body>\n</html>\n'
        dlent = []
        for method in self._gather_all_methods('', self):
            dlent.append('<dt>%s</dt>\n<dd>\n<dl>\n' % (method))
            kall = self._find_method(method)
            dlent.append('<dt>Help String:</dt>\n<dd>%s</dd>\n' % (kall.helpstr))
            for sig in kall.signatures:
                retval = sig[:1]
                parms = sig[1:]
                dlent.append('<dt>Method Signature</dt>\n<dd>\n<dl>\n')
                dlent.append('<dt>Returns:</dt>\n<dd>%s</dd>\n' % (retval))
                dlent.append('<dt>Parameters:</dt>\n<dd>%s</dd>\n' % (parms))
                dlent.append('</dl>\n</dd>\n')
            dlent.append('</dl>\n')
        return "%s%s%s%s" % (header, style, ''.join(dlent), footer)
    
    @expose(content_type='text/xml')
    def rpcfault(self, *p, **kw):
        return xmlrpclib.dumps(xmlrpclib.Fault(1, p[0]))
    
    @expose(content_type='text/xml')
    def _system_methodHelp(self, *p, **kw):
        try:
            method = self._find_method(p[0])
            rpcresponse = xmlrpclib.dumps((method.helpstr,), methodresponse=1)
        except:
            rpcresponse = xmlrpclib.dumps(('Invalid method',), methodresponse=1)
        return rpcresponse
    
    @expose(content_type='text/xml')
    def _system_methodSignature(self, *p, **kw):
        try:
            method = self._find_method(p[0])
            rpcresponse = xmlrpclib.dumps((method.signatures,), methodresponse=1)
        except:
            rpcresponse = xmlrpclib.dumps(('Invalid method',), methodresponse=1)
        return rpcresponse
    
    @expose(content_type='text/xml')
    def _system_listMethods(self, *p, **kw):
        methods = self._gather_all_methods('', self)
        return xmlrpclib.dumps((methods,), methodresponse=1)
            
    def _gather_all_methods(self, prefix, controller):
        methods = []
        if prefix != '':
            prefix = prefix + '.'
        for attrname in dir(controller):
            attr = getattr(controller, attrname)
            if hasattr(attr, 'signatures'):
                methods.append('%s%s' % (prefix, attrname))
            if isinstance(attr, XmlRpcController):
                methods.extend(self._gather_all_methods(prefix + attrname, attr))
        return methods
        
    def _find_method(self, method):
        mvals = method.split('.')
        midx = 0
        controller = self
        result = None
        while not result and controller and midx < len(mvals):
            controller = getattr(controller, mvals[midx], None)
            if controller is None:
                break
            if midx == len(mvals)-1:
                result = controller
            midx = midx + 1
        return result
    
    def _dispatch(self, state, remainder, parms=None, method=None):
        if remainder:
            return self._dispatch_first_found_default_or_lookup(state, remainder)
        
        if request.method.lower() == 'get':
            state.add_method(self.index, [])
            return state
        
        if not parms and not method:
            try:
                parms, method = xmlrpclib.loads(request.body)
            except:
                try:
                    parms, method = xmlrpclib.loads(urllib.unquote_plus(request.body))
                except:
                    state.add_method(self.rpcfault, ['Unable to decode request body "||%s||"' % (request.body)])
                    return state
            
        if method.startswith('system.'):
            methodname = '_%s' % (method.replace('.', '_'))
            if not getattr(self, methodname, None):
                state.add_method(self.rpcfault, ['Invalid system method called: %s' % (method)])
            else:
                state.add_method(getattr(self, methodname), parms)
            return state

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
