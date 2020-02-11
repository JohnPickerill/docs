
from docs_documents_api.exceptions import ApplicationError

class handlers:

    _handlers = {}

    def __init__(self, app):
        self.app = app

    def add(self, repo, doc_type, handler):
        repo = repo.lower()
        doc_type = doc_type.lower()
        r = self._handlers.setdefault(repo, {})
        r[doc_type] = handler
        self.app.logger.debug('add handler {}.{}'.format(repo, doc_type))

    def handler(self, repo, doc_type):
        repo = repo.lower()
        doc_type = doc_type.lower()
        try:
            handler = self._handlers[repo][doc_type]    
        except Exception as e :
            errstr = "Could not find handler for repo.doc_type {}.{}".format(repo, doc_type)
            self.app.logger.debug(errstr)
            raise ApplicationError(errstr,'BADREQUEST', 400, True) 
        return handler