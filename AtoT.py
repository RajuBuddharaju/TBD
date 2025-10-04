"""
Provide functionality for converting audio to text.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import shutil
import re


# ---- Public return types ----------------------------------------------------

@dataclass(frozen=True)
class Word:
    start: float
    end: float
    text: str

@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str
    words: List[Word]  # may be empty

@dataclass(frozen=True)
class Sentence:
    start: float
    end: float
    text: str

@dataclass(frozen=True)
class Transcript:
    text: str
    segments: List[Segment]
    sentences: List[Sentence]
    srt: Optional[str] = None          # segment-based SRT
    vtt: Optional[str] = None          # segment-based VTT 
    srt_sentences: Optional[str] = None  # sentence-based SRT 
    vtt_sentences: Optional[str] = None  # sentence-based VTT


# ---- Private utilities ------------------------------------------------------

def _resolve_path(audio: str | Path) -> Path:
    p = Path(audio).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Audio file not found: {p}")
    if not p.is_file():
        raise ValueError(f"Expected a file path, got: {p}")
    return p

def _load_model(size: str, device: str = "auto", compute_type: str = "auto"):
    from faster_whisper import WhisperModel
    resolved_device = None if device != "auto" else ("cuda" if shutil.which("nvidia-smi") else "cpu")
    if compute_type == "auto":
        compute_type = "float16" if resolved_device == "cuda" else "int8"
    return WhisperModel(size, device=resolved_device, compute_type=compute_type)

def _fmt_ts(seconds: float, srt: bool = True) -> str:
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    sep = "," if srt else "."
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"

def _to_srt(items: List[tuple[float, float, str]]) -> str:
    # items: list of (start, end, text)
    lines = []
    for i, (st, en, txt) in enumerate(items, start=1):
        lines += [str(i), f"{_fmt_ts(st, True)} --> {_fmt_ts(en, True)}", txt.strip(), ""]
    return "\n".join(lines).strip() + "\n"

def _to_vtt(items: List[tuple[float, float, str]]) -> str:
    body = []
    for st, en, txt in items:
        body += [f"{_fmt_ts(st, False)} --> {_fmt_ts(en, False)}", txt.strip(), ""]
    return "WEBVTT\n\n" + "\n".join(body).strip() + "\n"

_ABBREV = {
    "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "vs.", "etc.",
    "e.g.", "i.e.", "u.s.", "u.k.", "inc.", "ltd.", "co.", "no."
}

def _is_sentence_boundary(prev_word: str, next_char: str) -> bool:
    # Basic rule: '.', '?', '!' end a sentence unless it's a common abbreviation.
    w = prev_word.lower()
    if w in _ABBREV:
        return False
    return next_char in ".?!"

def _words_to_sentences(
    words: List[Word],
    *,
    max_pause: float = 0.9,        # split if long silence between words
    min_chars: int = 24,           # avoid super-short "sentences"
) -> List[Sentence]:
    sentences: List[Sentence] = []
    if not words:
        return sentences

    buf: List[Word] = []
    buf_start = words[0].start

    def flush():
        nonlocal buf, buf_start
        if not buf:
            return
        text = "".join(w.text for w in buf).strip()
        # Normalize spaces around punctuation
        text = re.sub(r"\s+([,.;:?!])", r"\1", text)
        text = re.sub(r"\s{2,}", " ", text)
        start = buf_start
        end = buf[-1].end
        if text:
            sentences.append(Sentence(start=start, end=end, text=text))
        buf = []
        buf_start = None

    for i, w in enumerate(words):
        if not buf:
            buf_start = w.start
        buf.append(w)

        # Lookahead to decide boundary
        next_word = words[i + 1] if i + 1 < len(words) else None

        # Heuristic 1: long pause
        if next_word and (next_word.start - w.end) >= max_pause:
            # End sentence if we already have a decent length
            if sum(len(x.text) for x in buf) >= min_chars:
                flush()
            continue

        # Heuristic 2: punctuation-based
        last_char = w.text[-1] if w.text else ""
        if _is_sentence_boundary(w.text, last_char):
            # Keep aggregating if extremely short; else split
            total_chars = sum(len(x.text) for x in buf)
            if total_chars >= min_chars or (not next_word):
                flush()

    # trailing buffer
    if buf:
        flush()

    return sentences


# ---- Public API -------------------------------------------------------------

def transcribe_audio(
    audio: str | Path,
    *,
    language: Optional[str] = None,     # None = auto-detect
    model_size: str = "small",          # "tiny" | "base" | "small" | "medium" | "large-v3"
    vad_filter: bool = True,
    beam_size: int = 5,
    sentence_timestamps: bool = False,   # if you want per-sentence timing
    word_timestamps: bool = False,      # if you want per-word timing
    # this stuff might be unnecessary
    emit_srt: bool = False,             # segment-based SRT
    emit_vtt: bool = False,             # segment-based VTT
    emit_srt_sentences: bool = False,   # sentence-based SRT
    emit_vtt_sentences: bool = False,   # sentence-based VTT
) -> Transcript:
    """
    Transcribe an audio file to text with segment and (optionally) sentence timestamps.

    Returns
    -------
    Transcript
        - text: full transcript
        - segments: model segments (start/end/text + words if requested)
        - sentences: sentence-level chunks with start/end/text
        - srt / vtt: segment-based subtitles if requested
        - srt_sentences / vtt_sentences: sentence-based subtitles if requested
    """
    audio_path = _resolve_path(audio)
    model = _load_model(model_size)

    need_words = word_timestamps or sentence_timestamps
    segments_iter, _info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=vad_filter,
        beam_size=beam_size,
        word_timestamps=need_words,   # get words only if needed
    )

    segs: List[Segment] = []
    text_parts: List[str] = []
    all_words: List[Word] = []

    for s in segments_iter:
        seg_text = s.text.strip()
        text_parts.append(seg_text)
        words: List[Word] = []
        if need_words and getattr(s, "words", None):
            for w in s.words:
                # faster-whisper uses w.word for the token text (includes spaces/punct)
                words.append(Word(start=float(w.start), end=float(w.end), text=w.word))
            all_words.extend(words)

        segs.append(
            Segment(
                start=float(s.start),
                end=float(s.end),
                text=seg_text,
                words=words,
            )
        )

    full_text = " ".join(tp for tp in text_parts if tp)

    # Build sentence-level timings
    sentences: List[Sentence] = []
    if sentence_timestamps:
        sentences = _words_to_sentences(all_words)

    # Subtitles
    srt = _to_srt([(s.start, s.end, s.text) for s in segs]) if emit_srt else None
    vtt = _to_vtt([(s.start, s.end, s.text) for s in segs]) if emit_vtt else None
    srt_sent = _to_srt([(s.start, s.end, s.text) for s in sentences]) if emit_srt_sentences else None
    vtt_sent = _to_vtt([(s.start, s.end, s.text) for s in sentences]) if emit_vtt_sentences else None

    # If caller didn’t ask for words explicitly, clear them from segments
    if not word_timestamps:
        segs = [Segment(start=s.start, end=s.end, text=s.text, words=[]) for s in segs]

    return Transcript(
        text=full_text,
        segments=segs,
        sentences=sentences,
        srt=srt,
        vtt=vtt,
        srt_sentences=srt_sent,
        vtt_sentences=vtt_sent,
    )

