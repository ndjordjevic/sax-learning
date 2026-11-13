#!/usr/bin/env python3
"""Estimate the concert key of audio tracks and the pitch shift between them.

Uses an energy-weighted STFT chromagram. The CQT chroma (librosa's default
choice) gave wrong shifts on the Band 2 play-alongs: it called alto vs tenor
"same pitch" when pitch-tracking the sax melody proved G minor vs D minor.

Usage:
    .venv-demucs/bin/python tools/key_compare.py A.mp3 B.mp3 [C.mp3 ...]

For each file, prints the estimated concert key (Krumhansl-Schmuckler profile
fit). For every file after the first, also prints the transposition that best
maps it onto the first file. Typical check: alto vs tenor play-along of the
same piece. If both are set up for the same written part, the tenor track sounds
a perfect 4th (5 semitones) below the alto one.

LIMITATION (tested 2026-11-13 on all 26 Band 2 alto/tenor pairs): whole-mix
chroma is noisy. Keys a 4th/5th apart share 6 of 7 notes, so the "shift" line
often wrongly says "same pitch" exactly in the alto-vs-tenor case. Trust the
per-file key lines more than the shift line, and confirm anything important by
ear or against the score. Melody pitch-tracking (librosa.pyin) on full mixes was
no better: bass and piano cause octave and pitch-class errors.

Written key for a horn = concert key + 2 semitones (tenor, Bb) or + 9 (alto, Eb).
"""
import sys

import librosa
import numpy as np

NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def chroma(path):
    y, sr = librosa.load(path, sr=22050, mono=True)
    c = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=8192, norm=None).sum(axis=1)
    return c / c.sum(), len(y) / sr


def key_of(c):
    best = max(
        (np.corrcoef(np.roll(prof, k), c)[0, 1], k, mode)
        for prof, mode in ((MAJOR, "major"), (MINOR, "minor"))
        for k in range(12)
    )
    return best[1], best[2], best[0]


def shift(ref, other):
    """Semitones to move `other` so it matches `ref` (-5..+6), plus match quality."""
    scores = sorted(((np.corrcoef(ref, np.roll(other, k))[0, 1], k) for k in range(12)), reverse=True)
    r, k = scores[0]
    return (k if k <= 6 else k - 12), r


def main(paths):
    if not paths:
        sys.exit(__doc__)
    results = [(p, *chroma(p)) for p in paths]
    ref = results[0][1]
    for p, c, dur in results:
        tonic, mode, r = key_of(c)
        name = p.rsplit("/", 1)[-1]
        print(f"{name}\n    {dur:5.1f}s  concert key ≈ {NAMES[tonic]} {mode} (fit {r:.2f})"
              f"  → tenor written {NAMES[(tonic + 2) % 12]} {mode}, alto written {NAMES[(tonic + 9) % 12]} {mode}")
        if c is not ref:
            k, rr = shift(ref, c)
            rel = "same pitch" if k == 0 else f"sounds {abs(k)} semitone(s) {'lower' if k > 0 else 'higher'} than the first file"
            print(f"    vs first file: {rel} (match {rr:.2f})")


if __name__ == "__main__":
    main(sys.argv[1:])
