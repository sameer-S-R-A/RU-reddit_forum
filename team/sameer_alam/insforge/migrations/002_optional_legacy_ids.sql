alter table public.reddit_posts alter column community_local_id drop not null;
alter table public.reddit_comments alter column post_local_id drop not null;
alter table public.reddit_votes alter column post_local_id drop not null;
alter table public.reddit_messages alter column conversation_local_id drop not null;
