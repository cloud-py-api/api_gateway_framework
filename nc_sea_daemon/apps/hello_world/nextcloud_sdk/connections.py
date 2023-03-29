from dataclasses import dataclass
from json import dumps, loads
from os import environ
from typing import Optional, Union
from urllib.parse import urlencode

import xmltodict
from httpx import Client, Limits, ReadTimeout

from . import exceptions


@dataclass
class ConnectConfig:
    def __init__(self, **kwargs):
        self.full_nc_url: str = self._get_value("nextcloud_url", **kwargs)
        self.endpoint = self.full_nc_url.removesuffix("/index.php")
        self.auth = (self._get_value("nc_auth_user", **kwargs), self._get_value("nc_auth_pass", **kwargs))

    def _get_value(self, value_name, **kwargs):
        value = kwargs.get(value_name, None)
        if not value:
            value = environ.get(value_name, None)
        if not value:
            raise ValueError(f"`{value_name}` is not found.")
        return value


class Connection:
    def __init__(self, **kwargs):
        self.adapter: Union[Client, None] = None
        self.config = ConnectConfig(**kwargs)

    def __del__(self):
        self.close()

    def request(self, method: str, path: str, data: Optional[dict] = None):
        if data is None:
            data = {}
        self.__request_prepare()
        method = method.upper()
        data.update({"format": "json"})
        try:
            if method == "GET":
                response = self.adapter.get(f"{self.config.endpoint}{path}?{urlencode(data, True)}")
            else:
                response = self.adapter.request(method, f"{self.config.endpoint}{path}", data=data)
        except ReadTimeout:
            raise exceptions.NextcloudRequestTimeout() from None

        if response.status_code == 400:
            raise exceptions.NextcloudBadRequest()
        if response.status_code == 401:
            raise exceptions.NextcloudUnauthorized()
        elif response.status_code == 403:
            raise exceptions.NextcloudForbidden()
        elif response.status_code == 404:
            raise exceptions.NextcloudNotFound()
        elif response.status_code == 405:
            raise exceptions.NextcloudMethodNotAllowed()

        if not response.text:
            return None
        response_data = loads(response.text)
        ocs_meta = response_data["ocs"]["meta"]
        if ocs_meta["status"] != "ok":
            raise exceptions.NextcloudException(status_code=ocs_meta["statuscode"], reason=ocs_meta["message"])
        return response_data["ocs"]["data"]

    def dav_request(self, method: str, path: str, data: Optional[str] = None):
        self.__request_prepare()
        response = self.adapter.request(method, f"{self.config.endpoint}{path}", data=data)
        if not response.content:
            return None
        response_data = loads(dumps(xmltodict.parse(response.content)))
        if "d:error" in response_data:
            # here need adjustments!
            err = response_data["d:error"]
            raise exceptions.NextcloudException(f'{err["s:exception"]}: {err["s:message"]}'.replace("\n", ""))
        return response_data["d:multistatus"]["d:response"]

    def close(self):
        if self.adapter:
            self.adapter.close()
            self.adapter = None

    def __request_prepare(self) -> None:
        if not self.adapter:
            limits = Limits(max_keepalive_connections=20, max_connections=20, keepalive_expiry=15.0)
            self.adapter = Client(auth=self.config.auth, follow_redirects=True, limits=limits, verify=False)
            self.adapter.headers.update({"OCS-APIRequest": "true"})
