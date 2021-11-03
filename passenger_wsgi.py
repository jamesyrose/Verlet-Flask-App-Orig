import imp
import os
import sys
from main import app as application
sys.path.insert(0, os.path.dirname(__file__))

wsgi = imp.load_source('wsgi', 'main.py')
#application = wsgi.web
