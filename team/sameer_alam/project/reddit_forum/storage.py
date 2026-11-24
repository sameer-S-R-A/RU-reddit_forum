"""Django storage adapter that sends post images to the InsForge media bucket."""
import os
from pathlib import PurePosixPath
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from .insforge import get_insforge, InsForgeError


@deconstructible
class InsForgeMediaStorage(Storage):
    bucket_name = "reddit-post-media"

    def _open(self, name, mode="rb"):
        raise NotImplementedError("InsForge media is served by URL, not opened locally.")

    def _save(self, name, content):
        client = get_insforge()
        if not client.configured:
            raise InsForgeError("InsForge media storage is not configured.")
        key = str(PurePosixPath(name))
        strategy = client._request("POST", f"/api/storage/buckets/{self.bucket_name}/upload-strategy", json={
            "filename": key,
            "contentType": getattr(content, "content_type", "application/octet-stream"),
            "size": content.size,
        })
        upload_url = strategy["uploadUrl"]
        if upload_url.startswith("/"):
            upload_url = f"{client.base_url}{upload_url}"
        if strategy["method"] == "presigned":
            data = strategy.get("fields", {})
            response = __import__("requests").post(upload_url, data=data, files={"file": (key, content, getattr(content, "content_type", None))}, timeout=30)
        else:
            response = __import__("requests").put(upload_url, files={"file": (key, content, getattr(content, "content_type", None))}, headers={"Authorization": f"Bearer {client.api_key}"}, timeout=30)
        if response.status_code >= 400:
            raise InsForgeError("Image upload to InsForge failed.")
        if strategy.get("confirmRequired"):
            confirm_url = strategy["confirmUrl"]
            if confirm_url.startswith("/"):
                confirm_url = f"{client.base_url}{confirm_url}"
            confirm = __import__("requests").post(confirm_url, headers=client._headers(), json={"size": content.size, "contentType": getattr(content, "content_type", None)}, timeout=15)
            if confirm.status_code >= 400:
                raise InsForgeError("InsForge could not confirm the image upload.")
        return key

    def exists(self, name):
        return False

    def url(self, name):
        return f"{os.environ.get('INSFORGE_BASE_URL', '').rstrip('/')}/api/storage/buckets/{self.bucket_name}/objects/{name}"
