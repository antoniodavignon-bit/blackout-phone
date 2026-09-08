# Phase 04 — Offline library

**Status:** ⏳ Planned

Goal: a 128 GB reference shelf that works with the radios off.

## The constraint that shapes this phase

FAT32 means **4 GB maximum per file**. Full English Wikipedia is out in every variant — `wikipedia_en_all_mini` alone is 12 GB — and Kiwix's split-ZIM support is unmaintained and unreliable. See [ADR-004](../decisions/ADR-004-fat32-library.md).

Space is not the problem. One large file is.

## Steps

### 1. Kiwix packs

Load from the Mac; every file gets a size check before transfer.

| Pack | Size |
|---|---|
| `wikipedia_en_simple_all_mini` | 447 MB — best breadth per byte, start here |
| `wikipedia_en_top_mini` | 316 MB |
| `wikipedia_en_100` | 318 MB |
| `wikipedia_en_medicine_mini` | 155 MB |
| `wikipedia_en_mathematics_mini` | 56 MB |
| `wikipedia_en_physics_mini` | 54 MB |

Topic `nopic` packs — computing, chemistry, geography, history, sociology, climate change — are also under the ceiling.

```bash
# mac
adb push <pack>.zim $SD/Kiwix/
```

Ten packs is roughly 5 GB, leaving well over 100 GB.

### 2. Offline maps

OsmAnd, regions downloaded to `$SD/Maps/`. The device has GPS, GLONASS and Galileo plus a barometer, and it's IP68 and drop-rated — a legitimate no-signal navigation unit.

### 3. Own documents

```bash
adb push ~/Documents/SOPs/ $SD/Reference/
```

Plain markdown, no app required.

### 4. Shell search over the vault

```bash
cat > $PREFIX/bin/vs <<'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
grep -rin --color=always "$*" ~/storage/shared/DMG/vault/ | head -40
SCRIPT
chmod +x $PREFIX/bin/vs
```

Full-text search across everything you own, offline, no index, no service, no account.
