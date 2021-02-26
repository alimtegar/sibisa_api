# import imp
# import os
# import sys


# sys.path.insert(0, os.path.dirname(__file__))

# wsgi = imp.load_source('wsgi', 'passenger_wsgi.py')
# application = wsgi.application

from a2wsgi import ASGIMiddleware
from sql_app.main import app

application = ASGIMiddleware(app)
