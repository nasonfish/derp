from flask import Blueprint

course = Blueprint("course", __name__, template_folder="templates", static_folder="static")

import derp.course.views
