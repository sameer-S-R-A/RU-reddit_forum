class ForumUser:
    def __init__(self, data=None):
        data = data or {}
        self.id = data.get("id")
        self.username = data.get("username", "")
        self.email = data.get("email", "")
        self.is_authenticated = bool(self.id)

    def __str__(self):
        return self.username or "Anonymous"


def forum_user(request):
    return {"user": request.user}


class InsForgeSessionUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = ForumUser(request.session.get("forum_user"))
        return self.get_response(request)
