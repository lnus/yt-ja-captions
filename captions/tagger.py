import re
from collections import Counter
from dataclasses import dataclass
from typing import List, Set

from fugashi import Tagger  # type: ignore

from captions.fetcher import TranscriptResult

tagger = Tagger("-Owakati")


@dataclass
class TokenInfo:
    surface: str  # The word as it appears in text
    dictionary_form: str  # Base form
    pos: str  # Part of speech
    features: List[str]  # Additional features


@dataclass
class SubtitleAnalysis:
    token_frequency: Counter
    pos_frequency: Counter
    dictionary_form_frequency: Counter
    kanji_compound_frequency: Counter
    content_word_frequency: Counter
    tokens: List[TokenInfo]
    total_words: int
    unique_words: int
    hapax_legomena: int  # words used exactly once
    total_characters: int
    unique_kanji: Set[str]
    single_use_kanji: Set[str]

    def get_hapax_percentage(self) -> float:
        """percentage of words that appear exactly once"""
        return (
            (self.hapax_legomena / self.unique_words * 100)
            if self.unique_words > 0
            else 0
        )

    def get_single_use_kanji_percentage(self) -> float:
        """percentage of kanji that appear exactly once"""
        return (
            (len(self.single_use_kanji) / len(self.unique_kanji) * 100)
            if self.unique_kanji
            else 0
        )

    def get_unique_words_percentage(self) -> float:
        """percentage of unique words relative to total words"""
        return (
            (self.unique_words / self.total_words * 100) if self.total_words > 0 else 0
        )


# Helper functions to produce more interesting data than that
# のwas the most common word
def is_kanji(char: str) -> bool:
    return re.match(r"[\u4e00-\u9faf]", char) is not None


def is_content_word(pos: str) -> bool:
    """Check if the part of speech represents a content word."""
    content_pos = {"名詞", "動詞", "形容詞", "形状詞", "副詞"}
    return pos in content_pos


def contains_kanji(text: str) -> bool:
    return any(is_kanji(char) for char in text)


def extract_kanji(text: str) -> Set[str]:
    """Extract all kanji characters from text."""
    return {char for char in text if is_kanji(char)}


# This function was written at 2AM with help from Claude 3.5 Sonnet, it was very helpful
# I am not very well versed in this type of parsing
def analyze_subtitles(transcript: TranscriptResult):
    token_freq = Counter()
    pos_freq = Counter()
    dictionary_freq = Counter()
    kanji_compound_freq = Counter()
    content_word_freq = Counter()
    kanji_freq = Counter()
    total_chars = 0
    all_kanji: Set[str] = set()
    all_tokens: List[TokenInfo] = []

    for segment in transcript.segments:
        parsed = tagger(segment.text)
        total_chars += len(segment.text)

        for token in parsed:
            # Ignore useless (sorry) symbols
            if token.feature.pos1 in {"記号", "補助記号", "空白"}:
                continue

            features = [
                f
                for f in [
                    token.feature.pos1,
                    token.feature.pos2,
                    token.feature.pos3,
                    token.feature.pos4,
                    token.feature.cType,
                    token.feature.cForm,
                ]
                if f
            ]

            token_info = TokenInfo(
                surface=token.surface,
                dictionary_form=token.feature.lemma or token.surface,
                pos=token.feature.pos1,
                features=features,
            )

            token_freq[token.surface] += 1
            pos_freq[token.feature.pos1] += 1
            dictionary_freq[token_info.dictionary_form] += 1

            if contains_kanji(token.surface):
                kanji_compound_freq[token.surface] += 1

                # Extract individual kanji
                token_kanji = extract_kanji(token.surface)
                all_kanji.update(token_kanji)
                for k in token_kanji:
                    kanji_freq[k] += 1

            if is_content_word(token.feature.pos1):
                content_word_freq[token.surface] += 1

            all_tokens.append(token_info)

    # Base metrics
    total_words = sum(token_freq.values())
    unique_words = len(token_freq)
    hapax_words = sum(1 for _, freq in token_freq.items() if freq == 1)
    single_use_kanji = {k for k, v in kanji_freq.items() if v == 1}

    return SubtitleAnalysis(
        token_frequency=token_freq,
        pos_frequency=pos_freq,
        dictionary_form_frequency=dictionary_freq,
        kanji_compound_frequency=kanji_compound_freq,
        content_word_frequency=content_word_freq,
        tokens=all_tokens,
        total_words=total_words,
        unique_words=unique_words,
        hapax_legomena=hapax_words,
        unique_kanji=all_kanji,
        single_use_kanji=single_use_kanji,
        total_characters=total_chars,
    )
