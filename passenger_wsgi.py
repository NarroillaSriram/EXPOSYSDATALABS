import sys
import os

# Set the path to the virtual environment created by GoDaddy's Python app setup.
# The exact path depends on your cPanel username, app folder, and Python version.
# For now, we just add the current working directory to the system path.
sys.path.insert(0, os.path.dirname(__file__))

# Import your Flask app
# Assuming your main file is app.py and the Flask instance is named 'app'
from app import app as application
