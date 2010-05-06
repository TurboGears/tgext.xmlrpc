from tg import config, expose, request, require
from tg.controllers import TGController

from tgext.xmlrpc import XmlRpcController, xmlrpc
from repoze.what.predicates import Not, is_anonymous, has_permission

class TestRpcSubController(XmlRpcController):
    @xmlrpc([['string', 'array']], helpstr='joins an array of strings with spaces')
    def joinit(self, *p, **kw):
        return " ".join(p)
    
class TestRpcController(XmlRpcController):
    subrpc = TestRpcSubController()
    
    @xmlrpc([['int', 'array']], helpstr='sums an array of numbers')
    def addit(self, *p, **kw):
        return sum(p)
    
    @xmlrpc([['fault', 'none'], ['fault', 'int', 'string', 'struct', 'array']])
    def genfault(self, *p, **kw):
        1/0
        
    def sumit(self, *p, **kw):
        return sum(p)
    
class RootController(TGController):
    @expose()
    def index(self, *p, **kw):
        return 'hello world'

    xmlrpc = TestRpcController()
    