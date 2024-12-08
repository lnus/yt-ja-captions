from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi as yta
import json


def get_video_metadata(video_id: str):
    ydl_opts = {"quiet": True}

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_id, download=False)
        assert info is not None  # Hacky error handling, ship it.

        return {
            "title": info.get("title"),
            "duration": info.get("duration"),
            "tags": info.get("tags", []),
        }


def get_japanese_captions(video_id: str):
    transcripts = yta.list_transcripts(video_id)
    lang_code = "ja"
    transcript = None
    auto_generated = False
    translated = False

    try:
        transcript = transcripts.find_manually_created_transcript([lang_code])
    except Exception as _:
        auto_generated = True
        print("Did not find manual translations")

    try:
        transcript = transcripts.find_generated_transcript([lang_code])
    except Exception as _:
        translated = True
        print("Did not find generated transcript translations")

    try:
        transcript = transcripts.find_transcript(["en"])
        transcript = transcript.translate("ja")
    except Exception as _:
        print("Did not find any transcript at all???")

    if transcript is not None:
        return transcript.fetch(), auto_generated, translated
    return None, auto_generated, translated


if __name__ == "__main__":
    foo = "L6qKgovhkdw"
    transcript, auto_generated, translated = get_japanese_captions(foo)
    print(auto_generated, translated)
    with open("t.json", "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=4)
