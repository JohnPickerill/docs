import os
import json
import datetime

# RULES OF CONFIG:
# 1. No region specific code. Regions are defined by setting the OS environment variables appropriately to build up the
# desired behaviour.
# 2. No use of defaults when getting OS environment variables. They must all be set to the required values prior to the
# app starting.
# 3. This is the only file in the app where os.environ should be used.

# For the enhanced logging extension
FLASK_LOG_LEVEL = os.environ['LOG_LEVEL']
LOG_LEVEL = os.environ['LOG_LEVEL']

# DEBUG
DEBUG = (os.getenv("DEBUG") == "True")
ASSETS_DEBUG = (os.getenv("ASSETS_DEBUG") == "True")
LOG_DEBUG_FORMAT = (os.getenv("LOG_DEBUG_FORMAT") == "True")
# For health route
COMMIT = os.environ['COMMIT']

# This APP_NAME variable is to allow changing the app name when the app is running in a cluster. So that
# each app in the cluster will have a unique name.
APP_NAME = os.environ['APP_NAME']
MAX_HEALTH_CASCADE = int(os.environ['MAX_HEALTH_CASCADE'])
DEFAULT_TIMEOUT = int(os.environ['DEFAULT_TIMEOUT'])

# CORS and CSRF stuff
if os.getenv("RESOURCES"):
        res = os.environ["RESOURCES"]
        try:
            RESOURCES = json.loads(res)
        except:
            # TODO how do we log a message here ?
            try:
                del RESOURCES
            except:
                pass
WTF_CSRF_ENABLED = (os.getenv("WTF_CSRF_ENABLED") == 'True')
SECRET_KEY = os.environ["SECRET_KEY"]
APP_SECRET_KEY = os.environ["SECRET_KEY"]

if os.getenv('PERMANENT_SESSION_LIFETIME'):
    minutes = os.environ['PERMANENT_SESSION_LIFETIME']
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=minutes)
else:
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=240)


# ADAPTOR access
REGIONS = os.environ['REGIONS'].split(',')
print(REGIONS)
for region in REGIONS:
    globals()[region + '_ADAPTOR_KEY'] = os.environ[region + '_ADAPTOR_KEY']
    globals()[region + '_ADAPTOR_URL'] = os.environ[region + '_ADAPTOR_URL']

# Service Access
OBJ_API_URL =  os.environ['OBJ_API_URL'] 
DOCS_API_URL = os.environ['DOCS_API_URL'] 

# Security
IGNORE_CERT_WARNINGS = (os.getenv('IGNORE_CERT_WARNINGS') == 'True')

# Following is an example of building the dependency structure used by the cascade route
# SELF can be used to demonstrate how it works (i.e. it will call it's own casecade
# route until MAX_HEALTH_CASCADE is hit)
# SELF = "http://localhost:8080"
# DEPENDENCIES = {"SELF": SELF}

# Using SQLAlchemy/Postgres?
# The required variables (and required usage) can be found here:
# http://git.dev.ctp.local/gadgets/gadget-api/blob/master/gadget_api/config.py


 