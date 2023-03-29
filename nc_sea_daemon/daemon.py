"""
EntryPoint of the daemon.
"""

import logging as log
import tarfile
from json import load, loads
from os import environ, makedirs, path, remove
from pathlib import Path
from secrets import compare_digest
from shutil import rmtree
from subprocess import Popen, run
from typing import Dict, List, Optional, Union

import requests

from config import Config
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated
from pydantic import BaseModel

APP = FastAPI()
SECURITY = HTTPBasic()

CFG = Config()
LOG = log.getLogger()
APPS_STATUS: Dict[str, List[Popen]] = {}


class AppRun(BaseModel):
    nc_url: str
    user_token: str
    app_name: str
    args: str = "[]"


class Option(BaseModel):
    key: str
    value: str
    app_name: Union[str, None] = None


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


def _load_app_config(app_name: str) -> Optional[dict]:
    app_root_path = path.join("apps", app_name)
    try:
        with open(path.join(app_root_path, "appinfo.json"), "r", encoding="utf8") as fp:
            app_config = load(fp)
    except OSError:
        return None
    return app_config


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
def app_install(_username: Annotated[str, Depends(current_username)], nc_url: str, user_token: str, app_name: str, package_url: str):
    # REWORK: this should be in a separate thread with notification to NC part when app install finished
    # Status: waiting: endpoint to send notify to, to be implemented by Andrey.
    _ = user_token
    _ = nc_url
    destination_path = path.join("apps", app_name)
    try:
        file_request = requests.get(package_url, allow_redirects=True)
        data = file_request.content
        with open(app_name + "_install_tmp.tar.gz", "wb") as fp:
            fp.write(data)
        archive_name = app_name + "_install_tmp.tar.gz"
        makedirs(destination_path, exist_ok=True)

        def members(tf):
            for member in tf.getmembers():
                stripped_path = Path(*Path(member.path).parts[1:])
                if stripped_path.name:
                    member.path = stripped_path
                    yield member

        with tarfile.open(archive_name, "r") as tar:
            tar.extractall(members=members(tar), path=destination_path)

        remove(archive_name)
        result = CFG.app_to_config(app_name)
        if not result:
            raise RuntimeError("Error during installing app.")
        app_config = _load_app_config(app_name)
        if app_config is None:
            return JSONResponse({"status": "fail", "error": "Can not load app config file."})
        setup_script = app_config.get("after_install", None)
        if setup_script:
            run(setup_script, cwd=path.abspath(f"apps/{app_name}"))
    except Exception as e:  # noqa
        rmtree(destination_path, ignore_errors=True)
        return JSONResponse({"status": "fail", "error": str(e)})
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
def app_run(_username: Annotated[str, Depends(current_username)], params: AppRun):
    app_cfg_daemon = CFG.apps.get(params.app_name, None)
    if app_cfg_daemon is None:
        return JSONResponse({"status": "fail", "error": "App with specified name does not found."})
    app_config = _load_app_config(params.app_name)
    if app_config is None:
        return JSONResponse({"status": "fail", "error": "Can not load app config file."})
    entry_point = app_config.get("entry_point", None)
    if entry_point is None:
        return JSONResponse({"status": "fail", "error": "`entrypoint` value missing from app config."})
    nc_auth = params.user_token.split(":", 1)
    if len(nc_auth) != 2:
        return JSONResponse({"status": "fail", "error": "`user_token` does not contain all required information."})
    app_config_args: List = app_config.get("args", [])
    modified_env = environ.copy()
    modified_env["nextcloud_url"] = params.nc_url
    modified_env["nc_auth_user"] = nc_auth[0]
    modified_env["nc_auth_pass"] = nc_auth[1]
    modified_env.update(**app_cfg_daemon)
    try:
        app_args = loads(params.args)
    except Exception as e:  # noqa # pylint: disable=broad-except
        json_data = jsonable_encoder({"status": "fail", "error": "Arg parse error: " + str(e)})
        return JSONResponse(json_data)
    try:
        cmd = [str(i) for i in [entry_point, *app_config_args, *app_args]]
        # pylint: disable=consider-using-with
        process = Popen(cmd, env=modified_env, cwd=path.abspath(f"apps/{params.app_name}"))
        # pylint: enable=consider-using-with
    except (OSError, TypeError) as e:
        json_data = jsonable_encoder({"status": "fail", "error": "Popen error: " + str(e)})
        return JSONResponse(json_data)
    if params.app_name not in APPS_STATUS:
        APPS_STATUS[params.app_name] = []
    APPS_STATUS[params.app_name].append(process)
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
def option_set(_username: Annotated[str, Depends(current_username)], option: Option):
    if option.app_name:
        app_config = CFG.apps.get(option.app_name, None)
        if app_config is None:
            return JSONResponse({"status": "fail", "error": f"app with name='{option.app_name}' not found"})
        app_config[option.key] = option.value
    else:
        CFG.options[option.key] = option.value
    CFG.save()
    return JSONResponse({"status": "ok", "error": ""})


@APP.on_event("startup")
def startup():
    print(f"http://{CFG.options['host']}:{CFG.options['port']}/status")  # For development
