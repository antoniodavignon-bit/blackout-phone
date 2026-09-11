# Engineering log

Newest first. Written as the build happens, including the parts that did not work.

---

## 2026-09-11 — The library is fine; the door is broken

Tested whether the offline library could answer questions in plain words.
Measured against the real chemistry ZIM pulled off the card in 20 MB pieces
and MD5-verified after reassembly.

### Three findings, in order of how much they changed the plan

**The ZIMs already carry a full-text index.** `has_fulltext_index: True`.
Xapian, inside the archive, answering in 1-12 ms. There was never a search
index to build — it has been on the card since Phase 04.

**Generating answers over the library is impossible, not merely slow.** Plain
text comes out at 5.68x the ZIM size: the 18 GiB library is ~104 GB of text
across more than a million articles. At five seconds of generation apiece
that is 58 days. 104 GB also fits neither the card nor the Mac.

**Then the finding that mattered.** The index is excellent, and unusable:

```
"how do I make drinking water safe" -> PFAS timeline, Bleach, Lead abatement
"water chlorination"                -> Water chlorination, Shock chlorination
```

Same intent. One works. Lexical search demands you already know the term,
which is exactly what you do not have in an emergency.

### So the model translates instead of answering

Build the door, not the building. On the Mac, once: rewrite a plain question
into expert vocabulary, let the ZIM's own index retrieve the article, write
three sentences from that article's text. Ship the table.

Bounded by questions asked — thousands — rather than articles stored —
millions. Measured at 4,915 bytes per question, so 20,000 questions is 98 MB
against 70 GB free. The phone runs no model. Lookup is 0.2 ms.

Prompt processing at 6.1 tok/s is not an obstacle to route around. It is the
number that says inference belongs on the other machine.

### And the test caught my own bug

The first `ask` reduced a question to FTS terms with `paste -sd' OR '`. That
produced:

```
how makeOdrinkingRwater safe
```

`paste -d` takes a *list of cycling delimiters*, not a string — space, O, R,
space. It would have degraded search quietly rather than failing, on a
command meant for emergencies. Caught because the output was printed and read
rather than assumed to work.

### Still unproven

`sqlite3` with FTS5 on armv7l Termux — the fifth ABI coin-flip, and `ask`'s
only dependency. And the real question: whether a generated bank actually
beats well-phrased Kiwix search. Twenty questions, both ways, then decide.
If the bank loses, the answer is a printed vocabulary card, and that write-up
is worth the same as the other one.

---

## 2026-09-10 — The backup that was not there

Before starting the 48-hour trial, a check on what a card failure would actually
cost.

```
$ find ~/Downloads -iname '*.zim' | wc -l
0
```

Eighteen gigabytes of curated offline reference — the reason this device exists
— had exactly one copy, on a consumer FAT32 card with no journal, about to spend
two days in a pocket getting power-cycled.

ADR-003 has said since the day it was written that *"the Mac is the master copy
of all library content. Card failure costs a re-copy, not data."* Every ZIM had
been downloaded, verified, moved to the card, and deleted from the Mac. The
sentence was an intention that got recorded as a fact, and it read as
reassurance for two days while the opposite was true.

The maps were genuinely fine — 29.6 GB of masters still in `~/Downloads/osm`.
The GGUF was fine. The library was not.

### The planned fix did not survive contact with the disk

The backlog said `dd` the card. 128 GB card, 118 GB image, 56 GB free on the
Mac. It does not fit — and compression buys nothing, because ZIMs and `.obf`
files are already compressed. Worse, landing near-full is the exact condition
that silently truncated five archives in Phase 04.

So: file-level backup of what exists nowhere else, skipping the duplicated.
19 GB, verified 18/18 by size and 3 by content hash at head, middle and tail,
with the non-empty guard that the New York incident earned. Mac sits at 38 GB
free.

### Manifests written

`MAPS.manifest`, `MAPS.sizes` and `ZIMS.sizes` now live in `Reference/`, which
Termux can read. `status` on the phone reports 84 maps as a recorded fact rather
than pretending to count what Android 11 hides from it.

### The rule

A backup claim is a measurement, not an intention. This one sat in an ADR for
two days, in good faith, being false. Check it or do not write it down.

---

## 2026-09-10 — Four rounds lost to a trailing slash that was not there

`vs` and `status` were rewritten, pushed, and installed. Three times the output
came back identical to before the fix. The push reported success. The installer
listed four files installed. Nothing had changed.

`adb push scripts /sdcard/blackout-scripts` creates the destination and fills it
on the first run. On every run after, the destination exists, so adb copies the
*directory* into it — `/sdcard/blackout-scripts/scripts/`. The stale files sit
untouched at the top level, which is exactly where `install.sh` was reading from.

Every individual step was succeeding and reporting honestly. The composition was
wrong, and nothing in either message could reveal that.

The tell was the count: `6 files pushed` became `7 files pushed` when
`mac/card-manifest.sh` was added, proving the new set had crossed the cable while
the installed behaviour stayed old. Two facts that cannot both be true unless the
files landed somewhere nobody was looking.

**Fix:** wipe the destination before pushing, or push `scripts/.` rather than
`scripts`. `install.sh` now warns when it finds a nested copy beside itself.

Third entry in this log where the failure was a report rather than a system —
a truncated ZIM that opens with a real title, a content check that passed on a
file that did not exist, and now two accurate messages that combine into a lie.
Verifying a step is not the same as verifying the step did what you wanted.

### And it works

```
kjv-bible.txt  (606 matches)
    … 603 more
CATALOG.md  (3 matches)
    20:**First aid and injuries**
```

606 matches summarised in four lines, the vault hit on top, and the catalog
surfacing something worth reading.

---

## 2026-09-10 — The phone cannot see its own maps

Scripts installed and running on the device. `status` came back with
`FAIL maps directory missing` while the card was plainly mounted — 69 GB free,
18 ZIMs found, CATALOG.md found — and while OsmAnd itself was listing all 83
regions without complaint.

```
$ ls /storage/0CEC-1F1B/Android/data/
ls: cannot open directory: Permission denied
```

Android 11 special-cases `Android/data` above the unix permission bits. No app
reads another app's directory there. ADR-003's first amendment established that
Termux can write anywhere on the card, and that finding was correct — it just
has an exception nobody hit until the maps landed inside one.

**Fifth consequence of this device's platform**, after four from the 32-bit
userspace. Different root cause, same discipline: check the constraint before
believing the plan.

### The fix is to stop pretending

`status` no longer counts maps. It reads `MAPS.manifest` — written from the Mac
by `scripts/mac/card-manifest.sh`, into `Reference/`, which sits outside
`Android/` and is readable — and reports it as a record, with the reason it is
only a record printed on the same line.

A health check that appears to verify what it cannot see is the New York file
again: a green result that means nothing. Better to print `NOTE` and the reason
than `OK` and a lie.

The manifest also opens backlog P0.3 — per-file sizes catch truncation now,
`--checksums` catches bit rot once there is a committed baseline.

### `vs` drowned in Genesis

Searching `first` returned forty lines of the KJV and buried the one vault hit
underneath. Reference files now report a match count with three sample lines,
sorted by count, cut to 100 characters so nothing wraps on a 2.8″ screen. The
vault still prints in full — there is never much of it, and it is the part you
wrote.

---

## 2026-09-10 — Phase 05 opens by deleting a feature

The daily interface is four commands: `cap`, `vs`, `status`, `home`. All four
are committed to `scripts/`, and all four were run end to end before commit —
usage errors, hits, misses, missing config, missing card — not just
syntax-checked.

### `ask` is gone

Phase 03 measured 0.6 tok/s and the earlier text left the model a job anyway:
tightening a sentence, generating variations, summarizing a paragraph. Every
one of those emits enough tokens to take a minute or more. At 1.7 seconds per
token there is no prompt worth writing.

So the model comes out of the loop rather than getting worked around. llama.cpp
stays compiled, the two `armv7l` patches stay documented, and the negative
result becomes the deliverable: a Snapdragon 215 with 2 GB of RAM will not carry
on-device generation. That is worth more written down than designed around.

Four fast commands beat three fast commands and one that makes you wait.

### `status` exists because the library is now worth checking

48 GB across two apps and a card with no journal. `status` reads free space,
counts maps and ZIMs against expected, reports the capture total and the
battery, and degrades to warnings instead of crashing when the card is absent.
Five seconds, no network, before you rely on the thing.

### Trial criteria written before the trial

The 48-hour scorecard is in the phase doc with the bars filled in and the
failure conditions named in advance — battery hours, capture count, other-phone
pickups, and a reach-fail log written in the moment. A trial with no criteria
produces a feeling, and a phase doc cannot be written from a feeling.

---

## 2026-09-09 — Maps: 83 regions, and a test that passed on nothing

83 US OsmAnd regions on the card, 29.57 GiB, 83/83 verified by size and 7 by
content hash. The device now has offline reference and offline navigation.

### The destination directory was a coin flip

OsmAnd's data folder on the card is `Android/data/net.osmand.plus/files/`.
Not `net.osmand`. The package suffix depends on which build is installed, and
guessing wrong means 83 files that occupy 29 GB and never appear in the app.
Listing `Android/data/*osmand*` takes one second and removes the guess.

### OsmAnd renames what it installs

Downloads are `_2.obf`; installed maps are not. Virginia had already migrated
to the card under the stripped name and matched the Mac's `_2` copy byte for
byte at head, middle and tail — the naming convention proved from evidence
already on the device rather than assumed.

### The test lied before the data could

A content spot-check reported `CONTENT-MATCH` on a New York file that does not
exist under that name — New York is five separate regions. Both sides hashed
to `d41d8cd98f00b204e9800998ecf8427e`, the MD5 of empty input.

Phase 04 established that a truncated archive opens and shows a real title.
This is the same failure one level up: a verification that runs on nothing
reports success. Assert non-empty inputs before comparing, or the check is
decoration.

### Backlog opened

`docs/backlog.md` — card imaging and integrity manifests, the missing SRTM
contour data, adb debloat, and the open question of whether a 0.6 tok/s model
earns its slot at all.

---

## 2026-09-09 — Phase 04: 18 archives, and three ways a library can quietly lie to you

The device now carries 18 GB of offline reference. Searching "water purification"
in Appropedia returns results with the radios off. That is the capability the
whole build exists for — not the language model.

### Kiwix would not install, and it was the architecture again

The mainline F-Droid package `org.kiwix.kiwixmobile` returns 404 and current
Kiwix builds target arm64. On a 32-bit armv7l userspace the app simply reads as
unavailable — no useful error, just absent.

The IzzyOnDroid repo carries `org.kiwix.kiwixmobile.standalone` 3.14.1 built for
**armeabi-v7a exclusively**. That installs and runs fine.

**Fourth consequence of the 32-bit userspace**, after the llama.cpp intrinsic
collision, the test suite that will not compile, and the model-size ceiling.
When an Android app is "unavailable" on this device, check the ABI before
anything else.

### Silent truncation is the real hazard of an offline library

Five ZIMs downloaded short. `mdwiki` stopped at 96 KB. `wikibooks` stopped at
1.8 GB of 3.3. Appropedia arrived at 225,828,864 bytes against a true size of
581,641,351 — **39% of the file**.

Every one of them is a structurally valid ZIM. They open in Kiwix. They show a
title and a description. They are simply missing most of their content, and
nothing in the interface says so.

For a device whose entire purpose is being trusted when nothing else works,
that is the worst possible failure mode: it fails silently, and it fails at the
moment you need it.

**Verify every archive against the server before trusting it:**

```
R=$(curl -sIL "$URL" | grep -i '^content-length:' | tail -1 | awk '{print $2}' | tr -d '\r')
L=$(stat -f%z "$f")
[ "$L" = "$R" ] && echo OK || echo "MISMATCH $f local=$L remote=$R"
```

Appropedia would have shipped at 39% complete without that check — and it is
the water-treatment and food-storage archive.

### Root cause: the build host ran out of disk

The truncations were not network failures. macOS reported
`No space left on device`, and curl kept going, writing partial files.

The build host had **118 MiB free on a 228 GB drive**. Investigating it found
79 GB in `~/git-backup-home-20260829` — a bare git repository created when
`git init` was run in the home directory instead of a project folder. Two
commits, "Initial commit" and "Add all life OS files," which faithfully stored
16 GB of Ollama model weights, 20 GB of `~/Library`, and every cache on the
machine as git objects.

Before deleting it: `ls-tree` showed it also held `Desktop/life-os/` — product
PRD, sales copy, architecture and vision documents that existed nowhere else.
Extracted with `git archive` first, then the blob was removed. **89 GB
recovered.**

The lesson is not about git. It is that **an offline device is only as
trustworthy as the machine that loaded it**, and a full disk corrupts a library
silently.

### The library

18 archives, 18 GB, every file under the FAT32 4 GB ceiling.

| Category | Contents |
|---|---|
| Survival | TruePrepper 1.3 G, Appropedia 555 M, Wikibooks 3.3 G |
| Medical | MDWiki 2.1 G, WikEM 357 M, Wikipedia Medicine 155 M |
| Nature | Wikispecies 3.2 G |
| Reference | Wikipedia Simple English 937 M, Top 100 318 M, World Factbook 388 M, plus Geography, Computer, History, Maths, Physics, Chemistry, Climate, Sociology |
| Scripture | KJV plain text 4 MB, AndBible app |

Topic packs come in `maxi` (with images) well under 4 GB, so the earlier
assumption that FAT32 forced text-only archives was wrong. Only the
whole-of-Wikipedia builds are out of reach.

### Kiwix does not file anything

It reads titles and descriptions from ZIM metadata and shows one flat list. No
folders, no tags, no reordering. With 18 archives that is workable but not good.

Written `Reference/CATALOG.md` as the index the app does not provide: a
"where do I look for X" table pointing each need — water, foraging, first aid,
navigation, scripture — at the specific archive that answers it, plus an honest
list of what the device cannot do.

**The gap worth stating plainly: there is no usable offline plant
identification.** Wikispecies is taxonomy, not edibility, and every plant-ID app
does recognition in the cloud. The answer is a paper field guide.

---

## 2026-09-08 — Phase 03: it runs, at 0.6 tokens per second

A language model is running on the flip phone, offline.

```
$ llama-cli -m ~/models/qwen2.5-0.5b-instruct-q4_k_m.gguf -c 1024 -t 4 \
    --no-display-prompt -p "Say hello in five words."

build : b10867-f3f1a8f27
model : qwen2.5-0.5b-instruct-q4_k_m.gguf
ftype : Q4_K - Medium

> Say hello in five words.
Hello!

[ Prompt: 6.1 t/s | Generation: 0.6 t/s ]
```

**0.6 tokens/second generation, 6.1 t/s prompt.** No published figure for
llama.cpp on a Snapdragon 215 existed to compare against, which is why
[ADR-002](decisions/ADR-002-model-ceiling.md) shipped with the number blank
rather than estimated. Now it is measured.

**What 0.6 t/s actually means.** About 1.7 seconds per token. A 30-token reply
takes ~50 seconds. A 200-token reply takes over five minutes. Prompt processing
runs ten times faster than generation, so reading is cheap and writing is the
wall.

That is slower than the low-single-digits ADR-002 anticipated, and it changes
the honest description of this capability. **The on-device model is not a
conversational tool and should not be described as one.** It is usable where the
output is genuinely tiny — one rewritten sentence, a few words, a yes/no
classification. Past that it is faster to write by hand. The Kiwix library, not
the model, is what makes this device useful offline.

Recording the disappointing number is the point. A repo that claimed
"on-device AI" without it would be marketing.

### Getting there took two source patches

**1. `vcvtnq_s32_f32` redefinition.** llama.cpp defines a scalar fallback for
this intrinsic on 32-bit ARM; clang 21 now provides it natively. Redefinition
error, build dead at 5%. Patched locally by `#if 0`-ing llama.cpp's version and
letting clang's win — which is also faster, being the real instruction rather
than four `roundf` calls.

**2. The test suite does not compile on 32-bit.** `tests/test-opt.cpp:101`
narrows `int64_t` to `size_t` in an initializer list. Fine where `size_t` is 64
bits; a hard C++11 error where it is 32. Not patched — the fix is to stop
building tests:

```
cmake --build build --config Release -j 2 --target llama-cli llama-bench
```

**That target line is the useful takeaway for anyone repeating this.** `--target
all` cannot succeed on armv7l against current llama.cpp. Building only what you
need sidesteps the entire test-suite problem and is much faster besides.

Both failures share one root cause: **this device runs a 32-bit armv7l
userspace on 64-bit ARMv8-A silicon**, because Android Go ships that way.
`hardware.md` said arm64 until `uname -m` said otherwise — taken from the
chipset spec rather than the device, and wrong for a plausible-sounding reason.
Corrected. Almost nobody compiles llama.cpp on 32-bit ARM in 2026, so these
paths sit unexercised upstream.

### Thread count: measured, and the tidy answer was wrong

Eight runs, same prompt, same 20-token cap, model on the card:

| Threads | Prompt t/s | Generation t/s |
|---|---|---|
| 4 | 6.1 | 0.6 |
| 4 | 5.9 | 0.6 |
| 4 | 6.1 | 0.6 |
| 4 | 6.2 | 0.6 |
| 4 | 6.2 | **0.7** |
| 2 | 3.6 | 0.7 |
| 2 | 3.6 | 0.7 |
| 2 | 3.6 | 0.7 |

After the first `-t 2` run returned 0.7 against a `-t 4` baseline pinned at 0.6,
the obvious conclusion was that generation is memory-bandwidth bound and fewer
threads wins. Three confirming runs seemed to settle it.

Then a fifth `-t 4` run also produced 0.7, which breaks the story. llama.cpp
reports one decimal place, so 0.64 and 0.68 round to different displayed values
while differing by ~6%. Two threads is modestly faster at generation; it is not
17% faster.

**Decision: `-t 4` stays the default.** The generation gain is inside rounding
error. The prompt-processing penalty — 6.1 → 3.6, a 41% loss — is unambiguous.
Trading a certain large loss for a marginal uncertain gain is a bad trade.

The general shape still holds and is worth knowing: **prompt processing scales
with cores (compute bound); generation barely does (memory-bandwidth bound).**
That is why halving threads nearly halves one and hardly moves the other.

### Card vs internal storage

Also measured across those runs: loading the GGUF from the microSD (5.9 t/s
prompt, 0.6 generation) versus internal storage (6.1 / 0.6). Identical within
noise. Once `mmap` has the file mapped, where it came from stops mattering —
so models live on the card, and internal storage keeps the binaries.

### Still open

`llama-bench` was not among the built targets, so these figures come from
`llama-cli`'s own reporting on a real prompt rather than a synthetic benchmark.
Arguably the more honest number, but not directly comparable to published
`llama-bench` results elsewhere.

Untested optimizations, in the order worth trying: fewer threads (`-t 2` — four
A53 cores may be memory-bandwidth bound rather than compute bound), a smaller
model (a ~270M parameter GGUF should roughly double throughput), and confirming
NEON is actually enabled in this 32-bit build rather than assumed.

---

## 2026-09-08 — The SD card is writable, and that changes the storage plan

[ADR-003](decisions/ADR-003-storage-split.md) was written from the documented Termux limitation: `termux-setup-storage` never requests SD-specific permission, so writes to the card fail. **On this device that is not true**, and measuring it beat assuming it.

```
$ readlink -f ~/storage/external-1
/storage/0CEC-1F1B/Android/data/com.termux/files

$ echo "termux wrote this" > /storage/0CEC-1F1B/Reference/tw.txt && cat …
termux wrote this

$ dd if=/dev/zero of=/storage/0CEC-1F1B/Reference/big.bin bs=1M count=200
209715200 bytes (210 MB, 200 MiB) copied, 10.7732 s, 19.5 MB/s

$ chmod +x …/t.sh && …/t.sh
bash: …/t.sh: /data/data/com.termux/files/usr/bin/bash: bad interpreter: Permission denied
```

Both things are true at once. `~/storage/external-1` really does point at the app-scoped sandbox — but the direct `/storage/0CEC-1F1B/…` path is writable anyway. The card's directories are `drwxrwx--- root everybody`, and Termux's uid is in `everybody`, so group write applies. A `touch` alone would not have proved this; writing real bytes and reading them back did.

**The real constraint turned out to be a different one.** The card is mounted `noexec`. `chmod +x` does not stick and the interpreter is refused outright. So the dividing line is not writable vs. read-only — it is **executable vs. data**.

Revised: the llama.cpp build and every binary stay on internal storage. Models are pure data and can move to the card, freeing ~500 MB each and allowing several to sit side by side instead of swapping. ADR-003 amended rather than rewritten — the original reasoning and why it was wrong are both worth keeping.

Sustained write measured at **19.5 MB/s**, which is fine for bulk content and slow enough that the Mac stays the right place to download.

Left open: whether `llama-cli` can `mmap` a GGUF from a `noexec` mount. Read-only mapping should not trip a restriction that only blocks `PROT_EXEC`, but that is reasoning, not measurement. Phase 03 settles it.

**Also this session:** every Termux mirror failed at once (25 hosts, four continents) — which is never a mirror problem. The phone had dropped Wi-Fi. Worth remembering that the USB cable carries adb and the SSH tunnel but gives the phone no internet of its own.

---

## 2026-09-08 — Phase 02 complete: it's a Linux machine now

Termux is up, the toolchain is installed, and the phone is reachable from the MacBook over SSH.

**Verified on device:**

```
$ python --version && git --version && ls ~/storage/
Python 3.14.6
git version 2.55.0
dcim  downloads  external-1  movies  music  pictures  shared
```

**The ergonomic problem, and the fix.** The first Termux session on the device made something obvious: with the on-screen keyboard up, a 2.8″ 480×640 display leaves roughly three visible lines of terminal. Typing a package install line on a T9 keypad is not a workflow.

The fix turned out to be better than a Bluetooth keyboard. Termux ships `sshd`, and `adb` can forward a TCP port over the USB cable — so no Wi-Fi IP, no network config, no exposure:

```
# phone
pkg install openssh -y && passwd && whoami && sshd

# mac
adb forward tcp:8022 tcp:8022
ssh -p 8022 u0_aXXX@localhost
```

From that point the Mac terminal *is* the phone's shell. Full keyboard, real screen, copy-paste. Every phase after this gets built from the laptop and the phone just gets carried. Written up as [ADR-005](decisions/ADR-005-ssh-over-usb.md).

**Termux ships a distant mirror.** The first `pkg upgrade` pulled every package from `mirror.iscas.ac.cn` — a Chinese mirror, from Virginia, over 2.4 GHz Wi-Fi, onto a 1.3 GHz A53. Three stacked bottlenecks, one of them free to fix:

```
termux-change-repo   # select main repo → North America group
pkg update
```

Worth doing before anything that installs at volume.

**Also learned:** `pkg upgrade` stops on dpkg conffile prompts (`*** openssl.cnf (Y/I/N/O/D/Z)`) and waits indefinitely. On a screen showing three lines this is easy to mistake for a hang. Default (Enter) is correct on a fresh system.

**Note for Phase 04:** `~/storage/external-1` appears in the Termux storage listing and points at the SD card. Whether it is writable is being tested — the documented behavior is read-only, but measuring beats assuming. *(Answered in the entry above: it is writable, and `noexec` is the real constraint.)*

---

## 2026-09-08 — Phase 01 complete: device access and the card

**Factory Reset Protection cost two days.** The device had been reset without removing its Google account, arming FRP. None of the accounts I owned were accepted.

The resolution was mundane and worth recording because the technical rabbit holes were all dead ends: a family member had used the phone and signed in with *his* Google account. FRP was asking for his, not mine. He supplied it and the device opened in thirty seconds.

Things that were **not** the answer, verified:
- Removing devices from your Google account's device list does **not** clear FRP. FRP is device-side and checks the account last signed in *on the phone*.
- The manufacturer cannot help. Bullitt Group closed January 2024; `catphones.com` no longer resolves. No firmware, no support, no unlock path.
- The carrier (a Lifeline MVNO) can reissue a SIM but has no FRP tooling — it's not the OEM.

**Design consequence:** for a device whose entire purpose is working with no network, a Google account is a liability, not a feature. Every app this build needs — Termux, Kiwix, OsmAnd — comes from F-Droid or a direct APK. So once setup is done the account comes off the device entirely. No account at reset time means FRP never arms again and the phone can be wiped and rebuilt freely for the rest of its life.

**The SD card had a previous life.** A 128 GB card that macOS refused to mount. `diskutil list` explained it:

```
/dev/disk4 (external, physical):
   0:  GUID_partition_scheme            *126.4 GB   disk4
   1:  19A710A2-B3CA-11E4-B026-10604B889DCF   16.8 MB   disk4s1
   2:  193D1EA4-B3CA-11E4-B075-10604B889DCF   126.4 GB  disk4s2
```

Those two type GUIDs are Android's `android_meta` and `android_expand` — the card had been formatted as **adoptable storage** by some previous Android device. The expand partition is dm-crypt encrypted (`aes-cbc-essiv:sha256`) with a key stored only on that phone's `/data` partition. Unreadable anywhere else, permanently.

Healthy hardware, wrong identity. Erased and rebuilt:

```
diskutil unmountDisk force /dev/disk4
sudo diskutil eraseDisk ExFAT CATSD MBRFormat /dev/disk4
```

**Then the device rejected exFAT.** The Cat S22 Flip refused to mount the exFAT card and offered to format it. exFAT support on Android is vendor-dependent and this device doesn't have it — a possibility flagged before testing, now confirmed on hardware.

Reformatted in the phone as **portable** storage (never internal — that is exactly the adoptable-storage state that made this card unreadable in the first place). Result: FAT32, mounted, 118 GB available, still fully read/write from macOS.

```
$ adb shell df -h /storage/0CEC-1F1B
Filesystem     Size  Used Avail Use% Mounted on
/dev/fuse      118G  1.0M  118G   1% /storage/0CEC-1F1B
```

The cost is a hard 4 GB per-file ceiling, which reshapes the entire library plan. See [ADR-004](decisions/ADR-004-fat32-library.md).

---

## 2026-09-07 — Scoping: what this hardware can actually do

Before writing any build steps, established what the device is and isn't.

**The temptation was to make it an AI device.** A Snapdragon 215 with 2 GB of Go-edition RAM leaves roughly a gigabyte usable. That rules out anything near a useful general model. The honest ceiling is a sub-1B quantized GGUF — Qwen2.5-0.5B-Instruct at Q4_K_M is 491 MB and fits with room for a small context window.

I could not find a published tokens-per-second figure for llama.cpp on a Snapdragon 215 and declined to invent one. Phase 03 includes a `llama-bench` step; the measured number goes in this log and sets what the model is actually used for.

**The rejected alternative** was making the phone a thin client to the Ollama stack already running on the MacBook — full 8B models from a rugged pocket device. Better output, and rejected anyway: it needs a network, and a device that needs a network to be useful is not an offline device. See [ADR-001](decisions/ADR-001-offline-first.md).

**What the hardware is genuinely good at**, once the AI ambition is right-sized: a pocket Linux terminal, an offline reference library on a 128 GB card, a rugged GPS unit with offline maps, and a capture device that survives being dropped. The model is a small utility inside that, not the headline.
