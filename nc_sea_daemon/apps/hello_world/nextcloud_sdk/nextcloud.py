from .connections import Connection
from .files import FilesAPI
from .users import UserAPI
from .users_groups import UsersGroupsAPI


class Nextcloud:
    def __init__(self, **kwargs):
        self.connection = Connection(**kwargs)
        self.users = UserAPI(self.connection)
        self.users_groups = UsersGroupsAPI(self.connection)
        self.files = FilesAPI(self.connection)

    @property
    def connected(self) -> bool:
        return self.connection.adapter is not None
