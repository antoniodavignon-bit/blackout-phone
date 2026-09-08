# ADR-003 — Internal/SD storage split

**Status:** Accepted · 2026-09-08

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
