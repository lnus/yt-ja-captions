from captions.tagger import SubtitleAnalysis
from pathlib import Path
import json

# Source: https://kanjiapi.dev/#!/documentation
JOYO_LIST_PATH = Path("joyo.json")  # TODO: Fix ugly


# TODO: Fully build this, and make a dataclass for results
def check_joyo(analysis: SubtitleAnalysis):
    joyo_kanji_count = 0
    with open(JOYO_LIST_PATH) as f:
        joyo = json.load(f)

    for kanji in analysis.unique_kanji:
        if kanji in joyo:
            joyo_kanji_count += 1

    print(
        f"found {joyo_kanji_count} out of {len(analysis.unique_kanji)} as joyo {round(joyo_kanji_count / len(analysis.unique_kanji), 2)*100}%"
    )
