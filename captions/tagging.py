# TODO: Type ignore is bad, but pyrightconfig.json wasn't registering, too lazy to fix rn
# Proposed solution: Uninstall pyright :) ruff is such a chill guy
from fugashi import Tagger  # type: ignore
from collections import Counter
from video.processing import TranscriptResult  # TODO: This import seems ugly

tagger = Tagger("-Owakati")


def analyze_subtitles(transcript: TranscriptResult):
    # Initialize counters
    word_freq = Counter()
    kanji_freq = Counter()  # Might not need this
    all_tokens = []

    for item in transcript.segments:
        print(item)
