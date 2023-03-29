from typing import Optional

from .connections import Connection

ENDPOINT_BASE = "/ocs/v1.php/cloud"
ENDPOINT = f"{ENDPOINT_BASE}/users"


class UserAPI:
    def __init__(self, connection: Connection):
        self.connection = connection

    def list_users(self, mask: Optional[str] = "", limit: Optional[int] = None, offset: Optional[int] = None) -> dict:
        data = {}
        if mask is not None:
            data["search"] = mask
        if limit is not None:
            data["limit"] = limit
        if offset is not None:
            data["offset"] = offset
        response_data = self.connection.request(method="GET", path=ENDPOINT, data=data)
        return response_data["users"] if response_data else {}

    def get_user(self, user_id: str) -> dict:
        return self.connection.request(method="GET", path=f"{ENDPOINT}/{user_id}")

    def create_user(self, user_id: str, **kwargs) -> dict:
        password = kwargs.get("password", None)
        email = kwargs.get("email", None)
        if password is None and email is None:
            raise ValueError("Either password or email must be set")
        data = {"userid": user_id}
        for k in ("password", "displayname", "email", "groups", "subadmin", "quota", "language"):
            if k in kwargs:
                data[k] = kwargs[k]
        return self.connection.request(method="POST", path=ENDPOINT, data=data)

    def delete_user(self, user_id: str) -> dict:
        return self.connection.request(method="DELETE", path=f"{ENDPOINT}/{user_id}")

    def enable_user(self, user_id: str) -> dict:
        return self.connection.request(method="PUT", path=f"{ENDPOINT}/{user_id}/enable")

    def disable_user(self, user_id: str) -> dict:
        return self.connection.request(method="PUT", path=f"{ENDPOINT}/{user_id}/disable")

    def resend_welcome_email(self) -> dict:
        return self.connection.request(method="POST", path=f"{ENDPOINT}/user/welcome")

    def editable_fields(self) -> dict:
        return self.connection.request(method="GET", path=f"{ENDPOINT_BASE}/user/fields")

    def edit_user(self, user_id: str, **kwargs) -> dict:
        return self.connection.request(method="PUT", path=f"{ENDPOINT}/{user_id}", data={**kwargs})

    def add_user_to_group(self, user_id: str, group_id: str) -> dict:
        return self.connection.request(method="POST", path=f"{ENDPOINT}/{user_id}/groups", data={"groupid": group_id})

    def remove_user_from_group(self, user_id: str, group_id: str) -> dict:
        return self.connection.request(method="DELETE", path=f"{ENDPOINT}/{user_id}/groups", data={"groupid": group_id})

    def promote_user_to_subadmin(self, user_id: str, group_id: str) -> dict:
        return self.connection.request(
            method="POST", path=f"{ENDPOINT}/{user_id}/subadmins", data={"groupid": group_id}
        )

    def demote_user_from_subadmin(self, user_id: str, group_id: str) -> dict:
        return self.connection.request(
            method="DELETE", path=f"{ENDPOINT}/{user_id}/subadmins", data={"groupid": group_id}
        )
