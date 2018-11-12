#!/usr/bin/env python3.4
from derp import app

from derp.course import course

# register the branding module as a blueprint
app.register_blueprint(course, url_prefix='/course')