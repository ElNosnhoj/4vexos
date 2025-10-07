#================================================================
# File: app.py
# Desc: flask app
#================================================================
import os
import signal
import flask
from flask_cors import CORS
from datetime import datetime
import logging
from route import *
import argparse
from main import MAIN

#================================================================
# parse arguments
#================================================================
parser = argparse.ArgumentParser()
parser.add_argument("--host",       default='0.0.0.0')
parser.add_argument("--port",       default=3001)
args = parser.parse_args()

# host = '0.0.0.0'
# port = '8021'
host = args.host
port = int(args.port)

#================================================================
# setup
#================================================================
# disabling default logger
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# app setup
app = flask.Flask(__name__)
cors = CORS(
    app,
    origins="*",
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization"]
)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'ihaveabigone'


@app.get("/suicide")
def __suicide():
    print("SHINDERU")
    os.kill(os.getpid(),signal.SIGKILL)
    return "",200

#================================================================
# print traffic
#================================================================
@app.before_request
def __before_req(**kwargs):
    path:str = flask.request.path
    params = flask.request.args.to_dict()
    visitor = flask.request.headers.get("X-Real-IP")
    method = flask.request.method
    
    t = datetime.now().strftime("%H:%M:%S")
    print("[%s] %s//%s -- %s - %s" %(t, visitor, method ,path, params))
    if flask.request.method == "OPTIONS":
        res = flask.Response()
        res.headers['X-Content-Type-Options'] = '*'
        return res
    
    
    
#================================================================
# register blueprints or traffic
#================================================================
base = flask.Blueprint('base', __name__, url_prefix='/')
base.register_blueprint(config.bp, url_prefix="/config")
base.register_blueprint(web.bp, url_prefix="/")
app.register_blueprint(base)

#================================================================
# run time!
#================================================================
if __name__ == "__main__": 
    print("=========================================================================")
    print(f">> Server running at {host}:{port}")
    MAIN().run_thread()
    app.run(host=host, port=port, )
    
    
    