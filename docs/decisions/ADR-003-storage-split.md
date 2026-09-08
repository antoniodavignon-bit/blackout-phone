# ADR-003 — Internal/SD storage split

**Status:** Accepted 2026-09-08 · **Amended 2026-09-08** after measurement — see [Amendment](#amendment-2026-09-08--measured-on-hardware)

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

### Open question

Whether `llama-cli` can `mmap` a GGUF from a `noexec` FAT32 mount. Read-only mapping should not trip the `noexec` restriction, which only blocks `PROT_EXEC` — but this is reasoning, not measurement. Test once Phase 03 compiles, and record the result here.
