from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import LoginForm, RegisterForm
from sameer_alam.project.reddit_forum.insforge import AccountAlreadyExists, InsForgeError, get_insforge


def _session_login(request, remote, username):
    user = remote["user"]
    request.session["auth_token"] = remote["accessToken"]
    request.session["forum_user"] = {"id": user["id"], "email": user["email"], "username": username}


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            client = get_insforge()
            remote = client.register_user(form.cleaned_data["email"], form.cleaned_data["password1"], form.cleaned_data["username"])
        except AccountAlreadyExists:
            request.session["login_email"] = form.cleaned_data["email"]
            messages.info(request, "This email already has an account. Log in with your existing password.")
            return redirect("accounts:login")
        except InsForgeError as error:
            form.add_error(None, str(error))
            return render(request, "accounts/register.html", {"form": form})
        if remote.get("requireEmailVerification"):
            request.session["login_email"] = form.cleaned_data["email"]
            messages.info(request, "Check your email to verify your account before logging in.")
            return redirect("accounts:login")
        try:
            get_insforge(remote["accessToken"]).insert("reddit_profiles", {
                "insforge_user_id": remote["user"]["id"],
                "username": form.cleaned_data["username"],
                "email": form.cleaned_data["email"],
                "bio": "", "avatar_url": "",
            })
        except InsForgeError:
            request.session["login_email"] = form.cleaned_data["email"]
            messages.warning(request, "Your account was created, but the forum profile could not be saved. You can log in now.")
            return redirect("accounts:login")
        _session_login(request, remote, form.cleaned_data["username"])
        messages.success(request, "Welcome to Reddit!")
        return redirect("home")
    return render(request, "accounts/register.html", {"form": form})


def sign_in(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = LoginForm(request.POST or None, initial={"email": request.session.pop("login_email", "")})
    if request.method == "POST" and form.is_valid():
        try:
            remote = get_insforge().login_user(form.cleaned_data["email"], form.cleaned_data["password"])
            profiles = get_insforge(remote["accessToken"]).select("reddit_profiles", {"insforge_user_id": remote["user"]["id"]})
            username = profiles[0]["username"] if profiles else remote["user"]["email"].split("@")[0]
            _session_login(request, remote, username)
        except InsForgeError as error:
            form.add_error(None, str(error))
            return render(request, "accounts/login.html", {"form": form})
        return redirect("home")
    return render(request, "accounts/login.html", {"form": form})


def sign_out(request):
    request.session.flush()
    return redirect("home")
