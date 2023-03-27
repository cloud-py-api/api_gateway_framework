from queue import Queue
from json import dumps
import logging as log
from secrets import compare_digest

from fastapi import FastAPI, File, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing_extensions import Annotated
import uvicorn

from config import Config

APP = FastAPI()
SECURITY = HTTPBasic()

CFG = Config()
LOG = log.getLogger()
APPS_STATUS = {}


def current_username(credentials: Annotated[HTTPBasicCredentials, Depends(SECURITY)]):
    xauth = CFG.options["xauth"].split(":", 1)
    username_ok = compare_digest(credentials.username.encode("utf8"), xauth[0].encode("utf8"))
    if len(xauth) == 2:
        password_ok = compare_digest(credentials.password.encode("utf8"), xauth[1].encode("utf8"))
    else:
        password_ok = True
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@APP.get("/status")
def daemon_status(_username: Annotated[str, Depends(current_username)]):
    json_data = jsonable_encoder({"apps": CFG.apps, "apps_status": APPS_STATUS, "options": CFG.options})
    return JSONResponse(json_data)


@APP.post("/update")
def daemon_update(_username: Annotated[str, Depends(current_username)], version_tag: str):
    # download
    # run updater
    # exit
    return JSONResponse({"status": "ok", "error": ""})


@APP.post("/app-install")
def app_install(_username: Annotated[str, Depends(current_username)], app_name: str, data: bytes = File()):
    return JSONResponse({"status": "ok", "error": ""})


@APP.post("/app-remove")
def app_remove(_username: Annotated[str, Depends(current_username)], app_name: str):
    CFG.apps.pop("app_name", None)
    # in progress
    return JSONResponse({"status": "ok", "error": ""})


@APP.post("/app-run")
def app_run(_username: Annotated[str, Depends(current_username)], app_name: str, *args):
    return JSONResponse({"status": "ok", "error": ""})


@APP.post("/app-stop")
def app_stop(_username: Annotated[str, Depends(current_username)], app_task_id: int):
    return JSONResponse({"status": "ok", "error": ""})


@APP.get("/option")
def option_get(_username: Annotated[str, Depends(current_username)], key: str, app_name: str = ""):
    value = ""
    if app_name:
        app_config = CFG.apps.get(app_name, "")
        if app_config:
            value = app_config.get(key, "")
    else:
        value = CFG.options.get(key, "")
    return JSONResponse(jsonable_encoder(value))


@APP.post("/option")
def option_set(_username: Annotated[str, Depends(current_username)], key: str, value: str, app_name: str = ""):
    if app_name:
        app_config = CFG.apps.get(app_name, None)
        if app_config is None:
            return JSONResponse({"status": "fail", "error": f"app with name='{app_name}' not found"})
        app_config[key] = value
    else:
        CFG.options[key] = value
    CFG.save()
    return JSONResponse({"status": "ok", "error": ""})


if __name__ == '__main__':
    print(f"http://{CFG.options['host']}:{CFG.options['port']}/status")
    log.basicConfig(format="%(levelname)s:%(name)s:%(module)s:%(funcName)s:%(message)s")
    log_level = log._nameToLevel[CFG.options["log_level"]]  # noqa
    LOG.setLevel(level=log_level)
    log.error("Logger initialized.")
    uvicorn.run(
        "daemon:APP", host=CFG.options["host"], port=CFG.options["port"], log_level=log_level)
