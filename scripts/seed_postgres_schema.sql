-- Minimal first-pass schema
create table if not exists courses (
  id serial primary key,
  slug text unique not null,
  title text not null,
  course_number int,
  duration_minutes int,
  theme text
);

create table if not exists chapters (
  id serial primary key,
  course_id int references courses(id) on delete cascade,
  slug text not null,
  title text not null,
  chapter_number int,
  target_book_words int,
  target_course_minutes int
);

create table if not exists chapter_segments (
  id serial primary key,
  chapter_id int references chapters(id) on delete cascade,
  slug text not null,
  title text not null,
  body_md text,
  segment_order int,
  mode_book boolean default true,
  mode_web boolean default true,
  mode_articulate boolean default true,
  mode_workshop boolean default true
);

create table if not exists stories (
  id serial primary key,
  title text not null,
  summary text,
  county text,
  tags text[],
  body_md text,
  source_notes text
);
