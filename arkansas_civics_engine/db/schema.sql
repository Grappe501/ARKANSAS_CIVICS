CREATE TABLE IF NOT EXISTS courses (
  id SERIAL PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  description TEXT
);

CREATE TABLE IF NOT EXISTS chapters (
  id SERIAL PRIMARY KEY,
  course_slug TEXT NOT NULL,
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  UNIQUE(course_slug, slug)
);

CREATE TABLE IF NOT EXISTS segments (
  id SERIAL PRIMARY KEY,
  course_slug TEXT NOT NULL,
  chapter_slug TEXT NOT NULL,
  segment_slug TEXT NOT NULL,
  segment_order INT NOT NULL,
  title TEXT NOT NULL,
  body_md TEXT,
  metadata JSONB,
  UNIQUE(course_slug, chapter_slug, segment_slug)
);

CREATE TABLE IF NOT EXISTS sources (
  id SERIAL PRIMARY KEY,
  source_key TEXT UNIQUE NOT NULL,
  title TEXT,
  url TEXT,
  citation_text TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS stories (
  id SERIAL PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  county TEXT,
  tags TEXT[],
  body_md TEXT,
  metadata JSONB
);
