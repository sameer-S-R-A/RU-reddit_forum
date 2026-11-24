"""Settings for the student Reddit-style community forum."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
TEAM_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(TEAM_ROOT))
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "change-this-before-deployment")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [host for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",") if host]

INSTALLED_APPS = ["django.contrib.messages", "django.contrib.staticfiles"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "reddit_forum.middleware.InsForgeSessionUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "reddit_forum.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            TEAM_ROOT / "kshitiz_kumar" / "accounts" / "templates",
            TEAM_ROOT / "aaditya_verma" / "communities" / "templates",
            TEAM_ROOT / "saksham_yadav" / "posts" / "templates",
            TEAM_ROOT / "aditya_kumar" / "messaging" / "templates",
        ],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "reddit_forum.middleware.forum_user",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "reddit_forum.wsgi.application"
ASGI_APPLICATION = "reddit_forum.asgi.application"

DATABASES = {"default": {"ENGINE": "django.db.backends.dummy"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
if os.environ.get("INSFORGE_ENABLED", "false").lower() == "true":
    STORAGES = {
        "default": {"BACKEND": "reddit_forum.storage.InsForgeMediaStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
