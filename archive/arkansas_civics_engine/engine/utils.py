from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = ROOT / 'content' / 'courses'
EXPORTS_ROOT = ROOT / 'exports'


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def parse_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
    if not text.startswith('---\n'):
        return {}, text
    try:
        _, rest = text.split('---\n', 1)
        fm, body = rest.split('\n---\n', 1)
    except ValueError:
        return {}, text
    data = yaml.safe_load(fm) or {}
    return data, body.strip()


def load_segment(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding='utf-8')
    metadata, body = parse_front_matter(raw)
    metadata['__path__'] = str(path)
    metadata['__body__'] = body
    return metadata


def list_segments() -> List[Dict[str, Any]]:
    segments: List[Dict[str, Any]] = []
    if not CONTENT_ROOT.exists():
        return segments
    for seg_path in CONTENT_ROOT.rglob('*.md'):
        if seg_path.name.startswith('.'):
            continue
        data = load_segment(seg_path)
        segments.append(data)
    segments.sort(key=lambda s: (
        s.get('course_slug', ''),
        s.get('chapter_slug', ''),
        int(s.get('segment_order', 9999)),
        s.get('segment_slug', '')
    ))
    return segments


def group_segments(segments: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    grouped: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for seg in segments:
        course = seg['course_slug']
        chapter = seg['chapter_slug']
        grouped.setdefault(course, {}).setdefault(chapter, []).append(seg)
    return grouped


def extract_block(body: str, heading: str) -> str:
    marker = f'## {heading}'
    if marker not in body:
        return ''
    parts = body.split(marker)
    if len(parts) < 2:
        return ''
    after = parts[1].strip()
    lines = after.splitlines()
    out = []
    for line in lines:
        if line.startswith('## '):
            break
        out.append(line)
    return '\n'.join(out).strip()


def to_json(data: Any, path: Path) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
