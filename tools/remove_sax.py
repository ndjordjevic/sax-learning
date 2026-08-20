#!/usr/bin/env python3
"""
Remove the saxophone from one channel of a Reading Jazz duet track,
leaving the rhythm section (piano + bass + drums) intact.

Reading Jazz play-along CDs are mixed as:
    LEFT  = Sax Part I  + rhythm section
    RIGHT = Sax Part II + rhythm section

This produces a rhythm-section-only backing track so you can play either
part yourself on a mono speaker (where a balance knob is not available).

Usage:
    python3 remove_sax.py <track.mp3> [--part I|II] [--outdir DIR] [--shifts N]

Example:
    python3 remove_sax.py "06_The_Smoothie.mp3" --part I

Requires: ffmpeg on PATH, and demucs + numpy in a virtualenv
(see ../audio-processing-methodology.md for setup).
"""

import argparse
import pathlib
import subprocess
import sys
import tempfile
import wave

import numpy as np

MODEL = "htdemucs_6s"  # 6-stem model: piano & guitar get their own stems,
                       # which leaves the sax alone in `other`.


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def read_wav(path, chan=None):
    """Read a wav as float64. chan=0/1 picks a channel; None averages to mono."""
    with wave.open(str(path), "rb") as w:
        n, ch = w.getnframes(), w.getnchannels()
        a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64)
    if ch == 2:
        a = a.reshape(-1, 2)
        a = a[:, chan] if chan is not None else a.mean(axis=1)
    return a


def write_wav(path, a, rate=44100):
    a = np.clip(np.round(a), -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(a.tobytes())


def db(x):
    return 20 * np.log10(np.sqrt(np.mean(x**2)) / 32768 + 1e-12)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("track", help="original STEREO mp3 from the CD rip")
    p.add_argument("--part", choices=["I", "II"], default="I",
                   help="which sax part to remove (I=left, II=right)")
    p.add_argument("--outdir", default=".")
    p.add_argument("--shifts", type=int, default=5,
                   help="shift-averaging passes; higher = cleaner, slower")
    args = p.parse_args()

    src = pathlib.Path(args.track).resolve()
    outdir = pathlib.Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    chan = 0 if args.part == "I" else 1

    # Sanity check: this must be the original stereo file. Demucs relies on
    # stereo panning to tell the hard-panned saxes from the centred rhythm
    # section, so feeding it a pre-split mono file separates noticeably worse.
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=channels",
         "-of", "default=noprint_wrappers=1:nokey=1", str(src)],
        capture_output=True, text=True, check=True).stdout.strip()
    if probe.split("\n")[0] != "2":
        sys.exit(f"ERROR: {src.name} is not stereo. Feed the ORIGINAL CD rip, "
                 "not an already-split mono file.")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)

        print(f"[1/3] separating with {MODEL} (shifts={args.shifts})…")
        run(["demucs", "-n", MODEL, "--shifts", str(args.shifts),
             "-o", str(tmp), str(src)])
        stems = tmp / MODEL / src.stem

        # Reference must be decoded straight from the ORIGINAL file. Decoding a
        # re-encoded intermediate introduces an MP3 encoder delay (~1105
        # samples) that silently wrecks the subtraction.
        print("[2/3] decoding reference channel…")
        ref_wav = tmp / "ref.wav"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
             "-af", f"pan=mono|c0=c{chan}", "-c:a", "pcm_s16le", str(ref_wav)])

        ref = read_wav(ref_wav)
        sax = read_wav(stems / "other.wav", chan)
        n = min(len(ref), len(sax))
        ref, sax = ref[:n], sax[:n]

        # Subtract ONLY the sax estimate from the untouched original, rather
        # than rebuilding from the remaining stems. Everything the model did
        # not label as sax then survives bit-for-bit, including the model's
        # own reconstruction error.
        result = ref - sax

        # Quality check. With a correct alignment and a clean separation the
        # energy-minimising gain lands near 1.0; far from it means the sax
        # estimate does not match what is really in the mix.
        gain = float(np.dot(ref, sax) / np.dot(sax, sax))
        print(f"      optimal gain {gain:.3f} "
              f"({'OK' if 0.9 < gain < 1.15 else 'SUSPECT — check alignment'})")
        print(f"      original {db(ref):.1f} dB -> result {db(result):.1f} dB")

        print("[3/3] encoding…")
        out_wav = tmp / "out.wav"
        write_wav(out_wav, result)
        out = outdir / f"{src.stem}_Part{args.part}_NOSAX.mp3"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out_wav),
             "-q:a", "2", str(out)])
        print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
