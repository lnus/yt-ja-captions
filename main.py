import json
from video import processing as video
from captions import tagging

# TODO: Add FastAPI maybe, not sure /shrug

if __name__ == "__main__":
    video_id = "ueEz7J2uRzs"
    metadata = video.get_video_metadata(video_id)
    captions = video.get_captions(video_id)
    out = "test.json"

    if not metadata or not captions:
        exit()  # Hacky

    print(metadata.title)
    print(metadata.uploader)
    print(metadata.upload_date)

    print(
        f"Captions\nTranslated: {captions.translated}\nAuto-generated: {captions.auto_generated}"
    )

    tagging.analyze_subtitles(captions)

    # print(f"Writing captions to {out}")
    # with open(out, "w", encoding="utf-8") as f:
    #     json.dump(captions.segments, f, ensure_ascii=False, indent=4)
