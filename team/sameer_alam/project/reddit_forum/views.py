from collections import Counter

from django.core.paginator import Paginator
from django.shortcuts import render

from .insforge import get_insforge


def decorate_posts(client, posts, groups=None):
    if not posts:
        return posts
    if groups is None:
        groups = client.select("reddit_communities")
    communities = {group["id"]: group for group in groups}
    scores = Counter()
    for vote in client.select("reddit_votes"):
        scores[vote.get("post_id")] += vote["value"]
    counts = Counter(comment.get("post_id") for comment in client.select("reddit_comments"))
    for post in posts:
        group = communities.get(post.get("community_id"), {})
        post["community_name"] = group.get("name", "community")
        post["community_slug"] = group.get("slug")
        post["score"] = scores[post["id"]]
        post["comment_count"] = counts[post["id"]]
    return posts


def home(request):
    client = get_insforge(request.session.get("auth_token"))
    groups = client.select("reddit_communities", order="name.asc")
    posts = decorate_posts(client, client.select("reddit_posts", order="created_at.desc"), groups)
    sort = "top" if request.GET.get("sort") == "top" else "new"
    if sort == "top":
        posts.sort(key=lambda post: post["score"], reverse=True)
    page = Paginator(posts, 25).get_page(request.GET.get("page"))
    images = sorted((post for post in posts if post.get("media_urls")), key=lambda post: post["score"], reverse=True)
    return render(request, "forum/home.html", {
        "highlights": images[:3] if page.number == 1 and len(images) >= 2 else [],
        "sort": sort, "posts": page, "sidebar_groups": [group for group in groups if group.get("slug")][:6],
    })
