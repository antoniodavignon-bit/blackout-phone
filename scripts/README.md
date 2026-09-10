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
