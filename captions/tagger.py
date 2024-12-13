from collections import Counter
from dataclasses import dataclass
from typing import List

# TODO: Type ignore is bad, but pyrightconfig.json wasn't registering, too lazy to fix rn
# Proposed solution: Uninstall pyright :) ruff is such a chill guy
from fugashi import Tagger  # type: ignore

from captions.fetcher import TranscriptResult

tagger = Tagger("-Owakati")


# TODO: Maybe just use fugashi's, but this interface is easier for my purposes right now
@dataclass
class TokenInfo:
    surface: str  # The word as it appears in text
    dictionary_form: str  # Base form
    pos: str  # Part of speech
    features: List[str]  # Additional features


@dataclass
class SubtitleAnalysis:
    token_frequency: Counter  # Raw token frequency
    pos_frequency: Counter  # Part of speech frequency
    dictionary_form_frequency: Counter  # Base form frequency
    tokens: List[TokenInfo]  # All tokens with their information


# This function was written at 2AM with help from Claude 3.5 Sonnet, it was very helpful
# I am not very well versed in this type of parsing
def analyze_subtitles(transcript: TranscriptResult):
    token_freq = Counter()
    pos_freq = Counter()
    dictionary_freq = Counter()
    all_tokens: List[TokenInfo] = []

    for segment in transcript.segments:
        parsed = tagger(segment.text)

        for token in parsed:
            # Get token features
            features = [
                token.feature.pos1,
                token.feature.pos2,
                token.feature.pos3,
                token.feature.pos4,
                token.feature.cType,
                token.feature.cForm,
            ]

            # Filter out None values
            features = [f for f in features if f]

            token_info = TokenInfo(
                surface=token.surface,
                dictionary_form=token.feature.lemma or token.surface,
                pos=token.feature.pos1,
                features=features,
            )

            # TODO: Maybe skip punctuation/symbols? Lol
            # if token.feature.pos1 != "補助記号"
            token_freq[token.surface] += 1
            pos_freq[token.feature.pos1] += 1
            dictionary_freq[token_info.dictionary_form] += 1
            all_tokens.append(token_info)

    return SubtitleAnalysis(
        token_frequency=token_freq,
        pos_frequency=pos_freq,
        dictionary_form_frequency=dictionary_freq,
        tokens=all_tokens,
    )
