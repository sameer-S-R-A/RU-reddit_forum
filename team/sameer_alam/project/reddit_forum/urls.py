from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/", include("kshitiz_kumar.accounts.urls")),
    path("communities/", include("aaditya_verma.communities.urls")),
    path("posts/", include("saksham_yadav.posts.urls")),
    path("social/", include("aditya_kumar.interactions.urls")),
    path("messages/", include("aditya_kumar.messaging.urls")),
]
