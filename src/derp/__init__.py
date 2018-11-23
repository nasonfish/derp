import os
import psycopg2
from flask_github import GitHub
from flask import Flask

from derp.picklesession import PickleSessionInterface

# globals
app = Flask(__name__)  # instantiate the app here so it can be run as a module

app.config.from_pyfile('CONFIG.py')

path = '/dev/shm/derp_sessions'
if not os.path.exists(path):
    os.mkdir(path)
    os.chmod(path, int('700', 8))

app.session_interface = PickleSessionInterface(path)

github = GitHub(app)
conn = psycopg2.connect(app.config['DB_LOCATION'])
cur = conn.cursor()

import derp.util

app.jinja_env.globals['breadcrumb'] = derp.util.breadcrumb

import derp.views
