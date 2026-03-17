# Arkansas Civics Content Engine

This repository is the single-source content engine for the Arkansas Civics book, website, Articulate course, workbook, workshop series, and facilitator guide.

## Outputs
- Book manuscript
- Website reader JSON/Markdown
- Course outlines for Articulate / digital learning
- Participant workbook
- Live workshop guide
- Facilitator guide
- Source/citation registry

## Core idea
Write modular segments once, then compile them into multiple aligned learning products.

## Content hierarchy
- Course
  - Chapter
    - Segment

Each segment is a Markdown file with YAML front matter. The body is the canonical source text. Specialized blocks in front matter feed different outputs.

## Quick start
```bash
pip install -r requirements.txt
python scripts/build_all.py
```

## Recommended future additions
- assessment bank
- asset registry (images, maps, handouts)
- citation/source library
- simulation state models
- analytics events for the website/course
- county/census data loaders
- BLS labor data loaders
- story archive / oral history importer
