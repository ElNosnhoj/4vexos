# ================================================================
# File: blueprint.py
# Desc: handle routes
# ================================================================
import flask
from lib.config.settings import ModuleMap, ModuleSettings
import json

bp = flask.Blueprint("config", __name__)

@bp.get("/hello")
def __hello():
    print("hello")
    return "", 200


@bp.get("/")
def __get_config():
    configs = ModuleSettings.get_keys()
    return json.dumps(configs), 200

# @bp.put("/")
# def __replace_config():
#     data:ModuleMap = flask.request.get_json() 
#     if not data:
#         return json.dumps({"error": "No data provided"}), 400

#     return json.dumps({"success": True, "received": data}), 200


@bp.put("/")
def __replace_config():
    data: ModuleMap = flask.request.get_json()
    if not data:
        return json.dumps({"error": "No data provided"}), 400

    # print("--DATA")
    # print(data)
    # print("--BEFORE")
    # print(ModuleSettings.get_keys())

    for key in list(ModuleSettings.get_keys().keys()):
        delattr(ModuleSettings, key)

    for k, v in data.items():
        ModuleSettings[k] = v

    try:
        ModuleSettings.save()
        # print("--AFTER")
        # print(ModuleSettings.get_keys())
    except ModuleSettings.WriteError:
        return json.dumps({"error": "Failed to write config"}), 500

    return json.dumps({"success": True, "received": data}), 200