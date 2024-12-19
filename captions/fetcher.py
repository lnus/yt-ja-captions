import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence
from urllib.request import urlopen

from yt_dlp import YoutubeDL


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
            if "aAppend" in entry:
                return None

            start_time = entry.get("tStartMs", 0) / 1000.0
            duration = entry.get("dDurationMs", 0) / 1000.0

            text = (
                " ".join(seg["utf8"] for seg in entry["segs"] if "utf8" in seg)
                if "segs" in entry
                else entry.get("text", "")
            )

            return cls(
                text=text,
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


def process_subtitle_formats(
    formats: Sequence[Dict[str, Any]],
    auto_generated: bool = False,
    translated: bool = False,
) -> Optional[TranscriptResult]:
    """
    Process a sequence of subtitle formats and return the first valid TranscriptResult.

    Args:
        formats: Sequence of subtitle format dictionaries
        auto_generated: Whether these are auto-generated captions
        translated: Whether these are translated captions

    Returns:
        TranscriptResult if valid subtitles are found, None otherwise
    """
    for fmt in formats:
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
                        auto_generated=auto_generated,
                        translated=translated,
                    )
    return None


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

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_id, download=False)

            if not info:
                print("No info could be extracted")
                return None

            if not info.get("subtitles") and not info.get("automatic_captions"):
                print("No types of subtitles were found")
                return None

            # Try to get manual subtitles first
            if info.get("subtitles") and "ja" in info["subtitles"]:
                result = process_subtitle_formats(
                    info["subtitles"]["ja"], auto_generated=False, translated=False
                )
                if result:
                    return result

            # Fall back to automatic captions if available
            if info.get("automatic_captions") and "ja" in info["automatic_captions"]:
                result = process_subtitle_formats(
                    info["automatic_captions"]["ja"],
                    auto_generated=True,
                    translated=False,
                )
                if result:
                    return result

            # Finally, try translated captions
            for lang, subtitle_info in info.get("subtitles", {}).items():
                if lang != "ja":
                    result = process_subtitle_formats(
                        subtitle_info, auto_generated=False, translated=True
                    )
                    if result:
                        return result

            return None
    except Exception as e:
        print(f"Error extracting captions: {str(e)}")
        return None
