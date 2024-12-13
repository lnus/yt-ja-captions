from captions import fetcher

if __name__ == "__main__":
    video_id = "7J5aS_pcBj4"
    result = fetcher.get_captions(video_id)
    if result:
        print(
            f"Found {'auto-generated' if result.auto_generated else 'manual'} "
            f"{'translated' if result.translated else 'original'} captions"
        )
        for segment in result.segments:
            print(f"[{segment.start:.2f}s] {segment.text}")
    else:
        print("No Japanese captions found")
