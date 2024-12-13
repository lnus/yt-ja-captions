from captions.tagger import SubtitleAnalysis


def print_analysis(analysis: SubtitleAnalysis, top_n: int = 10) -> None:
    """Print a basic analysis summary, thanks Claude, I was too lazy to write this"""
    print("\n=== Most Common Words (All) ===")
    for token, freq in analysis.token_frequency.most_common(top_n):
        print(f"{token}: {freq}")

    print("\n=== Most Common Parts of Speech ===")
    for pos, freq in analysis.pos_frequency.most_common():
        print(f"{pos}: {freq}")

    print("\n=== Most Common Content Words (No Particles) ===")
    for word, freq in analysis.content_word_frequency.most_common(top_n):
        print(f"{word}: {freq}")

    print("\n=== Most Common Kanji Compounds ===")
    for compound, freq in analysis.kanji_compound_frequency.most_common(top_n):
        print(f"{compound}: {freq}")

    print("\n=== Most Common Dictionary Forms ===")
    for form, freq in analysis.dictionary_form_frequency.most_common(top_n):
        print(f"{form}: {freq}")
