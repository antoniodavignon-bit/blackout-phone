# Phase 05 — Capture and sync

**Status:** ⏳ Planned

Goal: close the loop. What goes into the device in a dead zone comes back out.

## Steps

### 1. Capture

```bash
cat > $PREFIX/bin/cap <<'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
echo "- [$(date '+%Y-%m-%d %H:%M')] $*" \
  >> ~/storage/shared/DMG/inbox/capture.md
echo "captured."
SCRIPT
chmod +x $PREFIX/bin/cap
```

One command, timestamped, appended, offline. This is the reason to carry the thing.

### 2. Voice

```bash
termux-microphone-record -f ~/storage/shared/DMG/inbox/note.m4a -l 120
termux-microphone-record -q     # stop
```

Records with no network. Transcribe later on the Mac, where the horsepower is.

### 3. Sync home

```bash
cat > $PREFIX/bin/home <<'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
rsync -avz ~/storage/shared/DMG/inbox/ user@MAC-IP:~/Documents/inbox/
SCRIPT
chmod +x $PREFIX/bin/home
```

### 4. Persist sshd across reboots

Termux:Boot, so the SSH interface survives a restart without touching the keypad.

### 5. The 48-hour blackout trial

Radios off, primary phone in a drawer, this device only. Whatever breaks in those two days is the real punch list — not anything written in advance.

## The field loop

1. Radios off by default.
2. `cap "…"` everything the moment you think it. No triage in the field.
3. `vs "…"` to find what you already wrote down.
4. `ask "…"` for bounded text work only.
5. Kiwix and OsmAnd for anything factual or spatial. The model is not a reference source.
6. `home` when Wi-Fi returns, then process on the Mac.
7. Swap the battery instead of hunting a charger. That's why it's removable.
