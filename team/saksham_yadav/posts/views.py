from django.shortcuts import redirect, render
from .forms import PostForm
from sameer_alam.project.reddit_forum.insforge import get_insforge
from sameer_alam.project.reddit_forum.views import decorate_posts

def login_required(view):
    def wrapped(request, *args, **kwargs): return view(request, *args, **kwargs) if request.user.is_authenticated else redirect("accounts:login")
    return wrapped


def post_list(request):
    client = get_insforge(request.session.get("auth_token"))
    posts = client.select("reddit_posts", order="created_at.desc")
    query = request.GET.get("q", "").strip()
    if query:
        posts = [post for post in posts if query.lower() in (post.get("title", "") + post.get("body", "")).lower()]
    return render(request, "posts/list.html", {"posts": decorate_posts(client, posts), "query": query})


def post_detail(request, post_id):
    client = get_insforge(request.session.get("auth_token"))
    rows = client.select("reddit_posts", {"id": post_id})
    if not rows: return redirect("posts:list")
    post = decorate_posts(client, rows)[0]
    profiles = {str(p["insforge_user_id"]): p.get("username", "member") for p in client.select("reddit_profiles")}
    comments = client.select("reddit_comments", {"post_id": post_id}, "created_at.asc")
    for comment in comments: comment["author_username"] = profiles.get(str(comment.get("author_id")), "member")
    return render(request, "posts/detail.html", {"post": post, "comments": comments})


@login_required
def post_create(request):
    client = get_insforge(request.session["auth_token"])
    communities = [item for item in client.select("reddit_communities") if request.user.id in item.get("member_ids", [])]
    form = PostForm(request.POST or None, request.FILES or None, communities=communities)
    if request.method == "POST" and form.is_valid():
        media_urls = [client.upload_media(form.cleaned_data["image"], request.user.id)] if form.cleaned_data.get("image") else []
        post = client.insert("reddit_posts", {"community_id": form.cleaned_data["community"], "author_id": request.user.id, "author_username": request.user.username, "post_type": form.cleaned_data["post_type"], "title": form.cleaned_data["title"], "body": form.cleaned_data["body"], "link_url": form.cleaned_data["link_url"] or "", "media_urls": media_urls})
        return redirect("posts:detail", post_id=post["id"])
    return render(request, "posts/create.html", {"form": form})
