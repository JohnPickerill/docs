 
from flask import Blueprint, request,  abort
from flask import current_app as app


# This is the blueprint object that gets registered into the app in blueprints.py.
document_api = Blueprint('document_api', __name__)

@document_api.route("/<region>/docs/<doc_type>/titles")
def _get_titles(region, doc_type):
    app.logger.debug('get list of titles for doc_type: {}'.format(doc_type))
    handler = app.handlers.handler(region, doc_type)  
    titles = handler.get_titles(request.args.get('start'), request.args.get('size'))
    return titles

@document_api.route("/<region>/docs/<doc_type>/titles/<title>/documents")
def _get_documents(region, doc_type, title):
    app.logger.debug('get list of titles for doc_type: {}'.format(doc_type))
    handler = app.handlers.handler(region, doc_type) 
    documents = handler.get_documents(title, request.args.get('start'), request.args.get('size'))
    return documents

@document_api.route("/<region>/docs/<doc_type>/titles/<title>/documents/<document>")
def _get_document(region, doc_type, title, document):
    app.logger.debug('get metadata for document for doc_type: {}/{}/{}'.format(
        doc_type, title, document))
    handler = app.handlers.handler(region, doc_type) 
    document = handler.get_document(title, document)
    return document

@document_api.route("/<region>/docs/<doc_type>/titles/<title>/documents/<document>/versions")
def _get_versions(region, doc_type, title, document):
    app.logger.debug('get list of titles for doc_type: {}'.format(doc_type))
    handler = app.handlers.handler(region, doc_type) 
    versions = handler.get_versions(title, document)
    return versions

@document_api.route("/<region>/docs/<doc_type>/titles/<title>/documents/<document>/versions/<version>/objects")
def _get_objects(region, doc_type, title, document, version):
    app.logger.debug('get list of titles for doc_type: {}'.format(doc_type))
    handler = app.handlers.handler(region, doc_type) 
    _objects = handler.get_objects(title, document, version)
    return _objects

@document_api.route("/<region>/docs/<doc_type>/titles/<title>/documents/<document>/versions/<version>/objects/<object_no>")
def _get_object(region, doc_type, title, document, version, object_no):
    app.logger.debug('get object for : {} {} {} {}'.format(doc_type, document, version, object_no))
    handler = app.handlers.handler(region, doc_type) 
    _object = handler.get_object(title, document, version, object_no)
    return _object




@document_api.route("/<region>/docs/<doc_type>/titles/<title>/documents/<document>/versions/<version>/objects/<object_no>/_uuid", methods=['PUT'] )
def _set_uuid(region, doc_type, title, document, version, object_no):
    app.logger.debug('set uuid for : {} {} {} {}'.format(doc_type, document, version, object_no))
    handler = app.handlers.handler(region, doc_type) 
    titles = handler.set_uuid(title, document, version, object_no)
    return titles


@document_api.route("/<region>/docs/<doc_type>/uuids/<uuid>/meta", methods=['PUT'] )
def _put_meta(region, doc_type, uuid):
    app.logger.debug('set metadata for : {} {}'.format(doc_type, uuid))
    handler = app.handlers.handler(region, doc_type) 
    metadata = request.json   
    results = handler.set_meta(uuid, metadata)
    return results

@document_api.route("/<region>/docs/<doc_type>/uuids/<uuid>/meta", methods=['GET'] )
def _get_meta(region, doc_type, uuid):
    app.logger.debug('set metadata for : {} {}'.format(doc_type, uuid))
    handler = app.handlers.handler(region, doc_type) 
    metadata = request.json   
    results = handler.get_meta(uuid)
    return results



@document_api.route("/<region>/docs/<doc_type>/objects")
def _get_objects_in_state(region, doc_type):
    state = request.args.get("state","new")
    size = request.args.get("size","1")
    app.logger.debug('get list of {} {} objects in state: {}'.format(size, doc_type, state))
    handler = app.handlers.handler(region, doc_type) 
    titles = handler.get_objects_in_state(state, size)
    return titles