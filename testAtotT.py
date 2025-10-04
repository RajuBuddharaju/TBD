from AtoT import transcribe_audio

tx = transcribe_audio(
    "C:\\Users\\20221051\\Downloads\\BegumHate.mp4",
    sentence_timestamps=True,
)

# Full transcript first
print(tx.text, end="\n\n")

# Per-sentence: print the sentence text first, then its timings
for i, s in enumerate(tx.sentences, 1):
    print(f"{i}. {s.text}")
    print(f"   start={s.start:.2f}s  end={s.end:.2f}s  dur={s.end - s.start:.2f}s\n")