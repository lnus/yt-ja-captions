import json
from video import processing as video


if __name__ == "__main__":
    video_id = "L6qKgovhkdw"
    transcript, auto_generated, translated = video.get_captions(video_id)
    print(auto_generated, translated)
    with open("t.json", "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=4)
