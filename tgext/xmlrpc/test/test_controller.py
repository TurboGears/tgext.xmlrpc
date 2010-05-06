import os, sys
import xmlrpclib

from pylons import config
from tg.test_stack import TestConfig, app_from_config
from tg.util import Bunch

import tgext.xmlrpc.test

root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, root)
paths=Bunch(
            root=root,
            controllers=os.path.join(root, 'controllers'),
            static_files=os.path.join(root, 'static'),
            templates=os.path.join(root, 'templates')
            )

base_config = TestConfig(folder = 'rendering',
                         values = {'use_sqlalchemy': False,
                                   'use_toscawidgets2': False,
                                   'full_stack': False,
                                   'pylons.helpers': Bunch(),
                                   'renderers': ['genshi'],
                                   'use_legacy_renderer': False,
                                   'default_renderer':'genshi',
                                   'use_dotted_templatenames': True,
                                   'paths':paths,
                                   'package':tgext.xmlrpc.test,
                                   'beaker.session.secret': 'ChAnGeMe',
                                   'beaker.session.key': 'tgext.xmlrpc.test',
                                  }
                         )

class TestXmlRpcController:
    def __init__(self):
        self.app = app_from_config(base_config)
  
    def test_tgbase(self):
        resp = self.app.get('/')
        assert 'hello world' in resp, resp
        
    def test_helppage(self):
        resp = self.app.get('/xmlrpc')
        assert 'Help String' in resp, resp
        assert 'Method Signature' in resp, resp
        assert 'Returns' in resp, resp
        assert 'Parameters' in resp, resp
        assert 'addit' in resp, resp
        assert 'genfault' in resp, resp
        assert 'subrpc.joinit' in resp, resp
    
    def test_xmlrpc_correct_argcount(self):
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps((1,2), 'addit'))
        resp = xmlrpclib.loads(resp.body)
        assert resp[0][0] == 3, resp

    def test_subrpc(self):
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps(("hello","world","i","mean","it"), 'subrpc.joinit'))
        resp = xmlrpclib.loads(resp.body)
        assert resp[0][0] == 'hello world i mean it', resp
        
    def test_system_listmethods(self):
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps((), 'system.listMethods'))
        assert 'addit' in resp, resp
        assert 'genfault' in resp, resp
        assert 'subrpc.joinit' in resp, resp
    
    def test_system_methodsignature(self):
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps(('addit',), 'system.methodSignature'))
        assert 'int' in resp, resp
        assert 'string' in resp, resp
    
    def test_system_methodhelp(self):
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps(('addit',), 'system.methodHelp'))
        assert 'sums an array of numbers' in resp, resp
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps(('subrpc.joinit',), 'system.methodHelp'))
        assert 'joins an array of strings with spaces' in resp, resp
        
    def test_system_methodsignature_bad(self):
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps(('subrpc.nonexistant',), 'system.methodSignature'))
        assert 'Invalid method' in resp, resp

    def test_system_methodhelp_bad(self):
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps(('subrpc.nonexistant',), 'system.methodHelp'))
        assert 'Invalid method' in resp, resp
    
    def test_system_badcall(self):
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps((), 'system.badcall'))
        assert 'Invalid system method called' in resp, resp
        
    def test_xmlrpc_too_many_args(self):
        try:
            resp = self.app.get('/xmlrpc/myurl/what')
        except Exception, e:
            if '404 Not Found' in str(e):
                return
            else:
                raise
        assert 1==0, "too many args passed, and it should not have"

    def test_bad_xmlrpc_call(self):
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps((1,2), 'sumit'))
        assert 'Invalid XMLRPC Method' in resp, resp

    def test_bad_xml_post(self):
        resp = self.app.post('/xmlrpc', 'hello <world "/">')
        assert 'Unable to decode request body' in resp, resp
    
    def test_genfault(self):
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps((1,2), 'genfault'))
        assert '<name>faultCode</name>' in resp, resp
        