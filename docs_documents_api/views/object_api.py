 
from flask import Blueprint, request, abort
from flask import current_app as app


# This is the blueprint object that gets registered into the app in blueprints.py.
object_api = Blueprint('object_api', __name__)
 
@object_api.route("/<region>/objects/<doc_type>/titles/<title>/documents/<document>/versions/<version>/objects/<object_no>")
def _get_object_data(region, doc_type, title, document, version, object_no):
    app.logger.debug('get data for : {} {} {} {}'.format(doc_type, document, version, object_no))
    repo = request.headers.get('X-DOCS-REPO', region)
    try:
        handler = app.handlers.handler(repo, doc_type)
    except:
        app.logger.debug('No handler available for doc_type: {}'.format(doc_type))
        abort(400, 'No handler available for doc_type: {}'.format(doc_type))
    titles = handler.get_data(title, document, version, object_no)
    return titles

@object_api.route("/<region>/objects/<doc_type>/uuids/<uuid>", methods=['GET'] )
def _get_data(region, doc_type, uuid):
    app.logger.debug('set metadata for : {} {}'.format(doc_type, uuid))
    repo = request.headers.get('X-DOCS-REPO', region)
    try:
        handler = app.handlers.handler(repo, doc_type)
    except:
        app.logger.debug('No handler available for doc_type: {}'.format(doc_type))
        abort(400, 'No handler available for doc_type: {}'.format(doc_type))
    metadata = request.json   
    results = handler.get_data(uuid)
    return results