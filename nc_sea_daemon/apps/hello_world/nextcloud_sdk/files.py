from io import BytesIO
from typing import Optional, TypedDict
from xml.etree import ElementTree

from .connections import Connection

ENDPOINT = "/remote.php/dav"


class NodeInfo(TypedDict):
    id: int
    is_dir: bool
    is_local: bool
    mimetype: int
    mimepart: int
    name: str
    internal_path: str
    abs_path: str
    size: int
    parent_id: int
    permissions: int
    mtime: int
    checksum: str
    encrypted: bool
    etag: str
    ownerName: str
    storageId: int
    mountId: int
    direct_access: bool


class FilesAPI:
    def __init__(self, connection: Connection):
        self.connection = connection

    def list_files(
        self, user: Optional[str] = None, path: Optional[str] = "", properties: Optional[list[str]] = None
    ) -> dict:
        if properties is None:
            properties = []
        root = ElementTree.Element(
            "d:propfind",
            attrib={"xmlns:d": "DAV:", "xmlns:oc": "http://owncloud.org/ns", "xmlns:nc": "http://nextcloud.org/ns"},
        )
        prop = ElementTree.SubElement(root, "d:prop")
        for i in properties:
            ElementTree.SubElement(prop, i)

        with BytesIO() as buffer:
            ElementTree.ElementTree(root).write(buffer, xml_declaration=True)
            buffer.seek(0)
            data = buffer.read().decode("utf-8")

        full_path = f"{ENDPOINT}/files"
        if user:
            full_path += "/" + user
        if path:
            full_path += "/" + path
        response = self.connection.dav_request("PROPFIND", full_path, data=data)
        result = {}
        fileid = 1234
        for i in response:
            obj_name: str = i.pop("d:href")
            obj_name = obj_name.replace(full_path, "").lstrip("/")
            if not obj_name:
                continue
            fileid += 1
            result[obj_name] = {"path": obj_name}
        return result
