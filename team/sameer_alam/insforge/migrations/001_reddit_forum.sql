-- Apply this in the InsForge SQL editor after the project connection is loaded.
-- Django migrations are the authoritative schema for the Django deployment.
-- This companion schema documents the domain tables to protect forum data with RLS.

create table if not exists communities (
  id bigint generated always as identity primary key,
  name varchar(64) not null unique,
  slug varchar(80) not null unique,
  description varchar(500) not null,
  owner_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

create table if not exists community_members (
  community_id bigint not null references communities(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  primary key (community_id, user_id)
);

create table if not exists posts (
  id bigint generated always as identity primary key,
  community_id bigint not null references communities(id) on delete cascade,
  author_id uuid not null references auth.users(id) on delete cascade,
  post_type varchar(10) not null check (post_type in ('text', 'link', 'image')),
  title varchar(300) not null,
  body text not null default '',
  link_url text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists post_media (
  id bigint generated always as identity primary key,
  post_id bigint not null references posts(id) on delete cascade,
  storage_key text not null unique,
  created_at timestamptz not null default now()
);

create table if not exists comments (
  id bigint generated always as identity primary key,
  post_id bigint not null references posts(id) on delete cascade,
  author_id uuid not null references auth.users(id) on delete cascade,
  body text not null check (char_length(body) between 1 and 4000),
  created_at timestamptz not null default now()
);

create table if not exists votes (
  post_id bigint not null references posts(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  value smallint not null check (value in (-1, 1)),
  created_at timestamptz not null default now(),
  primary key (post_id, user_id)
);

create table if not exists conversations (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists conversation_members (
  conversation_id bigint not null references conversations(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  primary key (conversation_id, user_id)
);

create table if not exists direct_messages (
  id bigint generated always as identity primary key,
  conversation_id bigint not null references conversations(id) on delete cascade,
  sender_id uuid not null references auth.users(id) on delete cascade,
  body text not null check (char_length(body) between 1 and 4000),
  created_at timestamptz not null default now()
);

alter table communities enable row level security;
alter table community_members enable row level security;
alter table posts enable row level security;
alter table post_media enable row level security;
alter table comments enable row level security;
alter table votes enable row level security;
alter table conversations enable row level security;
alter table conversation_members enable row level security;
alter table direct_messages enable row level security;

create policy "public forum read" on communities for select using (true);
create policy "public posts read" on posts for select using (true);
create policy "public media read" on post_media for select using (true);
create policy "public comments read" on comments for select using (true);
create policy "public votes read" on votes for select using (true);
create policy "authenticated people create communities" on communities for insert to authenticated with check (owner_id = auth.uid());
create policy "authors create posts" on posts for insert to authenticated with check (author_id = auth.uid());
create policy "authors create comments" on comments for insert to authenticated with check (author_id = auth.uid());
create policy "people control their vote" on votes for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
