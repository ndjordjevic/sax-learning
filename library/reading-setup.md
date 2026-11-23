# Reading setup: iPad + MobileSheets + TV + pedal

How I read sheet music while playing. Researched 2026-11-23: [report](../reports/Sheet%20music%20reading%20setups.md), raw notes in `research_notes/Sheet music reading setups/`.

## MobileSheets docs
- **iOS manual (PDF, 195 pp):** https://www.zubersoft.download/manuals/MobileSheetsiOS.pdf
- Site and forum (developer answers questions): https://www.zubersoft.com/mobilesheets/
- Useful chapters: display modes and page scaling (song display), cropping files (song editor), Touch & Pedal Settings, Display Settings.

## What works (tested 2026-11-23)
- **Reading Jazz duets (A4 scans, 4 systems per page):** crop the margins (song editor → cropping → *Auto-Crop All Pages*; *Aggressively Crop* for scans), **Single Page** display in landscape, and the pedal. Two-page view made them too small, even on the TV.
- **Half pages:** Settings → Display → *Display Half Page in Landscape* and *Half-Page Turns in Landscape*, to fill the full width. The half-page position icon (bottom left) sets where each half ends. Set per song with "Use default display for song" unticked.
- **One-page lead sheets (557):** two-page view is fine.
- **TV:** iPad mirrored over HDMI (USB-C to HDMI is lower-lag than AirPlay). It shows exactly what the iPad shows, so layout fixes happen in MobileSheets.
- **Pedal: iRig BlueTurn.**
  - Pair within about 30 s of switching on: iPad Settings → Bluetooth open, blue light blinking, tap "iRig BlueTurn". Hold left pedal while switching on = mode 1 (up/down arrows), right pedal = mode 2 (Page Up/Down). Mode 3 = left/right arrows.
  - In MobileSheets: Settings → Touch & Pedal Settings → Pedal Actions → Keys (press the pedal) → *Go to Next Page* / *Go to Previous Page*. The mode doesn't matter.
  - If pages don't turn: switch mode and re-pair; if erratic, turn off iPadOS Settings → Accessibility → Keyboard → Full Keyboard Access.
  - The BlueTurn is a keyboard, so the on-screen keyboard won't appear; hold the left pedal 3 s to bring it back.

## Not worth it (from the research)
forScore (no feature gap), Newzik/BandHelper subscriptions, e-ink readers, dual-screen readers, a bigger iPad. No reader app transposes a PDF: make Bb versions in MuseScore.

## Ideas, not done
- A CSV index for the 557 (title, page; named exactly like the PDF) so MobileSheets splits the book into songs. No public index exists.
- Group the C page and my Bb copy of a tune as one song.
- A tablet clamp for a mic stand (K&M 19790, check it fits a thin iPad).
