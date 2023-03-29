from typing import Optional

from .connections import Connection

ENDPOINT_BASE = "/ocs/v1.php/cloud"
ENDPOINT = f"{ENDPOINT_BASE}/groups"


class UsersGroupsAPI:
    def __init__(self, connection: Connection):
        self.connection = connection

    def list_groups(self, mask: Optional[str] = "", limit: Optional[int] = None, offset: Optional[int] = None) -> dict:
        data = {}
        if mask is not None:
            data["search"] = mask
        if limit is not None:
            data["limit"] = limit
        if offset is not None:
            data["offset"] = offset
        response_data = self.connection.request(method="GET", path=ENDPOINT, data=data)
        return response_data["groups"] if response_data else {}

    def create_group(self, group_id: str) -> dict:
        return self.connection.request(method="POST", path=f"{ENDPOINT}", data={"groupid": group_id})

    def get_members_of_group(self, group_id: str) -> dict:
        response_data = self.connection.request(method="GET", path=f"{ENDPOINT}/{group_id}")
        return response_data["users"] if response_data else {}

    def get_subadmins_of_group(self, group_id: str) -> dict:
        return self.connection.request(method="GET", path=f"{ENDPOINT}/{group_id}/subadmins")

    def edit_group(self, group_id: str, **kwargs) -> dict:
        return self.connection.request(method="PUT", path=f"{ENDPOINT}/{group_id}", data={**kwargs})

    def delete_group(self, group_id: str) -> dict:
        return self.connection.request(method="DELETE", path=f"{ENDPOINT}/{group_id}")
