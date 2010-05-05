from tg import config, expose, request, require
from tg.controllers import TGController

from tgext.xmlrpc import XmlRpcController, xmlrpc
from repoze.what.predicates import Not, is_anonymous, has_permission

class TestRpcController(XmlRpcController):
    @xmlrpc([])
    def addit(self, p1, p2, *p, **kw):
        return []
    
    def sumit(self, p1, p2):
        return p1+p2
    
class RootController(TGController):
    @expose()
    def index(self, *p, **kw):
        return 'hello world'

    xmlrpc = TestRpcController()
    