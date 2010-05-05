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
                                   'renderers': ['json'],
                                   'use_legacy_renderer': False,
                                   'default_renderer':'json',
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
        
    def test_xmlrpc_too_many_args(self):
        try:
            resp = self.app.get('/xmlrpc/myurl/what')
        except Exception, e:
            if '404 Not Found' in str(e):
                pass
            else:
                raise
    def test_xmlrpc_correct_argcount(self):
        resp = self.app.post('/xmlrpc', xmlrpclib.dumps((1,2), 'tg.xmlrpc.addit'))
        assert 'goodbye' in resp, resp
        
# tests to write:
# url continues past current location of xmlrpc controller
# url stops at current xmlrpc controller
