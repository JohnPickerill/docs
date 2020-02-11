import requests
import uuid
from flask import current_app, session , request, g 
from cc_utils import register_logging
from docs_documents_api.utils.handlers import handlers
from docs_documents_api.handlers.db2_titleplan import Db2_titleplan
from docs_documents_api.handlers.db2_retained import Db2_retained
from docs_documents_api.handlers.stub import Stub

class RequestsSessionTimeout(requests.Session):
    """Custom requests session class to set some defaults on g.requests"""
    def request(self, *args, **kwargs):
        # Set a default timeout for the request.
        # Can be overridden in the same way that you would normally set a timeout
        # i.e. g.requests.get(timeout=5)
        if not kwargs.get('timeout'):
            kwargs['timeout'] = current_app.config['DEFAULT_TIMEOUT']
        return super(RequestsSessionTimeout, self).request(*args, **kwargs)


def before_request():
    # Sets the transaction trace id on the global object if provided in the HTTP header from the caller.
    # Generate a new one if it has not. We will use this in log messages.
    g.trace_id = request.headers.get('X-Trace-ID', uuid.uuid4().hex)
    # We also create a session-level requests object for the app to use with the header pre-set, so other APIs
    # will receive it. These lines can be removed if the app will not make requests to other LR APIs!
    g.requests = RequestsSessionTimeout()
    g.requests.headers.update({'X-Trace-ID': g.trace_id})
    session.permanent = True  # chrome cookie expiry at end of session is unpredictable so use configured timeout


def register_extensions(app):
    """Adds any previously created extension objects into the app, and does any further setup they need."""

    register_logging(app)

    # enable sessions
    app.secret_key = app.config["APP_SECRET_KEY"]

    app.before_request(before_request)
    app.handlers = handlers(app)

    app.handlers.add('DC3A', 'titleplan', Db2_titleplan(app, 'DC3A', 'titleplan'))
    app.handlers.add('DC3A', 'retained',  Db2_retained (app, 'DC3A', 'retained'))
    app.handlers.add('STUB', 'titleplan', Stub(app, 'STUB', 'titleplan'))
    app.handlers.add('STUB', 'retained',  Stub(app, 'STUB', 'retained'))

    # All done!
    app.logger.info("Extensions registered")
