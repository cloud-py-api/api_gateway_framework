import logging as log
from os import chdir, path

import uvicorn

from config import Config

LOG = log.getLogger()

_nameToLevel = {
    "FATAL": 50,
    "ERROR": 40,
    "WARN": 30,
    "INFO": 20,
    "DEBUG": 10,
}


if __name__ == "__main__":
    chdir(path.dirname(path.abspath(__file__)))
    cfg = Config()
    log.basicConfig(format="%(levelname)s:%(name)s:%(module)s:%(funcName)s:%(message)s")
    log_level = _nameToLevel[cfg.options["log_level"]]
    LOG.setLevel(level=log_level)
    log.debug("Logger initialized.")
    uvicorn.run(
        "daemon:APP",
        host=cfg.options["host"],
        port=cfg.options["port"],
        log_level=log_level,
    )
