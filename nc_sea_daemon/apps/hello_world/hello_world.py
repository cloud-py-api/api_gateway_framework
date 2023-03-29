"""
Simplest example.
"""

import sys

from uvicorn import run
from fastapi.responses import Response
from fastapi import FastAPI

from nextcloud_sdk import Nextcloud


APP = FastAPI()
NC_CLIENT = Nextcloud()


@APP.get("/iframe")
def hello_world():
    return Response(f"Hello world! \nHere is the list of Nextcloud users:\n {NC_CLIENT.users.list_users()}")


if __name__ == "__main__":
    run(
        "hello_world:APP",
        host="127.0.0.1",
        port=8777,
        log_level=40,
    )
    sys.exit(0)
