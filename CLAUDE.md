# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this directory is

This is not a software project. It's the working directory for a personal saxophone/jazz-study reference: a set of markdown files that catalog every jazz/blues sax book, method and course the user owns or has bookmarked, sorted by difficulty and cross-referenced into a study plan.

## Current skill level

The user's level and progress are recorded **only** in `README.md` ("📍 Where I am now" + its phase checklist). Read it at the start of a session. When the user reports finishing a book, module, duet, song or phase, update that tracker (and the matching line of the daily plan). Standing facts: advanced beginner on the horn, jazz study from zero; plays tenor (Bb) and alto (Eb) but **mainly practices tenor**, so prioritize Bb/tenor editions and default to tenor when a resource offers a choice.

## The files

Rule: **each fact lives in one file; the others link to it.** Don't copy a book's verdict or a tune's coverage into a second place.
- `README.md`: start page. Where I am now + phase checklist, the **daily plan** (a short 5-item list + off-the-sax + weekly band + a few notes; **keep it short**, put detail in the other files), and a file index.
- `plan/study-plan.md`: Phases 1–5, every owned resource ordered by real difficulty. Rows say only which chapters/exercises and why in that phase; the book's full verdict lives in the library. Rule: max 2–3 book streams per day. Frozen while the daily plan is on trial.
- `band/repertoire.md`: the 57 band tunes (557 page, tempo, notes, status) with one column per source: other owned fake books, Quartet, Tomplay, Hal Leonard play-alongs, MuseScore lead sheets; plus the backing-track apps. Answer "where do I find tune X" from here.
- `band/how-to-learn-a-standard.md`: the step method for a band tune, ear training, chord-tone ideas for later.
- `tunes/<tune>.md`: one file per tune being learned (progress, material, form). Add one when a tune becomes the current or next tune, and update its Status in the repertoire table.
- `library/books.md`: owned books by level with the deep-read verdicts, the Essential Elements phase map, the owned fake books, horn/key notes. `✅`/`🔍` marks as in the README legend.
- `library/courses.md`: BetterSax Foundations module by module, BetterSax Shed.
- `library/wishlist.md`: everything bookmarked but not owned (levels from publisher pages), buy ideas, Hal Leonard play-along series.

Every level/verdict for an owned resource comes from actually deep-reading the PDFs and course guides, not publisher blurbs. When adding a new book or course, do the same: read the actual PDF (`Read` tool with a `pages` range) or the course's companion PDFs before assigning a level, then add it to `library/` and, if owned, slot it into the study plan. When something is bought, move it from the wishlist to `books.md`. Prefer dispatching subagents for multi-PDF deep-reads to keep the main context lean.

## Practice-audio processing

`audio-processing-methodology.md` documents how the play-along audio in `extracted-audio/`
is made — channel-splitting duet tracks and AI sax-removal — including the four non-obvious
gotchas that each cost a failed attempt. `tools/remove_sax.py` is the reusable script
(needs the `.venv-demucs` virtualenv). `tools/key_compare.py` estimates each track's concert key
and the semitone shift between tracks (e.g. alto vs tenor play-alongs); it uses an STFT chroma
because CQT chroma gave false "same pitch" results.

Linux machine tooling (installed 2026-11-13): `ffmpeg`/`ffprobe`, `sox`, `pdftotext`/`pdftoppm`,
`tesseract`; `.venv-demucs/` holds CPU-only torch + demucs, numpy, scipy, librosa, soundfile
(rebuild: `python3 -m venv .venv-demucs && .venv-demucs/bin/pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu && .venv-demucs/bin/pip install demucs numpy scipy librosa soundfile`).
pCloud folder names may use decomposed Unicode (e.g. the `ö` in *Saxophon spielen*), so
typed paths can fail: reach those folders with a glob instead. **Read that doc before doing any new audio work**;
notably, Demucs' `vocals` stem does *not* detect saxophone, and measuring against a
re-encoded MP3 introduces a 1105-sample delay that masquerades as a bad separation.
`extracted-audio/` is git-ignored. All 30 duets are processed. All are archived in the
pCloud folder `2 Jazz Methods & Etudes/Reading Jazz - Alto and Tenor Sax - Jacques Rizzo (Alfred, 1996)/Audio/`; if a machine needs them, copy them from there. To regenerate from scratch, follow the doc's "Processing more duets" runbook.

## pCloud library

The user's book/course library lives on a pCloud Drive mount at:
`/Users/nenaddjordjevic/pCloud Drive/iCloud-Migration/MyBookLive/Sax/`
(on the Linux machine: `~/pCloudDrive/iCloud-Migration/MyBookLive/Sax/`).

Layout (reorganized 2026-11-02):
- `1 Classical Methods & Fundamentals/`, `2 Jazz Methods & Etudes/`, `3 Theory/`, `4 Video Courses/`, `5 Gear/`, `6 Fake Books/` (fake books in C/concert and Bb editions, incl. the 557 the weekly band uses, plus single-tune tenor lead sheets transposed from it, named `<Tune> - Bb Tenor Sax (from 557 Jazz Standards).pdf`).
- File/folder naming: `Title - Author (Publisher, Year).pdf`, with an extra edition tag like `- Tenor Sax` where it matters. Duplicate scans get a ` [scan 2]` suffix.
- A book that has audio gets its own folder holding the PDF plus `Audio/` (or `Audio - Tenor/` / `Audio - Alto/`).
- New downloads go into the matching category folder with the same naming. Once a zip is unpacked and its contents verified, delete the zip; don't keep archive copies.

Source books/courses to check for "anything new" live there — audit it (`ls`, then read PDFs/course guides directly) rather than assuming `library/` is complete.

These md files are **not** synced to pCloud; the GitHub repo is its only home.

The pCloud kext-based mount on this Mac is known to wedge under load: `ls` the folder first to confirm it's responsive, and if it's stale/hung, tell the user and don't retry in a loop.
