# ADR-003 — Internal/SD storage split

**Status:** Accepted 2026-09-08 · **Amended 2026-09-08** after measurement · **Amended 2026-09-10** — the card-write finding has an exception, see [Second amendment](#second-amendment-2026-09-10--androiddata-is-not-included)

## Context

The device has 16 GB of internal storage and a 128 GB microSD card. The obvious plan — put everything large on the card — collides with a known Termux limitation: `termux-setup-storage` does not request the SD-card-specific permission modern Android requires, so writes to `/storage/XXXX-XXXX` fail with permission denied. This is a long-standing tracked issue, not a misconfiguration.

## Decision

Split by access pattern, not by size.

**Internal storage (16 GB)** — everything Termux needs to write:
- Termux rootfs and installed packages
- `~/models/` — the GGUF
- `~/llama.cpp/` — source and build output
- `~/storage/shared/DMG/` — capture inbox and notes vault

**microSD (128 GB)** — large read-only content, loaded from the Mac:
- `Kiwix/` — ZIM archives
- `Maps/` — offline map regions
- `Reference/` — PDFs and documents

## Rationale

Kiwix and OsmAnd read the card through Android's own storage APIs and are unaffected by the Termux limitation. Termux never needs to write there. Every file on the card arrives via `adb push` or `scp` from the Mac, which has full read/write access to the FAT32 volume.

This also means the card is disposable: it holds nothing that isn't mirrored on the Mac.

## Consequences

- Internal 16 GB must hold the toolchain, the model, and the working vault. Comfortable, but not unlimited — a second model swaps rather than accumulates.
- The Mac is the master copy of all library content. Card failure costs a re-copy, not data.
- `~/storage/external-1` appears in the Termux storage listing and points at the card; it is usable for reads.

---

## Amendment 2026-09-08 — measured on hardware

The premise above was taken from the documented Termux limitation. **On this device it is wrong**, and the correction changes what belongs where.

### What was measured

```
$ readlink -f ~/storage/external-1
/storage/0CEC-1F1B/Android/data/com.termux/files

$ echo "termux wrote this" > /storage/0CEC-1F1B/Reference/tw.txt && cat …
termux wrote this

$ dd if=/dev/zero of=/storage/0CEC-1F1B/Reference/big.bin bs=1M count=200
209715200 bytes (210 MB, 200 MiB) copied, 10.7732 s, 19.5 MB/s

$ chmod +x /storage/0CEC-1F1B/Reference/t.sh && /storage/0CEC-1F1B/Reference/t.sh
bash: …/t.sh: /data/data/com.termux/files/usr/bin/bash: bad interpreter: Permission denied
```

Three findings:

1. **Termux can write anywhere on the card**, not just its app-scoped sandbox. `~/storage/external-1` does resolve to `Android/data/com.termux/files`, but the direct `/storage/0CEC-1F1B/…` path is writable too. The card's directories are `drwxrwx--- root everybody` and Termux's uid is in `everybody`, so group write applies.
2. **Sustained write is 19.5 MB/s.** Adequate for bulk content; slow enough that the Mac remains the right place to download.
3. **The card is `noexec`.** `chmod +x` does not stick and the interpreter is refused. Nothing executable runs from it.

### Revised split

The dividing line is **executable vs. data**, not writable vs. read-only.

**Internal storage** — anything that must execute:
- Termux rootfs and packages
- `~/llama.cpp/` — source, build output, and every binary

**microSD** — data of any kind, now writable directly by Termux:
- `Kiwix/`, `Maps/`, `Reference/` — as before
- `models/` — GGUF files are pure data, read by the runtime rather than executed
- Capture and vault files, if they outgrow internal storage

### What this buys

Internal storage is 16 GB and holds a toolchain plus a build tree. Moving models to the card frees roughly 500 MB per model and allows several to sit side by side instead of swapping one in and out.

### Confirmed 2026-09-08

`llama-cli` loads a GGUF directly from the card:

```
$ cp ~/models/qwen2.5-0.5b-instruct-q4_k_m.gguf /storage/0CEC-1F1B/ \
  && llama-cli -m /storage/0CEC-1F1B/qwen2.5-0.5b-instruct-q4_k_m.gguf -c 1024 -t 4 -p "hi"

model : /storage/0CEC-1F1B/qwen2.5-0.5b-instruct-q4_k_m.gguf
ftype : Q4_K - Medium
```

Read-only `mmap` does not trip `noexec`, which only blocks `PROT_EXEC`. The
reasoning held, and now it is measured rather than assumed.

**Models live on the card.** Each one frees ~469 MiB of the 16 GB internal
storage, and several can sit side by side instead of swapping one in and out.
The executable/data split is the whole rule: binaries internal, everything else
on the card.


---

## Second amendment 2026-09-10 — `Android/data` is not included

The first amendment said Termux can write anywhere on the card, and explained
why: the directories are `drwxrwx--- root everybody` and Termux's uid is in
`everybody`. That reasoning is correct, and it is not the whole picture.

```
$ ls /storage/0CEC-1F1B/Android/data/
ls: cannot open directory '/storage/0CEC-1F1B/Android/data/': Permission denied
```

Android 11 special-cases `Android/data` and `Android/obb` above the unix
permission bits. No app may read another app's directory there, whatever the
mode says and whatever storage permissions have been granted. `MANAGE_EXTERNAL_STORAGE`
does not lift it either.

### Why this matters here

Phase 04 put 83 map regions in `Android/data/net.osmand.plus/files/` — because
that is where OsmAnd keeps them, and OsmAnd is not negotiable about it. The maps
work perfectly: OsmAnd reads its own directory and lists all 83 regions.

**But the phone can never audit them.** Anything running in Termux — `status`,
a future integrity check, any script at all — is blind to the single largest
body of content on the card.

### Consequence

The dividing line from the first amendment stands (executable internal, data on
the card), with an addition:

**Content owned by another app is verifiable only from the Mac.** The Mac mounts
the card as an ordinary FAT32 volume with no scoped-storage layer, so it sees
everything.

`scripts/mac/card-manifest.sh` writes a record the phone can read — counts,
byte totals and per-file sizes — into `Reference/`, which is a plain directory
outside `Android/`. `status` reports that record and labels it as a record,
never as a live count.

This is deliberate. A health check that appears to verify something it cannot
see is worse than one that admits the gap: it is the same failure as the Phase 04
content check that reported a match on a file that did not exist. A check must
either see its subject or say that it cannot.
