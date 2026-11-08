"""Fetch transcripts and metadata for YouTube videos."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi


@dataclass
class VideoData:
    video_id: str
    title: str
    url: str
    transcript: Optional[str]  # None when unavailable


def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:shorts/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Cannot extract video ID from URL: {url}")


def _fetch_title(video_id: str, url: str) -> str:
    try:
        from pytubefix import YouTube
        yt = YouTube(url)
        return yt.title or video_id
    except Exception:
        return video_id


def fetch_video(url: str, title_override: Optional[str] = None) -> VideoData:
    video_id = extract_video_id(url)
    title = title_override or _fetch_title(video_id, url)

    try:
        ytt = YouTubeTranscriptApi()
        fetched = ytt.fetch(video_id)
        transcript = " ".join(entry.text for entry in fetched)
    except Exception as exc:
        print(f"  [warn] Could not fetch transcript for {video_id}: {exc}")
        transcript = None

    return VideoData(video_id=video_id, title=title, url=url, transcript=transcript)
