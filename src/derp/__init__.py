import os
import psycopg2
from picklesession import PickleSessionInterface
from flask_github import GitHub
from flask import Flask, render_template, request, redirect, url_for, session, flash

# globals
app = Flask(__name__)  # instantiate the app here so it can be run as a module
app.secret_key = str(app.config['APP_SECRET_KEY'])

app.config.from_pyfile('CONFIG.py')

path = '/dev/shm/derp_sessions'
if not os.path.exists(path):
    os.mkdir(path)
    os.chmod(path, int('700', 8))

app.session_interface = PickleSessionInterface(path)

github = GitHub(app)
conn = psycopg2.connect(app.config['DB_LOCATION'])
cur = conn.cursor()
