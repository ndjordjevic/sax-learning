# 🎧 Audio Processing Methodology — Reading Jazz play-along tracks

*How the practice audio in `extracted-audio/` was produced. Written 2026-08-06.*

Two separate jobs are documented here:

1. **Channel splitting** — turn a stereo duet track into two mono files, one per sax part.
2. **Sax removal** — strip the sax off a part, leaving a rhythm-section-only backing track.

---

## Background: how the Reading Jazz CD is mixed

Per the book's Introduction ("Practice Both Parts"):

| | Content |
|---|---|
| **Left channel** | Sax **Part I** + rhythm section |
| **Right channel** | Sax **Part II** + rhythm section |
| **Rhythm section** | on **both** channels |

The book's intended workflow is to kill one channel with the balance knob and play that
part yourself. That fails on a **mono Bluetooth speaker**, which sums both channels back
together — hence the processing below.

---

## Job 1 — Split the channels (simple, lossless-ish, no AI)

Pure channel selection with ffmpeg's `pan` filter. Fast and exact.

```bash
SRC="02_First_Time.mp3"

# Part I  (left channel)  = sax I  + rhythm
ffmpeg -y -i "$SRC" -af "pan=mono|c0=c0" -q:a 2 "02_First_Time_PartI_left.mp3"

# Part II (right channel) = sax II + rhythm
ffmpeg -y -i "$SRC" -af "pan=mono|c0=c1" -q:a 2 "02_First_Time_PartII_right.mp3"
```

`pan=mono|c0=c0` means "output one channel, take it from input channel 0". Each result
is **one sax part plus the full rhythm section** — exactly what the book asks you to
practise against.

---

## Job 2 — Remove the sax (AI source separation)

**Use the script:** [`tools/remove_sax.py`](tools/remove_sax.py)

```bash
source .venv-demucs/bin/activate
python3 tools/remove_sax.py "/path/to/06_The_Smoothie.mp3" --part I --outdir extracted-audio
```

### Setup (one time)

```bash
python3 -m venv .venv-demucs
source .venv-demucs/bin/activate
pip install demucs numpy      # numpy is NOT pulled in automatically — install it explicitly
```

[Demucs](https://github.com/adefossez/demucs) is Meta AI Research's open-source music
source-separation model. It runs locally on CPU; a 1-minute track takes well under a
minute even with shift-averaging.

### The four decisions that make this work

Each of these was arrived at by a failed attempt first.

#### 1. Do NOT use the `vocals` stem — use the 6-stem model and take `other`

The obvious move is `--two-stems=vocals`, expecting the sax to count as the "lead voice".
**It does not work.** Demucs' vocal model is trained on the human singing voice and does
not recognise saxophone at all. The measured result:

```
vocals stem     mean_volume: -46.0 dB   <- essentially silent
no_vocals stem  mean_volume: -27.4 dB   <- the sax stayed in here
```

The output was just the full mix handed back.

**Fix:** use the 6-stem model `htdemucs_6s`, which adds dedicated `piano` and `guitar`
stems. With piano pulled out separately, the sax is left alone in the catch-all `other`
stem. Energy per stem for Duet 1, which identifies what is where:

| Stem | Level | What it actually is |
|---|---|---|
| `other` | **-30.4 dB** | **the saxophone** |
| `bass` | -32.8 dB | walking bass |
| `piano` | -37.7 dB | comping piano |
| `drums` | -42.4 dB | drums |
| `vocals` | -46.0 dB | *(empty)* |
| `guitar` | -84.3 dB | *(empty — no guitar in this mix)* |

Always check these levels on a new album before trusting the stem assignment:

```bash
for f in *.wav; do printf "%-12s " "$f"; \
  ffmpeg -hide_banner -i "$f" -af volumedetect -f null - 2>&1 | grep mean_volume; done
```

#### 2. Feed Demucs the ORIGINAL STEREO file, not a pre-split mono channel

Demucs leans heavily on stereo panning to tell instruments apart. On this CD the saxes
are hard-panned and the rhythm section is centred — a very strong separation cue. Splitting
to mono *first* throws that information away and separates worse.

So: separate the stereo original → then take the **left channel of the `other` stem** as
the Part I sax estimate.

#### 3. Subtract the sax from the original — don't rebuild from the other stems

Two ways to get "everything except the sax":

- **Rebuild:** sum `bass + drums + piano + guitar + vocals`.
- **Subtract:** take the **untouched original** and subtract only the `other` stem.

**Subtraction is better.** Demucs stems do not sum back to exactly the input — there is
always reconstruction error. Rebuilding discards that error along with anything the model
misfiled; subtracting keeps every part of the original that was not labelled sax,
bit-for-bit. (Measured difference between the two methods: −44.6 dB — audible detail, not
nothing.)

```python
result = original_left_channel - sax_stem_left_channel
```

#### 4. Beware the MP3 decoder-delay trap when measuring

⚠️ **This one caused a false "the separation is bad" conclusion.**

Decoding a *re-encoded* intermediate MP3 introduces an encoder delay — measured here as
**1105 samples** (~25 ms) versus the original. Any subtraction against a misaligned
reference *adds* signal instead of cancelling it, making a good separation look broken:

```
mean_volume BEFORE alignment fix: -23.0 dB   <- LOUDER than the -27.3 dB original
```

**Fix:** always decode the reference straight from the **original** file, never from an
intermediate you produced earlier. Do that and the offset is 0 and no alignment step is
needed at all.

### Verifying the result numerically

Compute the energy-minimising gain for the subtraction:

```python
gain = np.dot(ref, sax) / np.dot(sax, sax)
```

- **gain ≈ 1.0** → alignment is right and the sax estimate matches what is really in the
  mix. Measured **1.02–1.05** on these tracks. ✅
- **gain far from 1.0** (e.g. 0.73) → misalignment or a poor separation. Investigate
  before trusting the output; in this project every such case turned out to be the
  decoder-delay trap above, not a bad separation.

`remove_sax.py` prints this automatically and flags anything outside 0.9–1.15.

---

## Results archive

Everything lands in `extracted-audio/`:

| Suffix | Contents |
|---|---|
| `_PartI_left.mp3` | sax Part I + rhythm |
| `_PartII_right.mp3` | sax Part II + rhythm |
| `_PartI_NOSAX.mp3` | rhythm section only (sax removed, subtraction method) |

Done: **all 30 duets** (Duets 1–6 on 2026-08-06, Duets 7–30 on 2026-11-01) fully processed — channel-split *and* sax-removed. Nothing left to run; the runbook below is for regenerating `extracted-audio/` on a new machine.

**pCloud archive status:** all 30 duets archived (3 files each, byte-verified with `cmp`, 2026-11-01).

Measured optimal gain per track (all comfortably in the healthy 0.9–1.15 band):

| Duet | Track | Gain |
|---|---|---|
| 1 | First Time | 1.025 |
| 2 | The Smoothie | 1.050 |
| 3 | Daht's Dah Vay | 1.054 |
| 4 | Pop It! | 1.018 |
| 5 | Slip 'N Slide | 1.035 |
| 6 | One More Time | 1.045 |
| 7 | Same Lick – Different Look | 1.041 |
| 8 | Skippin' | 1.048 |
| 9 | Two Short – Not Too Short | 1.047 |
| 10 | The Frondescence of Fall | 1.029 |
| 11 | A Little Minor Blooze | 1.055 |
| 12 | A Ol' Ian | 1.057 |
| 13 | Restin' Fore and Aft | 1.044 |
| 14 | Say It Again Virginia D. | 1.054 |
| 15 | Two Brothers | 1.039 |
| 16 | Two Others | 1.049 |
| 17 | Cha-Da | 1.046 |
| 18 | Bleu Skies | 1.086 |
| 19 | Just for Jack | 1.048 |
| 20 | Egual Octavo | 1.073 |
| 21 | Bright Eyes | 1.053 |
| 22 | Barbara's Blues | 1.046 |
| 23 | Jersey's Bounce | 1.034 |
| 24 | Kickin' It Around | 1.060 |
| 25 | Charlie Jack | 1.047 |
| 26 | September's Song | 1.034 |
| 27 | Sippimissi Mud | 1.052 |
| 28 | Melody for Michelle | 1.034 |
| 29 | Lull-A-Byin' Rhythm | 1.031 |
| 30 | Triplication | 1.039 |

Only the **Part I (left)** channel is sax-removed, and that is sufficient: left minus Sax I
and right minus Sax II both yield the same thing — the rhythm section, which sits on both
channels. One `_PartI_NOSAX` file per duet is the backing track for *either* part.

Two extra files that are deliberate keeps, not strays:
- `02_First_Time_PartI_NOSAX_stems-method.mp3` — the rebuild-from-stems alternative, kept
  as an A/B reference against the canonical subtraction version.
- `02_First_Time_PartI_left_no_wind_split_by_lalalai.mp3` — produced separately with
  [lalal.ai](https://lalal.ai), not by this pipeline.

**Intermediates are disposable.** `remove_sax.py` writes its stems to a temp dir that is
deleted automatically, so nothing needs cleaning up after a run. Earlier manual
experiments left ~230 MB of stem WAVs behind; those were removed and are fully
regenerable by re-running the script. The one thing to keep is `.venv-demucs/` (~730 MB) —
delete it and you just reinstall per the setup step above.

---

## Processing more duets (runbook — e.g. Duets 7–30)

`extracted-audio/` is git-ignored, so on a fresh machine it won't exist. Everything needed
to regenerate it is here plus `tools/remove_sax.py`.

### Source files

The original stereo CD rips live in the user's pCloud library:

```
<pCloud Drive>/iCloud-Migration/MyBookLive/Sax/2 Jazz Methods & Etudes/Reading Jazz - Tenor Sax - Jacques Rizzo (Alfred, 1996)/Audio/
```

On the original Mac `<pCloud Drive>` is `/Users/nenaddjordjevic/pCloud Drive`; on another
machine, find the mount first (on the Linux box it is `~/pCloudDrive`). The folder holds 79 tracks (`01_…` to `79_…`), and that
same folder is also where the processed output is archived (see step 4).

### Which tracks to process

Only the **duet tune itself**, never the `Preliminary_Exercise` tracks. Each duet's tune is
the last track of its group, the one that is *not* a preliminary exercise:

- Duet 1 → `02_First_Time` and Duet 2 → `06_The_Smoothie`. These two carry **no**
  `Duet_N` prefix, so a name-based filter misses them.
- Duets 3–30 → `NN_Duet_N_-_<Title>.mp3` without `Preliminary_Exercise` in the name.

List the duet tunes, excluding outputs you've already made:

```bash
SRC_DIR=".../2 Jazz Methods & Etudes/Reading Jazz - Tenor Sax - Jacques Rizzo (Alfred, 1996)/Audio"
ls "$SRC_DIR" | grep -v Preliminary_Exercise | grep -vE '_Part(I|II)_' 
```

Duets 7–30 are tracks `21, 24, 27, 31, 34, 37, 40, 44, 46, 49, 52, 54, 56, 58, 60, 62,
64, 66, 69, 71, 73, 75, 77, 79`.

### Setup on a new machine (one time)

```bash
brew install ffmpeg                 # provides ffmpeg + ffprobe
python3 -m venv .venv-demucs        # built with Python 3.14, demucs 4.1.0, torch 2.13
source .venv-demucs/bin/activate
pip install demucs numpy
```

The first Demucs run downloads the `htdemucs_6s` weights, so it needs internet access.

### Steps per duet

```bash
source .venv-demucs/bin/activate
mkdir -p extracted-audio
for f in "$SRC_DIR"/21_*.mp3 ...; do            # the duet-tune tracks only
  b=$(basename "$f" .mp3)
  # copy the source locally first: reading heavily off the pCloud mount can wedge it
  cp "$f" /tmp/"$b.mp3"
  ffmpeg -y -loglevel error -i /tmp/"$b.mp3" -af "pan=mono|c0=c0" -q:a 2 extracted-audio/"${b}_PartI_left.mp3"
  ffmpeg -y -loglevel error -i /tmp/"$b.mp3" -af "pan=mono|c0=c1" -q:a 2 extracted-audio/"${b}_PartII_right.mp3"
  python3 tools/remove_sax.py /tmp/"$b.mp3" --part I --outdir extracted-audio
done
```

1. **Split** each tune into `_PartI_left` and `_PartII_right` (Job 1).
2. **Remove the sax** with `remove_sax.py --part I` → `_PartI_NOSAX` (Job 2). Feed it the
   original stereo file, never a split output.
3. **Check the gain** it prints. It should be 0.9–1.15; anything flagged `SUSPECT` must be
   investigated (see decision 4) before it's archived. If a later duet sounds like it has
   different instrumentation, check the stem levels as described in decision 1.
4. **Archive to pCloud.** Copy the three outputs per duet into the same
   `.../Reading Jazz - Tenor Sax - Jacques Rizzo (Alfred, 1996)/Audio` folder, then verify each with `cmp`. `ls` the
   folder first to make sure the mount responds, and don't retry in a loop if it's hung.
5. **Record progress.** Update "Done so far" and add each duet's gain to the table in the
   Results archive above, then commit this doc.

> Practice note: the sax-removed tracks are for *after* you can play the part. Rizzo's own
> sequence is chant → play along **with** the recorded part → then play it against the other
> part. A rhythm-only track is the final stage, and doubles as a plain backing track.
