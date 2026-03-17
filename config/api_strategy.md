# API Strategy

## Recommended yes

- U.S. Census API: yes, for Arkansas demographics, county comparisons, race, age, income, education, rural/urban splits.
- BLS API: yes, for labor force, unemployment, industry trends, and wage context.
- Google Civics API: useful, but secondary. Best for elected officials lookup and district info.
- Google Maps API: optional. Use only when you need mapping, event geocoding, or interactive location-based storytelling.

## Architecture recommendation

Use PostgreSQL as the system of record.

APIs should hydrate your database, not drive the site live on every request.

Why:
- better speed
- lower API fragility
- historical snapshots
- easier citations and reproducibility
- lets you attach stories, chapters, and simulations to real data

## Suggested core tables

- stories
- story_tags
- chapters
- chapter_segments
- courses
- lessons
- simulations
- civic_frameworks
- counties
- county_demographics
- labor_series
- ballot_measures
- organizing_events
- source_citations
- readers_progress
