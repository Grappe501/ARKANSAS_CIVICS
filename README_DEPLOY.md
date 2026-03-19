# Phase 13 — AI Auto-Generation for New Lessons

This package adds a generator that converts your source course segments into activation-format lessons.

## Included
- `scripts/generate_activation_lessons_ai.py`
- `prompts/activation_lesson_prompt.txt`
- `config/phase13_generation_config.json`
- `apps/phase-13-ai-generator/index.html`

## Modes

### 1) Template mode
Fast, deterministic, no API required.

```bash
python scripts/generate_activation_lessons_ai.py --course course_01_civic_awakening --chapter chapter_01 --mode template
```

### 2) OpenAI mode
Uses the OpenAI API to generate stronger activation lessons.

Requirements:
- Install the OpenAI Python package in your local environment
- Set `OPENAI_API_KEY`

```bash
pip install openai
set OPENAI_API_KEY=your_key_here
python scripts/generate_activation_lessons_ai.py --course course_01_civic_awakening --chapter chapter_01 --mode openai
```

## Generate everything
```bash
python scripts/generate_activation_lessons_ai.py --all --mode template
```

## Outputs
Generated bundles are written to:
- `exports/activation_generated/<bundle_name>/activation_lessons.json`
- `exports/activation_generated/<bundle_name>/markdown/`

Each bundle includes:
- JSON payload for system ingestion
- Markdown files for editing
- `manifest.json`
