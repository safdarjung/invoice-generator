import os
import sys

# Add your project directory to the sys.path
# Assuming your project structure is /home/your_username/invoice-generator/backend
path = '/home/safdar1/invoice-generator/backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the FLASK_APP environment variable (even for FastAPI, it's a common practice for WSGI)
os.environ['FLASK_APP'] = 'main' # Or 'main:app' if you prefer

from main import app as application # 'application' is the variable PythonAnywhere looks for