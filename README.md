# Arkansas Civics

A modular content system for building:

- a book manuscript
- a Netlify web reader
- a 12-unit Articulate 360 course
- workshop derivatives
- future spawned course tracks

## Why this structure exists

The existing manuscript already centers the Arkansas Table as a repeatable civic practice — a table where every Arkansan has a seat, and where civic life becomes local, relational, and human again. fileciteturn4file0L1-L18 The later chapters also establish that the Arkansas Table is not a one-off event but a practice that can spread into schools, churches, town halls, workplaces, and coffee shops. fileciteturn4file7L1-L23

This repo turns that idea into infrastructure.

## Core apps

- `apps/web-reader`: public-facing book and course reader
- `apps/api`: data and content API
- `apps/admin`: optional admin/editor tooling
- `apps/course-player`: interactive course and simulation layer

## Main data model

The recommended long-term backend is PostgreSQL with content, stories, datasets, simulations, and cross-links stored relationally. Keep raw narrative in markdown, but index it in the database for search, tagging, citations, and reuse.

## First run

```bash
python scripts/scaffold_everything.py
```
