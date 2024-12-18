from captions.tagger import SubtitleAnalysis


def print_analysis(analysis: SubtitleAnalysis, top_n: int = 10) -> None:
    """print a fancy analysis summary with all the juicy stats! ✨"""

    # overall stats section
    print("\n=== overall stats ===")
    print(f"total words: {analysis.total_words}")
    print(
        f"unique words: {analysis.unique_words} ({analysis.get_unique_words_percentage():.1f}%)"
    )
    print(
        f"one-hit wonders: {analysis.hapax_legomena} ({analysis.get_hapax_percentage():.1f}%)"
    )
    print(f"total characters: {analysis.total_characters}")

    # kanji section
    print("\n=== 漢字 kanji stats ===")
    print(f"unique kanji: {len(analysis.unique_kanji)}")
    print(
        f"single-use kanji: {len(analysis.single_use_kanji)} ({analysis.get_single_use_kanji_percentage():.1f}%)"
    )

    # frequency sections (the classics)
    print("\n=== most common words ===")
    for token, freq in analysis.token_frequency.most_common(top_n):
        print(f"{token}: {freq}")

    print("\n=== most common parts of speech ===")
    for pos, freq in analysis.pos_frequency.most_common():
        print(f"{pos}: {freq}")

    print("\n=== most common content words (no particles!) ===")
    for word, freq in analysis.content_word_frequency.most_common(top_n):
        print(f"{word}: {freq}")

    print("\n=== most common kanji compounds ===")
    for compound, freq in analysis.kanji_compound_frequency.most_common(top_n):
        print(f"{compound}: {freq}")

    print("\n=== most common dictionary forms ===")
    for form, freq in analysis.dictionary_form_frequency.most_common(top_n):
        print(f"{form}: {freq}")
