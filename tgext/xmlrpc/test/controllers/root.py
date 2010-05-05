from tg import config, expose, request, require
from tg.controllers import TGController

from repoze.what.predicates import Not, is_anonymous, has_permission

class RootController(TGController):
    @expose()
    def index(self, *p, **kw):
        return 'hello world'

