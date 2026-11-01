# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this directory is

This is not a software project. It's the working directory for a personal saxophone/jazz-study reference: a single markdown file, `jazz-blues-sax-books-analysis.md`, that catalogs every jazz/blues saxophone book, method, and course the user owns or has bookmarked, sorted by difficulty and cross-referenced into a study plan.

## Current skill level (update as the user progresses)

- Saxophone (classical fundamentals): **Rubank Elementary Method — done** (will keep revisiting 1-2 lessons as a warmup, not for progress tracking). **Saxophon spielen – mein schönstes Hobby Band 1 — done.** Phase 0 complete; **currently in Phase 1** — Reading Jazz (Rizzo) Duets 1–4 done, on Duet 5. Working all songs from *Band 2* as warmup (tenor play-along audio is in the same pCloud folder) — songs 1–5 done, on song 6. Advanced beginner on the horn.
- Jazz vocabulary: zero prior study as of this plan being written — the study plan in the md starts from absolute zero (rhythm-reading, pentatonic scale) and is phased over ~18+ months.
- Plays both tenor (Bb) and alto (Eb), but **mainly practices tenor** — prioritize Bb/tenor editions and default to tenor when a resource offers a choice.

When the user reports finishing a book, course module, or phase, update **both** this section here **and** the matching item in the md's "📍 Where I am now" progress tracker (tick the phase checkbox) so progress stays recorded in one place.

## The canonical file

`jazz-blues-sax-books-analysis.md` is the single source of truth. Structure (keep it to these parts — resist re-fragmenting it):
- **📍 Where I am now** — current level + a phase-by-phase progress-tracker checklist.
- **Chapter 1 — Study Plan** — the phased (Phase 1–5) sequence of every owned resource, ordered by real difficulty.
- **Chapter 2 — Books** — grouped by level (Beginner → Advanced), with a final "Repertoire to play" sub-list; `✅` marks owned.
- **Chapter 3 — Courses** — the BetterSax Foundations video course, module-by-module.
- **Notes on horn/key** — tenor Bb vs alto Eb guidance per title.

Every level/verdict in the file comes from actually deep-reading the PDFs and course guides, not publisher blurbs. When adding a new book or course, do the same: read the actual PDF (`Read` tool with a `pages` range) or the course's companion PDFs before assigning a level, then slot it into the right chapter/level and, if owned, the study plan. Prefer dispatching subagents for multi-PDF deep-reads to keep the main context lean.

## Practice-audio processing

`audio-processing-methodology.md` documents how the play-along audio in `extracted-audio/`
is made — channel-splitting duet tracks and AI sax-removal — including the four non-obvious
gotchas that each cost a failed attempt. `tools/remove_sax.py` is the reusable script
(needs the `.venv-demucs` virtualenv). **Read that doc before doing any new audio work**;
notably, Demucs' `vocals` stem does *not* detect saxophone, and measuring against a
re-encoded MP3 introduces a 1105-sample delay that masquerades as a bad separation.

## pCloud sync (standing instruction)

The user's book/course library lives on a pCloud Drive mount at:
`/Users/nenaddjordjevic/pCloud Drive/iCloud-Migration/MyBookLive/Sax/`

**Always sync `jazz-blues-sax-books-analysis.md` to that folder after editing it, without being asked.** Procedure:
1. `ls` the target pCloud folder first to confirm the mount is responsive.
2. `cp` the local file over (never `rm` first, no retry loops).
3. `diff -q` the two copies to verify byte-identical.
4. If the mount check fails (stale/hung), skip the sync, tell the user, and don't retry in a loop — the pCloud kext-based mount on this Mac is known to wedge under load and cannot be reasoned into working via retries.

Source books/courses to check for "anything new" live in that same pCloud folder — audit it (`ls`, then read PDFs/course guides directly) rather than assuming the md is complete.
