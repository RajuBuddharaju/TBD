"""
Provide functionality for converting audio to text.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import shutil


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
    words: List[Word]  # empty if word_timestamps=False


@dataclass(frozen=True)
class Transcript:
    text: str
    segments: List[Segment]
    srt: Optional[str] = None
    vtt: Optional[str] = None


# ---- Private utilities ------------------------------------------------------


def _resolve_path(audio: str | Path) -> Path:
    p = Path(audio).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Audio file not found: {p}")
    if not p.is_file():
        raise ValueError(f"Expected a file path, got: {p}")
    return p


def _load_model(size: str, device: str = "auto", compute_type: str = "auto"):
    try:
        from faster_whisper import WhisperModel
    except Exception as e:
        raise RuntimeError(
            "Missing dependency: faster-whisper\n"
            "Install with:  pip install 'faster-whisper>=1.0.0'"
        ) from e

    resolved_device = None if device == "auto" else device
    if resolved_device is None:
        resolved_device = "cuda" if shutil.which("nvidia-smi") else "cpu"

    if compute_type == "auto":
        compute_type = "float16" if resolved_device == "cuda" else "int8"

    return WhisperModel(size, device=resolved_device, compute_type=compute_type)


def _fmt_ts(seconds: float) -> str:
    # 00:00:00,000 for SRT; 00:00:00.000 for VTT (we'll swap delimiter later)
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _to_srt(segments: List[Segment]) -> str:
    lines = []
    for i, seg in enumerate(segments, start=1):
        lines.append(str(i))
        lines.append(f"{_fmt_ts(seg.start)} --> {_fmt_ts(seg.end)}")
        lines.append(seg.text.strip())
        lines.append("")  # blank line
    return "\n".join(lines).strip() + "\n"


def _to_vtt(segments: List[Segment]) -> str:
    # WebVTT requires a header and uses '.' as the milliseconds separator
    srt = _to_srt(segments)
    body = []
    for line in srt.splitlines():
        if "-->" in line:
            body.append(line.replace(",", "."))
        elif line.isdigit():
            # drop the numeric cue identifiers
            continue
        else:
            body.append(line)
    return "WEBVTT\n\n" + "\n".join(body).strip() + "\n"


# ---- Public API -------------------------------------------------------------


def transcribe_audio(
    audio: str | Path,
    *,
    language: Optional[str] = None,   # None = auto-detect
    model_size: str = "small",        # "tiny" | "base" | "small" | "medium" | "large-v3"
    vad_filter: bool = True,
    beam_size: int = 5,
    word_timestamps: bool = False,    # True => include per-word timing
    emit_srt: bool = False,
    emit_vtt: bool = False,
) -> Transcript:
    """
    Transcribe an audio file to text with timestamps.

    Returns
    -------
    Transcript
        - text: full transcript
        - segments: per-segment start/end/text (+ words if requested)
        - srt/vtt: optional subtitle strings when emit_srt/emit_vtt are True
    """
    audio_path = _resolve_path(audio)
    model = _load_model(model_size)

    segments_iter, _info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=vad_filter,
        beam_size=beam_size,
        word_timestamps=word_timestamps,
    )

    segs: List[Segment] = []
    text_parts: List[str] = []

    for s in segments_iter:
        words: List[Word] = []
        if word_timestamps and getattr(s, "words", None):
            for w in s.words:
                words.append(Word(start=float(w.start), end=float(w.end), text=w.word))
        seg_text = s.text.strip()
        text_parts.append(seg_text)
        segs.append(
            Segment(
                start=float(s.start),
                end=float(s.end),
                text=seg_text,
                words=words,
            )
        )

    full_text = " ".join(tp for tp in text_parts if tp)

    srt = _to_srt(segs) if emit_srt else None
    vtt = _to_vtt(segs) if emit_vtt else None

    return Transcript(text=full_text, segments=segs, srt=srt, vtt=vtt)

