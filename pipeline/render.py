"""Render Jinja2 templates into MyST Markdown chapter files."""
from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from pipeline.fetch import VideoData
from pipeline.summarize import Summary

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
CHAPTERS_DIR = Path(__file__).parent.parent / "book" / "chapters"


def _slug(video_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", video_id)


def render_chapter(video: VideoData, summary: Summary | None) -> Path:
    """Render a chapter .md file. summary=None produces a placeholder."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
    )

    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    slug = _slug(video.video_id)
    out_path = CHAPTERS_DIR / f"{slug}.md"

    if summary is None:
        template = env.get_template("placeholder.md.j2")
        content = template.render(
            title=video.title,
            video_id=video.video_id,
            url=video.url,
        )
    else:
        template = env.get_template("chapter.md.j2")
        content = template.render(
            title=video.title,
            video_id=video.video_id,
            url=video.url,
            abstract=summary["abstract"],
            key_insights=summary["key_insights"],
            deep_dive=summary["deep_dive"],
        )

    out_path.write_text(content, encoding="utf-8")
    return out_path
