from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List

from .utils import EXPORTS_ROOT, ensure_dir, extract_block, group_segments, list_segments, to_json


def build_book() -> Path:
    segments = list_segments()
    grouped = group_segments(segments)
    out_path = EXPORTS_ROOT / 'book' / 'compiled_book.md'
    ensure_dir(out_path.parent)
    lines: List[str] = ['# Arkansas Civics\n']
    for course_slug, chapters in grouped.items():
        course_title = next((s.get('course_title') for s in segments if s.get('course_slug') == course_slug), course_slug)
        lines.append(f'\n# {course_title}\n')
        for chapter_slug, chapter_segments in chapters.items():
            chapter_title = chapter_segments[0].get('chapter_title', chapter_slug)
            lines.append(f'\n## {chapter_title}\n')
            for seg in chapter_segments:
                if not seg.get('book', {}).get('include', True):
                    continue
                sec_title = seg.get('book', {}).get('section_title', seg.get('segment_title'))
                lines.append(f'\n### {sec_title}\n')
                lines.append(extract_block(seg['__body__'], 'Canonical Body') or seg['__body__'])
    out_path.write_text('\n'.join(lines), encoding='utf-8')
    return out_path


def build_workbook() -> Path:
    segments = list_segments()
    grouped = group_segments(segments)
    out_path = EXPORTS_ROOT / 'workbook' / 'participant_workbook.md'
    ensure_dir(out_path.parent)
    lines: List[str] = ['# Arkansas Civics Workbook\n']
    for course_slug, chapters in grouped.items():
        course_title = next((s.get('course_title') for s in segments if s.get('course_slug') == course_slug), course_slug)
        lines.append(f'\n# {course_title}\n')
        for chapter_slug, chapter_segments in chapters.items():
            chapter_title = chapter_segments[0].get('chapter_title', chapter_slug)
            lines.append(f'\n## {chapter_title}\n')
            for seg in chapter_segments:
                if not seg.get('workbook', {}).get('include', False):
                    continue
                title = seg.get('workbook', {}).get('prompt_title', seg.get('segment_title'))
                block = extract_block(seg['__body__'], 'Workbook Prompt')
                if block:
                    lines.append(f'\n### {title}\n{block}\n')
    out_path.write_text('\n'.join(lines), encoding='utf-8')
    return out_path


def build_workshop() -> Path:
    segments = list_segments()
    grouped = group_segments(segments)
    out_path = EXPORTS_ROOT / 'workshop' / 'live_workshop_guide.md'
    ensure_dir(out_path.parent)
    lines: List[str] = ['# Arkansas Civics Workshop Guide\n']
    for course_slug, chapters in grouped.items():
        course_title = next((s.get('course_title') for s in segments if s.get('course_slug') == course_slug), course_slug)
        lines.append(f'\n# {course_title}\n')
        for chapter_slug, chapter_segments in chapters.items():
            chapter_title = chapter_segments[0].get('chapter_title', chapter_slug)
            lines.append(f'\n## {chapter_title}\n')
            for seg in chapter_segments:
                if not seg.get('workshop', {}).get('include', False):
                    continue
                title = seg.get('workshop', {}).get('activity_title', seg.get('segment_title'))
                block = extract_block(seg['__body__'], 'Workshop Activity')
                if block:
                    lines.append(f'\n### {title}\n{block}\n')
    out_path.write_text('\n'.join(lines), encoding='utf-8')
    return out_path


def build_facilitator_guide() -> Path:
    segments = list_segments()
    grouped = group_segments(segments)
    out_path = EXPORTS_ROOT / 'facilitator' / 'facilitator_guide.md'
    ensure_dir(out_path.parent)
    lines: List[str] = ['# Arkansas Civics Facilitator Guide\n']
    for course_slug, chapters in grouped.items():
        course_title = next((s.get('course_title') for s in segments if s.get('course_slug') == course_slug), course_slug)
        lines.append(f'\n# {course_title}\n')
        for chapter_slug, chapter_segments in chapters.items():
            chapter_title = chapter_segments[0].get('chapter_title', chapter_slug)
            lines.append(f'\n## {chapter_title}\n')
            for seg in chapter_segments:
                if not seg.get('facilitator', {}).get('include', False):
                    continue
                title = seg.get('segment_title')
                note = seg.get('facilitator', {}).get('coaching_note', '')
                block = extract_block(seg['__body__'], 'Facilitator Notes')
                lines.append(f'\n### {title}\n**Coaching note:** {note}\n')
                if block:
                    lines.append(block + '\n')
    out_path.write_text('\n'.join(lines), encoding='utf-8')
    return out_path


def build_course_manifest() -> Path:
    segments = list_segments()
    grouped = group_segments(segments)
    manifest: Dict[str, Any] = {'courses': []}
    for course_slug, chapters in grouped.items():
        course_segments = [s for s in segments if s.get('course_slug') == course_slug]
        course_title = next((s.get('course_title') for s in course_segments), course_slug)
        course_obj: Dict[str, Any] = {
            'slug': course_slug,
            'title': course_title,
            'chapters': []
        }
        for chapter_slug, chapter_segments in chapters.items():
            chapter_obj: Dict[str, Any] = {
                'slug': chapter_slug,
                'title': chapter_segments[0].get('chapter_title', chapter_slug),
                'lessons': []
            }
            for seg in chapter_segments:
                if not seg.get('course', {}).get('include', True):
                    continue
                chapter_obj['lessons'].append({
                    'id': seg.get('id'),
                    'slug': seg.get('segment_slug'),
                    'title': seg.get('course', {}).get('lesson_title', seg.get('segment_title')),
                    'activity_type': seg.get('course', {}).get('activity_type', 'reading'),
                    'content': extract_block(seg['__body__'], 'Canonical Body') or seg['__body__'],
                    'interaction': extract_block(seg['__body__'], 'Course Interaction'),
                })
            course_obj['chapters'].append(chapter_obj)
        manifest['courses'].append(course_obj)
    out_path = EXPORTS_ROOT / 'course' / 'course_manifest.json'
    to_json(manifest, out_path)
    return out_path


def build_website_manifest() -> Path:
    segments = list_segments()
    pages: List[Dict[str, Any]] = []
    for seg in segments:
        if not seg.get('web', {}).get('include', True):
            continue
        pages.append({
            'id': seg.get('id'),
            'course_slug': seg.get('course_slug'),
            'chapter_slug': seg.get('chapter_slug'),
            'segment_slug': seg.get('segment_slug'),
            'title': seg.get('segment_title'),
            'content': extract_block(seg['__body__'], 'Canonical Body') or seg['__body__'],
            'sources': seg.get('sources', []),
            'tags': seg.get('tags', []),
        })
    out_path = EXPORTS_ROOT / 'website' / 'reader_manifest.json'
    to_json({'pages': pages}, out_path)
    return out_path
