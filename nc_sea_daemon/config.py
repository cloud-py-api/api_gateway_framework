"""
Configuration related stuff lives here
"""

from json import dump, load
from os import mkdir, path, scandir


class Config:
    config_name = "daemon_cfg.json"
    apps_folder = "apps"

    def __init__(self):
        self.apps = {}
        self.options = {}
        # if there is no `apps` folder, create it
        if not path.isdir(self.apps_folder):
            mkdir(self.apps_folder)
        # if there is no config file, create minimal file with default values
        if not path.isfile(self.config_name):
            self.load_default_values()
        # load config
        with open(self.config_name, "r", encoding="utf8") as fp:
            cfg = load(fp)
            self.apps = cfg["apps"]
            self.options = cfg["options"]
        self.check_config()
        # rescan apps folder, some of them can be installed manually by admin
        for obj in scandir(self.apps_folder):
            if obj.is_dir():
                self.apps[obj.name] = {}

    def load_default_values(self):
        self.options["log_level"] = "WARN"
        self.options["host"] = "127.0.0.1"
        self.options["port"] = 8063
        self.options["xauth"] = "nextcloud:"
        self.options["nc_url"] = ""  # url should be full, with "index.php" if no `pretty_url` is installed.
        self.save()

    def check_config(self):
        for k in ("log_level", "host", "port", "xauth"):
            if k not in self.options:
                raise ValueError(f"Can not find `{k}` key in {self.config_name}")

    def save(self):
        with open(self.config_name, "w", encoding="utf8") as fp:
            cfg = {"apps": self.apps, "options": self.options}
            dump(cfg, fp, indent=4)
