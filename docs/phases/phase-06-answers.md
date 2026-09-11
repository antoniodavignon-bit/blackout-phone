# Phase 06 — Answers without inference

**Status:** 📐 Designed and measured, not yet built

Goal: ask the library a question in plain words and get a usable answer, on a
device that cannot run a language model.

## The measurement that decides the architecture

Phase 03 recorded two numbers. Everyone fixates on the wrong one.

| | |
|---|---|
| Generation | 0.6 tok/s |
| **Prompt processing** | **6.1 tok/s** |

Retrieval-augmented generation means putting retrieved passages *into the
prompt*. On this device:

| Prompt size | Time to read it, before generating anything |
|---|---|
| 200 tokens — one short passage | 33 seconds |
| 2,000 tokens — five passages | **5.5 minutes** |
| 4,000 tokens — ordinary RAG context | 11 minutes |

On-device RAG is not slow here. It is impossible, and no prompt engineering
recovers an order of magnitude.

## What was measured, 2026-09-11

Tested against the real `wikipedia_en_chemistry_nopic_2026-07.zim` from the
card (MD5 verified after transfer).

### The ZIMs already contain a search index

```
articles           : 57,058
has_fulltext_index : True
'distillation'     : 593 matches in 1 ms
'sodium hypochlorite' : 120 matches in 1 ms
```

Kiwix ships a Xapian full-text index inside the archive. **There is no search
index to build.** It has been on the card since Phase 04, answering in
single-digit milliseconds.

### Generating over the whole library is impossible

| | |
|---|---|
| Plain text : ZIM size | **5.68×** |
| 18.23 GiB library as text | **~104 GB** |
| Articles, chemistry alone | 57,058 |
| Articles, full library | > 1,000,000 |
| Generation at 5 s/article | **~58 days** |

104 GB fits neither the card (70 GB free) nor the Mac (38 GB). This was not
scoped down. It was abandoned.

### The actual problem is the door, not the library

The index is excellent and unusable, depending entirely on your vocabulary:

| Asked the way a person asks | Returns |
|---|---|
| "how do I make drinking water safe" | PFAS timeline, Bleach, Lead abatement |
| "how do I store fuel safely" | radioactive waste management, Electric battery |
| "what can I use to disinfect a wound" | Antimicrobial, Bleach, Disinfectant |

| Same intent, expert vocabulary | Returns |
|---|---|
| "water chlorination" | **Water chlorination**, Chlorine-releasing compounds, Shock chlorination |
| "saponification" | **Saponification**, Saponification value, Ester hydrolysis |

Lexical search requires you to already know the term — which is exactly what
you do not have at the moment you need it.

## The design: translate, don't generate

The model's job is not to answer. It is to build the door.

```
BUILD TIME — Mac, hours, once, plugged in
  question in plain words
    → model rewrites it as expert search vocabulary
    → ZIM's own Xapian index retrieves the article       (1-12 ms)
    → model writes a 3-sentence answer FROM that article's text
    → row: question | expert_query | answer | article | zim
  → SQLite FTS5

QUERY TIME — phone, sub-millisecond, no model at all
  ask "can I drink this water"
    → FTS5 lookup
    → answer + the article it came from + the expert term
```

Bounded by **questions asked** (thousands), not **articles stored**
(millions). That is the whole trick.

### Measured cost

| Questions | Bank size |
|---|---|
| 1,000 | 4.9 MB |
| 5,000 | 24.6 MB |
| 20,000 | 98 MB |

4,915 bytes per question. Against 70 GB free, storage is not a consideration.
The cost is a few hours of Mac time, once.

### Prototype, end to end

```
ask: 'can I drink this water'   [0.2 ms]
  -> Add unscented household bleach (sodium hypochlorite). Let stand 30
     minutes; a faint chlorine smell should remain. Boiling 1 minute is
     more reliable when fuel allows.
  source: Water chlorination  (expert term: water chlorination)
  zim lookup confirms: ['Water chlorination']
```

## Why answers are written from retrieved text only

The build prompt forbids the model from answering out of its own memory, and
it must reply `NOT IN SOURCE` rather than improvise. Those rows are dropped.

Every answer carries the article it came from, so the source is one Kiwix
search away. A survival reference that confidently invents a dilution ratio is
worse than no reference. The answer is a signpost; the archive is the truth.

## Gates

| Gate | Status |
|---|---|
| ZIM text extraction on the Mac | ✅ libzim, 273 articles/sec |
| Embedded full-text index usable | ✅ present, 1-12 ms |
| Size of a generated bank | ✅ 4,915 bytes/question |
| Natural-language gap is real | ✅ measured, and it is large |
| `sqlite3` + FTS5 in Termux on armv7l | ⬜ **untested — fifth ABI coin-flip** |
| Answer quality vs raw Kiwix search | ⬜ needs 20 real questions, both ways |

`ask` needs only `sqlite3` on the phone — not libzim, not a model. One
dependency, one ABI risk.

## Build it

```bash
# Mac
pip install libzim
./scripts/mac/build-answerbank.py \
    --zim ~/Downloads/blackout-library/Kiwix/*.zim \
    --questions scripts/mac/questions.txt \
    --model llama3.1:8b \
    --limit 25                       # prove the loop before committing hours
```

Copy the result to `Reference/answerbank.sqlite` on the card, then on the
phone:

```bash
pkg install sqlite
ask "how do I make drinking water safe"
```

## The open question worth publishing either way

Does a generated answer bank actually beat well-phrased Kiwix search?

The honest possibility is no — that curated sources plus knowing two or three
expert terms wins, and the bank is ceremony. Build 25 answers, take 20 real
questions, run both, compare.

If the bank wins, this is a genuinely new way to put a language model on
hardware that cannot run one. If it loses, that is a finding worth the same
write-up, and the fix is a printed vocabulary card rather than a database.

Measure it before believing either.
