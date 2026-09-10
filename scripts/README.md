# Field scripts

These live on the device in `$PREFIX/bin` and are the entire daily interface.
Internal storage only — the card is `noexec` (see [ADR-003](../docs/decisions/ADR-003-storage-split.md)).

| Command | Does |
|---|---|
| `cap "…"` | Timestamps a note into the capture inbox. Offline. |
| `vs "…"` | Full-text search across the notes vault and the card's reference index. |
| `status` | Five-second health check — storage, library counts, captures, battery. |
| `home` | rsync the inbox to the Mac when a network returns. |

Install with `./install.sh` from a copy of this directory on the device.

`ask` was removed in Phase 05. The on-device model measured 0.6 tok/s and is not
part of the daily loop — see [ADR-002](../docs/decisions/ADR-002-model-ceiling.md).

## Mac-side

`mac/card-manifest.sh` runs on the Mac with the card mounted. Android 11 blocks
Termux from reading `Android/data`, where OsmAnd keeps its maps, so the phone
cannot count them — see [ADR-003](../docs/decisions/ADR-003-storage-split.md#second-amendment-2026-09-10--androiddata-is-not-included).
This writes counts and per-file sizes into `Reference/`, which `status` reads
and reports as a record rather than a live check.

```bash
./mac/card-manifest.sh              # counts and sizes
./mac/card-manifest.sh --checksums  # plus SHA-256 of every map (slow)
```

## Configuration

`home` reads `~/.blackout.conf`, which is not committed:

```bash
MAC_HOST="user@192.168.1.50"
MAC_PATH="~/Documents/inbox/"
```

## Hard-coded paths

The card UUID `0CEC-1F1B` appears in `vs` and `status`. It is stable for this
card; a reformat or a replacement card changes it. `ls /storage/` on the device
gives the current value.
