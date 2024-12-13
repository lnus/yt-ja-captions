from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from yt_dlp import YoutubeDL


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
    ydl_opts = {"quiet": True, "extract_flat": True}

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_id, download=False)
            if not info:
                return None
            return VideoMetadata.from_yt_dlp(info)

    except Exception as e:
        print(f"Error extracting metadata for video {video_id}: {str(e)}")
        return None
