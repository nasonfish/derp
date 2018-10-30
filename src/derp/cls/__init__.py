from flask import Blueprint

cls = Blueprint("class", __name__, template_folder="templates", static_folder="static")

import derp.cls.views
