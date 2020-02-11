# Import every blueprint file
from docs_documents_api.views import general, document_api, object_api

def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(general.general)
    app.register_blueprint(document_api.document_api)
    app.register_blueprint(object_api.object_api)
    
    # All done!
    app.logger.info("Blueprints registered")
