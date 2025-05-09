import os
import sys
from main import app as application

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# This is the WSGI application object for Gunicorn
# 'application' is the default variable name that Gunicorn looks for
app = application