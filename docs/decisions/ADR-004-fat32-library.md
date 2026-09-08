# ADR-004 — FAT32 and the 4 GB library problem

**Status:** Accepted · 2026-09-08

## Context

The 128 GB card was formatted exFAT on macOS, which is the SDXC standard and removes any practical file-size limit. **The device rejected it** — it refused to mount the card and offered to format. exFAT support on Android requires a vendor-supplied driver and this device does not have one.

Reformatting in the phone as portable storage produced FAT32: readable and writable from macOS, mounted cleanly at 118 GB available, and carrying a hard **4 GB per-file ceiling**.

## Decision

Accept FAT32. Build the library from curated sub-4 GB packs rather than full-corpus archives.

| Pack | Size |
|---|---|
| `wikipedia_en_simple_all_mini` | 447 MB — all of Simple English Wikipedia |
| `wikipedia_en_top_mini` | 316 MB |
| `wikipedia_en_100` | 318 MB |
| `wikipedia_en_medicine_mini` | 155 MB |
| `wikipedia_en_mathematics_mini` | 56 MB |
| `wikipedia_en_physics_mini` | 54 MB |

Topic `nopic` packs for chemistry, computing, geography, history, sociology and climate change are also under the ceiling.

## Rejected alternatives

**Full English Wikipedia.** Off the table in every variant — `wikipedia_en_all_mini` alone is 12 GB, and nopic and maxi are far larger.

**Split ZIM archives.** Kiwix's split-file support is an unmaintained remnant. Maintainer-tracked issues report split archives failing to open on Android, and most large ZIMs contain internal search indexes that individually exceed 4 GB, so they cannot be split into valid FAT32-sized chunks at all.

**Adoptable storage.** Formatting the card as internal storage would allow ext4 and remove the file-size limit — and would encrypt the card to this one phone with a key stored on its `/data` partition, making it unreadable from the Mac and unrecoverable if the phone is ever reset. This is precisely the state the card arrived in and had to be erased out of. Never again.

## Consequences

- The encyclopedia is curated, not complete. Ten packs is roughly 5 GB.
- **Space was never the constraint — a single large file is.** Over 100 GB remains for offline maps, PDFs, and documents.
- Every file crosses from the Mac, where the 4 GB check happens before transfer.
