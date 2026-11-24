"""Small server-side client used to mirror the Django forum into InsForge."""
import os
import uuid
from urllib.parse import quote
import requests


class InsForgeError(Exception):
    pass


class AccountAlreadyExists(InsForgeError):
    pass


class InsForgeClient:
    def __init__(self, token=None):
        self.base_url = os.environ.get("INSFORGE_BASE_URL", "").rstrip("/")
        self.api_key = os.environ.get("INSFORGE_API_KEY", "")
        self.enabled = os.environ.get("INSFORGE_ENABLED", "false").lower() == "true"
        self.token = token or self.api_key

    @property
    def configured(self):
        return self.enabled and bool(self.base_url and self.api_key)

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def _request(self, method, path, **kwargs):
        if not self.configured:
            return None
        headers = kwargs.pop("headers", self._headers())
        try:
            response = requests.request(method, f"{self.base_url}{path}", headers=headers, timeout=15, **kwargs)
        except requests.RequestException as error:
            raise InsForgeError("InsForge is temporarily unavailable.") from error
        if response.status_code >= 400:
            raise InsForgeError(response.text[:500])
        return response.json() if response.content else None

    def upsert(self, table, payload):
        return self._request("POST", f"/api/database/records/{table}", json=[payload], headers={**self._headers(), "Prefer": "resolution=merge-duplicates,return=representation"})

    def delete(self, table, filters):
        query = "&".join(f"{quote(str(key))}=eq.{quote(str(value))}" for key, value in filters.items())
        return self._request("DELETE", f"/api/database/records/{table}?{query}")

    def select(self, table, filters=None, order=None):
        parts = []
        for key, value in (filters or {}).items():
            parts.append(f"{quote(str(key))}=eq.{quote(str(value))}")
        parts.append(f"order={quote((order + ',' if order else '') + 'id.asc')}")
        page_size = 100
        parts.append(f"limit={page_size}")
        path = f"/api/database/records/{table}?" + "&".join(parts)
        rows = []
        try:
            while True:
                batch = self._request("GET", f"{path}&offset={len(rows)}") or []
                rows.extend(batch)
                if len(batch) < page_size:
                    return rows
        except InsForgeError:
            return []

    def insert(self, table, payload):
        response = self._request("POST", f"/api/database/records/{table}", json=[payload], headers={**self._headers(), "Prefer": "return=representation"})
        return (response or [None])[0]

    def update(self, table, record_id, payload):
        response = self._request("PATCH", f"/api/database/records/{table}?id=eq.{quote(str(record_id))}", json=payload, headers={**self._headers(), "Prefer": "return=representation"})
        return (response or [None])[0]

    def upload_media(self, uploaded_file, user_id):
        key = f"{user_id}/{uuid.uuid4().hex}-{uploaded_file.name}"
        strategy = self._request("POST", "/api/storage/buckets/reddit-post-media/upload-strategy", json={"filename": key, "contentType": uploaded_file.content_type, "size": uploaded_file.size})
        url = strategy["uploadUrl"]
        if url.startswith("/"):
            url = self.base_url + url
        if strategy["method"] == "presigned":
            response = requests.post(url, data=strategy.get("fields", {}), files={"file": (uploaded_file.name, uploaded_file, uploaded_file.content_type)}, timeout=30)
        else:
            response = requests.put(url, headers={"Authorization": f"Bearer {self.token}"}, files={"file": (uploaded_file.name, uploaded_file, uploaded_file.content_type)}, timeout=30)
        if response.status_code >= 400:
            raise InsForgeError("Media upload failed.")
        return f"{self.base_url}/api/storage/buckets/reddit-post-media/objects/{key}"

    def register_user(self, email, password, username):
        if not self.configured:
            raise InsForgeError("Registration is unavailable until InsForge is configured.")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/users?client_type=server",
                json={"email": email, "password": password, "name": username},
                headers=self._headers(),
                timeout=20,
            )
        except requests.RequestException as error:
            raise InsForgeError("InsForge could not be reached. Please try again.") from error
        if response.status_code == 409:
            raise AccountAlreadyExists("This email already has an account.")
        if response.status_code == 429:
            raise InsForgeError("Too many registration attempts. Please try again later.")
        if not response.ok:
            raise InsForgeError("InsForge could not complete registration. Please try again later.")
        return response.json()

    def login_user(self, email, password):
        if not self.configured:
            raise InsForgeError("Login is unavailable until the forum’s InsForge connection is configured.")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/sessions?client_type=server",
                json={"method": "password", "email": email, "password": password},
                headers=self._headers(),
                timeout=20,
            )
        except requests.RequestException as error:
            raise InsForgeError("InsForge could not be reached. Please try again.") from error
        if response.status_code in (400, 401, 403):
            raise InsForgeError("Sign-in failed. Check your email and password and try again.")
        if response.status_code == 429:
            raise InsForgeError("Too many sign-in attempts. Please try again later.")
        if not response.ok:
            raise InsForgeError("InsForge could not complete sign-in. Please try again later.")
        return response.json()


def get_insforge(token=None):
    return InsForgeClient(token)
