from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi as yta
from enum import Enum, auto


class TranscriptType(Enum):
    MANUAL = auto()
    GENERATED = auto()
    MANUAL_TRANSLATED = auto()
    GENERATED_TRANSLATED = auto()


def get_video_metadata(video_id: str):
    ydl_opts = {"quiet": True}

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_id, download=False)
        assert info is not None  # Hacky error handling, ship it.

        return {
            "title": info.get("title"),
            "description": info.get("description"),
            "duration": info.get("duration"),
            "view_count": info.get(
                "view_count"
            ),  # This will be invalidated instantly, do I need to store it?
            "uploader": info.get("uploader"),
            "upload_date": info.get("upload_date"),
            "thumbnail": info.get("thumbnail"),
            "tags": info.get("tags", []),
        }


def get_captions(video_id: str, lang_code: str = "ja"):
    transcripts = yta.list_transcripts(video_id)

    transcript_methods = [
        (
            TranscriptType.MANUAL,
            transcripts.find_manually_created_transcript,
            [lang_code],
            False,
            False,
        ),
        (
            TranscriptType.GENERATED,
            transcripts.find_generated_transcript,
            [lang_code],
            True,
            False,
        ),
        (
            TranscriptType.MANUAL_TRANSLATED,
            transcripts.find_manually_created_transcript,
            ["en"],
            False,
            True,
        ),
        (
            TranscriptType.GENERATED_TRANSLATED,
            transcripts.find_transcript,
            ["en"],
            True,
            True,
        ),
    ]

    auto_generated = False
    translated = False
    transcript = None

    for method, func, args, sets_auto, sets_translated in transcript_methods:
        try:
            transcript = (
                func(args).translate(lang_code)
                if "TRANSLATED" in method.name
                else func(args)
            )
            auto_generated = sets_auto
            translated = sets_translated
            break  # Exit loop on success
        except Exception:
            print(f"Did not find {method.name.lower()} transcript.")

    return (transcript.fetch() if transcript else None), auto_generated, translated
