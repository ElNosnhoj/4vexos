# ================================================================
# File: blueprint.py
# Desc: handle routes
# ================================================================
import flask

bp = flask.Blueprint("web", __name__)

# @bp.get("/")
# def index():
#     return flask.send_from_directory("/srv/fiv", "index.html")

# @bp.get("/<path:filename>")
# def static_files(filename):
#     return flask.send_from_directory("/srv/fiv", filename)




@bp.get("/")
def index():
    return flask.send_from_directory("/app/static", "index.html")

@bp.get("/<path:filename>")
def static_files(filename):
    return flask.send_from_directory("/app/static", filename)
