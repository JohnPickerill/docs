#!/usr/local/bin/python3

from flask import Flask

from cc_utils import load_config_yml


def make_app():
    # Configure flask
    # Create flask app
    app = Flask(__name__,
                template_folder='templates')
    load_config_yml(app)
    app.config.from_pyfile("config.py")
    return app

app = make_app()
 
@app.after_request
def after_request(response):
    # Add the API version (as in the interface spec, not the app) to the header. Semantic versioning applies - see the
    # API manual. A major version update will need to go in the URL. All changes should be documented though, for
    # reusing teams to take advantage of.
    response.headers["X-API-Version"] = "1.0.0"
    return response
