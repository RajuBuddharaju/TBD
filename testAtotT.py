from AtoT import transcribe_audio


file = "/home/raju/Downloads/Hate.mp4"

# Per-segment timestamps
tx = transcribe_audio(file, model_size="small", emit_srt=True)
print(tx.text)                 # full transcript
print(tx.segments[0].start)    # e.g., 0.0
print(tx.segments[0].end)      # e.g., 3.2
print(tx.segments[0].text)     # segment text
open("out.srt", "w").write(tx.srt or "")

# With per-word timestamps too
tx_words = transcribe_audio(file, word_timestamps=True)
print(tx_words.segments[0].words[:3])  # [Word(start=..., end=..., text='Hello'), ...]
