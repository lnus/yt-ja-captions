from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Callable
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi as yta
from enum import Enum, auto
from ftfy import fix_encoding
import unicodedata


class TranscriptType(Enum):
    MANUAL = auto()
    GENERATED = auto()
    MANUAL_TRANSLATED = auto()
    GENERATED_TRANSLATED = auto()


@dataclass
class TranscriptMethod:
    type: TranscriptType
    func: Callable
    args: List[str]
    sets_auto: bool
    sets_translated: bool


@dataclass
class TranscriptSegment:
    text: str
    start: float
    duration: float

    @classmethod
    def from_dict(cls, data: dict) -> "TranscriptSegment":
        text = fix_encoding(data["text"])

        return cls(text=text, start=data["start"], duration=data["duration"])


@dataclass
class TranscriptResult:
    segments: List[TranscriptSegment]
    auto_generated: bool
    translated: bool


@dataclass
class VideoMetadata:
    title: str
    description: str
    duration: int
    view_count: int
    uploader: str
    upload_date: datetime
    thumbnail: str
    tags: List[str]

    @classmethod
    def from_yt_dlp(cls, info: dict) -> "VideoMetadata":
        """Create VideoMetadata from yt-dlp info dictionary."""
        upload_date_str = info.get("upload_date", "")
        upload_date = (
            datetime.strptime(upload_date_str, "%Y%m%d")
            if upload_date_str
            else datetime.now()
        )

        return cls(
            title=info.get("title", ""),
            description=info.get("description", ""),
            duration=info.get("duration", 0),
            view_count=info.get("view_count", 0),
            uploader=info.get("uploader", ""),
            upload_date=upload_date,
            thumbnail=info.get("thumbnail", ""),
            tags=info.get("tags", []),
        )


def get_video_metadata(video_id: str) -> Optional[VideoMetadata]:
    """
    Fetch metadata for a YouTube video.

    Args:
        video_id: YouTube video ID

        Returns:
        VideoMetadata object if successful, None if extraction fails

    Raises:
        ValueError: If video_id is invalid or empty
    """
    if not video_id:
        raise ValueError("Video ID cannot be empty")

    ydl_opts = {"quiet": True, "extract_flat": True}

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_id, download=False)
            if not info:
                return None
            return VideoMetadata.from_yt_dlp(info)

    except Exception as e:
        # TODO: Better logging
        print(f"Error extracting metadata for video {video_id}: {str(e)}")
        return None


def get_captions(video_id: str, lang_code: str = "ja") -> TranscriptResult:
    """
    Fetch captions for a YouTube video with fallback options for different transcript types.

    Args:
        video_id: YouTube video ID
        lang_code: Language code for the desired captions (default: "ja")

    Returns:
        Tuple containing:
        - List of transcript dictionaries if successful, None if extraction fails
        - Boolean indicating if the transcript is auto-generated
        - Boolean indicating if the transcript is translated

    Raises:
        ValueError: If video_id is invalid or empty
    """
    if not video_id:
        raise ValueError("Video ID cannot be empty")

    transcripts = yta.list_transcripts(video_id)

    transcript_methods = [
        TranscriptMethod(
            type=TranscriptType.MANUAL,
            func=transcripts.find_manually_created_transcript,
            args=[lang_code],
            sets_auto=False,
            sets_translated=False,
        ),
        TranscriptMethod(
            type=TranscriptType.GENERATED,
            func=transcripts.find_generated_transcript,
            args=[lang_code],
            sets_auto=True,
            sets_translated=False,
        ),
        TranscriptMethod(
            type=TranscriptType.MANUAL_TRANSLATED,
            func=transcripts.find_manually_created_transcript,
            args=["en"],
            sets_auto=False,
            sets_translated=True,
        ),
        TranscriptMethod(
            type=TranscriptType.GENERATED_TRANSLATED,
            func=transcripts.find_transcript,
            args=["en"],
            sets_auto=True,
            sets_translated=True,
        ),
    ]

    auto_generated = False
    translated = False
    transcript = None

    for method in transcript_methods:
        try:
            transcript = (
                method.func(method.args).translate(lang_code)
                if "TRANSLATED" in method.type.name
                else method.func(method.args)
            )
            auto_generated = method.sets_auto
            translated = method.sets_translated
            break
        except Exception:
            print(f"Did not find {method.type.name.lower()} transcript.")

    if not transcript:
        raise ValueError("Something went wrong terribly, this is not a value error")

    segment_dicts = transcript.fetch()
    print(segment_dicts)
    segments = [TranscriptSegment.from_dict(seg) for seg in segment_dicts]

    return TranscriptResult(
        segments=segments,
        auto_generated=auto_generated,
        translated=translated,
    )
