# Backlog

Work identified but not yet scheduled into a phase. Ordered by what would hurt most if it went unaddressed.

Nothing in this file is verified on the hardware yet. Everything in the phase docs was measured; everything here is a plan. The distinction matters — see [Unverified assumptions](#unverified-assumptions) at the bottom.

---

## P0 — The card is a single point of failure

Phase 04 put 48 GB onto one consumer microSD card formatted FAT32. That card now holds the entire value of this build, and every failure mode below has already happened to somebody:

| Failure | Why it applies here |
|---|---|
| Card death | Consumer TLC card, no wear reporting, no SMART equivalent |
| Directory corruption | FAT32 has no journal — an interrupted write can take the file table with it |
| Silent bit rot | A corrupted ZIM opens and shows a real title, same as a truncated one did in Phase 04 |
| Accidental overwrite | Card mounts read/write on any machine it touches |

### 1. Image the card

Once the library is final, `dd` the whole card to a `.img` on the Mac. A dead card becomes a 30-minute restore instead of a week of re-downloading and re-verifying.

### 2. Clone to a second card

Buy an identical Onn 128 GB, restore the image onto it, keep it out of the device. Cheap, and it makes the build handable to someone else.

### 3. Integrity manifest

Generate `SHA256SUMS` for every file on the card. Store it **on the card and in this repo**. Then integrity is checkable offline, forever, with one Termux command.

This is the Phase 04 verification lesson extended from download time to the whole life of the card. Byte-verifying at download only proves the file arrived intact. It says nothing about whether it is still intact eighteen months later.

---

## P1 — The maps have no terrain

The 83 `.obf` files are vector street data. They contain no elevation.

For the scenario this device is built for, contour lines and hillshade matter more than street names. OsmAnd ships those as **separate SRTM downloads** that Phase 04 did not pull.

- Grab contours at minimum for Virginia and any realistic destination region
- Watch the FAT32 4 GB per-file ceiling — same constraint as the ZIMs
- Hillshade and slope layers are separate again from contours

---

## P2 — Reduce what can go wrong

### Debloat over adb

```bash
adb shell pm uninstall -k --user 0 <package>
```

Google Play services, Play Store, and anything with a background sync loop. On 2 GB of RAM with roughly 1 GB usable, every removed wakelock is measurable battery and measurable responsiveness. This is the highest-leverage reliability work available and it costs nothing.

### Freeze the software

Disable automatic app and system updates entirely. A device you depend on should not change underneath you without a decision.

### Never hot-pull the card

Unmount from Android settings before removing it, every time. FAT32 has no journal; there is no recovery path from a torn directory write.

### Battery strategy

The removable 2000 mAh pack is the best feature on this hardware.

- Two or three spare packs
- An external cradle charger, so charging does not depend on the phone functioning
- A power bank that can be topped from a solar panel

### `status` — one-command health check

A Phase 05 companion to `vs` / `cap` / `home`:

```
free space on card
battery percentage
manifest spot-check (N files sampled)
model present and correct size
map count
ZIM count
```

Five seconds, no network, tells you whether the device is sound before you rely on it.

### Printed runbook

One page, on paper. If the phone is the thing that is broken, the documentation cannot live on the phone.

Contents: card restore procedure, storage paths, installed package list, the two llama.cpp `armv7l` patches, OsmAnd data directory.

---

## P3 — Capability gaps worth filling

| Addition | Why |
|---|---|
| KeePassDX | Fully offline password vault. Useful every day, not only in a blackout. |
| Wiktionary ZIM or StarDict | Real dictionary lookup — something the 0.6 tok/s model will never do acceptably |
| WikiMed ZIM | Medical reference, if not already among the 18 |
| *Where There Is No Doctor* | Field medicine, PDF |
| iFixit ZIM | Repair procedures — believed to exist in the Kiwix library, unconfirmed |
| GPS as clock | With radios off the system clock drifts. A GPS fix restores accurate time and position with no network. OsmAnd already provides this. |

---

## P4 — Resolve the model question honestly

Phase 03 measured 0.6 tok/s. That is not a conversational assistant and no amount of tuning changes the order of magnitude.

Two options, and the phase doc should commit to one:

1. **Narrow the job.** Single-label classification, one-field extraction, short structured output where the answer is ten tokens and not three hundred. Define the bounded task, measure whether it clears the bar.
2. **Cut it.** Reclaim the internal storage and the ~1 GB of RAM headroom, and record in ADR-002 that the hardware will not carry on-device generation.

An honest negative result is a better phase outcome than a documented feature that nobody would use twice.

---

## P5 — Design the blackout trial before running it

Phase 05 ends in a 48-hour trial. Write the pass/fail criteria **first**, or it produces a feeling instead of data:

- Hours of real use per battery pack
- Every task reached for and not completed, logged at the moment it failed
- Every instance of picking up the other phone, and what for
- Whether `cap` actually got used in the field, or whether triage crept back in

A phase doc written from measurements is the whole point of this repo. A trial with no criteria cannot produce one.

---

## Unverified assumptions

Called out explicitly, because this build has already been broken four separate times by the same root cause.

**The ABI.** This device runs a 32-bit `armv7l` userspace on ARMv8-A silicon. Every app named in P3 is assumed to have an `armeabi-v7a` build, and none of them have been checked. Confirm the ABI before planning around any of them.

Installing from the F-Droid **app** rather than the website is the mitigation: the app resolves the correct ABI automatically, where the website offers a default download that may be 64-bit only.

**Everything else here.** No item in this file has been run on the hardware. Items move into a phase doc only once they have been.
