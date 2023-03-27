"""
EntryPoint of the daemon.
"""

import logging as log
from json import load, loads
from os import environ, path, chdir
from secrets import compare_digest
from shutil import rmtree
from subprocess import Popen
from typing import Dict, List

import uvicorn
from config import Config
from fastapi import Depends, FastAPI, File, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated

APP = FastAPI()
SECURITY = HTTPBasic()

CFG = Config()
LOG = log.getLogger()
APPS_STATUS: Dict[str, List[Popen]] = {}


_nameToLevel = {
    'FATAL': 50,
    'ERROR': 40,
    'WARN': 30,
    'INFO': 20,
    'DEBUG': 10,
}


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
    app_status: Dict[str, list] = {}
    for app_name, app_stats in APPS_STATUS.items():
        app_status[app_name] = []
        for popen in app_stats:
            app_run_info = {
                "pid": popen.pid,
                "alive": bool(popen.poll() is None),
                "args": popen.args,
            }
            app_status[app_name].append(app_run_info)
    json_data = jsonable_encoder({"apps": CFG.apps, "apps_status": app_status, "options": CFG.options})
    return JSONResponse(json_data)


@APP.post("/update")
def daemon_update(_username: Annotated[str, Depends(current_username)], version_tag: str):
    _ = version_tag
    # download
    # run updater
    # exit
    return JSONResponse({"status": "ok", "error": ""})


@APP.post("/app-install")
def app_install(_username: Annotated[str, Depends(current_username)], app_name: str, data: bytes = File()):
    _ = app_name
    _ = data
    return JSONResponse({"status": "ok", "error": ""})


@APP.post("/app-remove")
def app_remove(_username: Annotated[str, Depends(current_username)], app_name: str):
    app_runs_info = APPS_STATUS.pop(app_name, [])
    for app_run_info in app_runs_info:
        if app_run_info.poll() is None:
            app_run_info.kill()
    CFG.apps.pop("app_name", None)
    rmtree(f"apps/{app_name}")
    return JSONResponse({"status": "ok", "error": ""})


@APP.post("/app-run")
def app_run(_username: Annotated[str, Depends(current_username)], app_name: str, args: str = "[]"):
    app_cfg_daemon = CFG.apps.get(app_name, None)
    if app_cfg_daemon is None:
        return JSONResponse({"status": "fail", "error": "App with specified name does not found."})
    app_root_path = path.join("apps", app_name)
    try:
        with open(path.join(app_root_path, "appinfo.json"), "r", encoding="utf8") as fp:
            app_config = load(fp)
    except OSError:
        return JSONResponse({"status": "fail", "error": "Can not load app config file."})
    entry_point = app_config.get("entry_point", None)
    if entry_point is None:
        return JSONResponse({"status": "fail", "error": "`entrypoint` value missing from app config."})
    app_config_args: List = app_config.get("args", [])
    modified_env = environ.copy()
    modified_env.update(**app_cfg_daemon)
    try:
        app_args = loads(args)
    except Exception as e:  # noqa # pylint: disable=broad-except
        json_data = jsonable_encoder({"status": "fail", "error": "Arg parse error: " + str(e)})
        return JSONResponse(json_data)
    try:
        # pylint: disable=consider-using-with
        process = Popen([entry_point, *app_config_args, *app_args], env=modified_env, cwd=path.abspath(app_root_path))
        # pylint: enable=consider-using-with
    except OSError as e:
        json_data = jsonable_encoder({"status": "fail", "error": "Popen error: " + str(e)})
        return JSONResponse(json_data)
    if app_name not in APPS_STATUS:
        APPS_STATUS[app_name] = []
    APPS_STATUS[app_name].append(process)
    return JSONResponse({"status": "ok", "error": "", "pid": str(process.pid)})


@APP.post("/app-stop")
def app_stop(_username: Annotated[str, Depends(current_username)], app_pid: int):
    for app_run_infos in APPS_STATUS.values():
        for app_run_info in app_run_infos:
            if app_run_info.pid == app_pid:
                app_run_info.kill()
                return JSONResponse({"status": "ok", "error": ""})
    return JSONResponse({"status": "fail", "error": "app with provided pid was not found"})


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


if __name__ == "__main__":
    chdir(path.dirname(path.abspath(__file__)))
    print(f"http://{CFG.options['host']}:{CFG.options['port']}/status")  # For development
    log.basicConfig(format="%(levelname)s:%(name)s:%(module)s:%(funcName)s:%(message)s")
    log_level = _nameToLevel[CFG.options["log_level"]]
    LOG.setLevel(level=log_level)
    log.error("Logger initialized.")
    uvicorn.run(
        "daemon:APP",
        host=CFG.options["host"],
        port=CFG.options["port"],
        log_level=log_level,
    )
