from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from PIL import Image

from captions.tagger import SubtitleAnalysis


def create_mask_from_frame(image_path: str) -> np.ndarray:
    image = Image.open(image_path).convert("L")
    mask = np.array(image)
    return mask


def create_kanji_wordcloud(analysis: SubtitleAnalysis) -> Tuple[plt.Figure, plt.Axes]:  # type: ignore
    """Create a word cloud from kanji compounds."""
    fig, ax = plt.subplots(figsize=(12, 8))
    mask = create_mask_from_frame("apple.png")

    wordcloud = WordCloud(
        font_path="noto.ttc",
        width=mask.shape[1],
        height=mask.shape[0],
        background_color="white",
        colormap="Set3",
        mask=mask,
    ).generate_from_frequencies(dict(analysis.kanji_compound_frequency))

    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Kanji Compound Word Cloud", pad=20)

    return fig, ax


def create_visual_plot(analysis: SubtitleAnalysis, output_dir: Path) -> None:
    """Create and save a visualization of a SubtitleAnalysis object"""
    output_dir.mkdir(parents=True, exist_ok=True)

    cloud_fig, _ = create_kanji_wordcloud(analysis)
    cloud_fig.savefig(output_dir / "kanji_cloud.png", bbox_inches="tight", dpi=300)
    plt.close(cloud_fig)
