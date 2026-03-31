from app.services.disks.fnnas_client import FnNASClient
from app.services.disks.webdav_client import WebDAVClient


class DiskFactory:
    @staticmethod
    def create_disk_client(user):
        disk_config = user.get_disk_config()
        
        if user.disk_type == "fnnas":
            return FnNASClient(
                host=disk_config.get("host", ""),
                token=disk_config.get("token", "")
            )
        elif user.disk_type == "webdav":
            return WebDAVClient(
                host=disk_config.get("host", ""),
                username=disk_config.get("username", ""),
                password=disk_config.get("password", "")
            )
        else:
            return FnNASClient(
                host=disk_config.get("host", ""),
                token=disk_config.get("token", "")
            )
