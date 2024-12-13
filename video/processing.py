from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Callable, Dict, Any
from yt_dlp import YoutubeDL
from enum import Enum, auto
from urllib.request import urlopen
import json


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


@dataclass
class TranscriptSegment:
    text: str
    start: float
    duration: float

    @classmethod
    def from_subtitle_entry(
        cls, entry: Dict[str, Any]
    ) -> Optional["TranscriptSegment"]:
        try:
            # Debug print to see the entry structure
            # print(
            #     f"Processing entry: {json.dumps(entry, indent=2, ensure_ascii=False)}"
            # )

            if "segs" in entry:
                # Handle segmented format
                text = " ".join(seg["utf8"] for seg in entry["segs"] if "utf8" in seg)
                start_time = entry.get("tStartMs", 0) / 1000.0
                duration = entry.get("dDurationMs", 0) / 1000.0
            elif "aAppend" in entry:
                # Skip append entries
                return None
            else:
                # Handle standard format
                text = entry.get("text", "")
                start_time = entry.get("tStartMs", 0) / 1000.0
                duration = entry.get("dDurationMs", 0) / 1000.0

            return cls(
                text=text.replace("\u200b", "").strip(),
                start=start_time,
                duration=duration,
            )
        except Exception as e:
            print(f"Error processing entry: {str(e)}")
            print(
                f"Problematic entry: {json.dumps(entry, indent=2, ensure_ascii=False)}"
            )
            return None


@dataclass
class TranscriptResult:
    segments: List[TranscriptSegment]
    auto_generated: bool
    translated: bool


def fetch_subtitle_data(url: str) -> Optional[Dict]:
    """Fetch and parse subtitle data from a URL."""
    try:
        with urlopen(url) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Error fetching subtitles: {str(e)}")
        return None


# TODO: Use same youtube instance or something idk, im very tired
def get_captions(video_id: str) -> Optional[TranscriptResult]:
    """
    Extract Japanese captions from a YouTube video, preferring manual captions
    but falling back to auto-generated or translated ones if necessary.

    Args:
        video_id: YouTube video ID

    Returns:
        TranscriptResult object if captions are found, None otherwise
    """
    ydl_opts = {
        "writesubtitles": True,
        "subtitleslangs": ["ja"],
        "skip_download": True,
        "quiet": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_id, download=False)
        if not info:
            return None

        # Try to get manual subtitles first
        if info.get("subtitles") and "ja" in info["subtitles"]:
            subtitle_info = info["subtitles"]["ja"]
            for fmt in subtitle_info:
                if fmt.get("ext") == "json3":
                    subtitles = fetch_subtitle_data(fmt["url"])
                    if subtitles and "events" in subtitles:
                        segments = [
                            segment
                            for entry in subtitles["events"]
                            if (segment := TranscriptSegment.from_subtitle_entry(entry))
                            is not None
                        ]
                        if segments:
                            return TranscriptResult(
                                segments=segments,
                                auto_generated=False,
                                translated=False,
                            )

        # Fall back to automatic captions if available
        if info.get("automatic_captions") and "ja" in info["automatic_captions"]:
            auto_info = info["automatic_captions"]["ja"]
            for fmt in auto_info:
                if fmt.get("ext") == "json3":
                    subtitles = fetch_subtitle_data(fmt["url"])
                    if subtitles and "events" in subtitles:
                        segments = [
                            segment
                            for entry in subtitles["events"]
                            if (segment := TranscriptSegment.from_subtitle_entry(entry))
                            is not None
                        ]
                        if segments:
                            return TranscriptResult(
                                segments=segments, auto_generated=True, translated=False
                            )

        # Finally, try translated captions
        for lang, subtitle_info in info.get("subtitles", {}).items():
            if lang != "ja":
                for fmt in subtitle_info:
                    if fmt.get("ext") == "json3":
                        subtitles = fetch_subtitle_data(fmt["url"])
                        if subtitles and "events" in subtitles:
                            segments = [
                                segment
                                for entry in subtitles["events"]
                                if (
                                    segment := TranscriptSegment.from_subtitle_entry(
                                        entry
                                    )
                                )
                                is not None
                            ]
                            if segments:
                                return TranscriptResult(
                                    segments=segments,
                                    auto_generated=False,
                                    translated=True,
                                )

        return None
