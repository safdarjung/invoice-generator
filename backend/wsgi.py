import os
import sys

# Add your project directory to the sys.path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Set the FLASK_APP environment variable (not strictly needed for FastAPI, but harmless)
os.environ['FLASK_APP'] = 'main'

# Import the FastAPI app for WSGI servers (PythonAnywhere looks for 'application')
from main import app as application
