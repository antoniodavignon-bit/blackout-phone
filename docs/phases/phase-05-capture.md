# Phase 05 — Capture, sync, and the blackout trial

**Status:** 🔨 In progress

Goal: close the loop. What goes into the device in a dead zone comes back out —
and then prove it by living on the thing for two days.

## The four commands

`ask` is gone. Phase 03 measured 0.6 tok/s and Phase 05 acts on that number
rather than working around it — see the [ADR-002 amendment](../decisions/ADR-002-model-ceiling.md#amendment-2026-09-10--cut-from-the-daily-loop).
What remains all runs at full speed with every radio off.

| Command | Does |
|---|---|
| `cap "…"` | Timestamps a note into the capture inbox |
| `vs "…"` | Searches the vault and the card's reference index |
| `status` | Health check — storage, library counts, captures, battery |
| `home` | rsync the inbox to the Mac when a network returns |

Source lives in [`scripts/`](../../scripts/), tested before commit.

### Install

```bash
cd ~/blackout-phone/scripts
./install.sh
```

The card is `noexec`, so these go to `$PREFIX/bin` on internal storage. Nothing
executable ever runs from the SD card.

### Configure `home`

```bash
cat > ~/.blackout.conf <<'CONF'
MAC_HOST="user@192.168.1.50"
MAC_PATH="~/Documents/inbox/"
CONF
```

Not committed — the repo is public and the address is not.

## Voice capture

```bash
termux-microphone-record -f ~/storage/shared/DMG/inbox/note.m4a -l 120
termux-microphone-record -q     # stop
```

Records with no network. Transcribe later on the Mac, where the horsepower is.
Requires the Termux:API app plus the `termux-api` package — the same dependency
`status` needs for its battery reading.

## Persist sshd across reboots

Termux:Boot, so the SSH interface survives a restart without touching the keypad.

## The 48-hour blackout trial

**Criteria are written here before the trial runs.** A trial with no criteria
produces a feeling, and a phase doc cannot be written from a feeling.

### Rules

1. Radios off by default. Turning one on is allowed and gets logged, with why.
2. Primary phone in a drawer. Reachable for a genuine emergency; every pickup
   is logged with its reason.
3. Log in the moment, not afterward. `cap` is right there — that is the point.
4. Run `status` at the start and at the end.

### Scorecard

Fill in the actuals. The bar is what "this works" was defined as in advance.

| Metric | How measured | Bar | Actual |
|---|---|---|---|
| Battery per pack | note % at start and end of each session | ≥ 18 h mixed use | |
| Captures made | `wc -l` delta on `capture.md` | ≥ 10 over 48 h | |
| `vs` invocations | count | ≥ 3 | |
| Map used to navigate for real | yes/no | at least once | |
| Kiwix answered a real question | yes/no | at least once | |
| Other-phone pickups | logged, with reason | ≤ 3 | |
| Reach-fails | logged at the moment | listed, not scored | |
| `status` clean at start and end | yes/no | both | |

### Defined failures

Any one of these fails the trial outright, regardless of the scorecard:

- A capture is lost
- The card corrupts, or `status` reports a library count drop
- `sshd` does not survive a reboot
- Battery cannot carry a normal day on two packs

### Reach-fail log

The most valuable output of the trial. Every time the device could not do
something, recorded when it happened:

```
- [date time] wanted X, could not because Y
```

That list is the real Phase 06 punch list — not anything written in advance,
including this document.

## The field loop

1. Radios off by default.
2. `cap "…"` everything the moment you think it. No triage in the field.
3. `vs "…"` to find what you already wrote down.
4. Kiwix and OsmAnd for anything factual or spatial.
5. `status` when something feels off, and before you rely on the device.
6. `home` when Wi-Fi returns, then process on the Mac.
7. Swap the battery instead of hunting a charger. That's why it's removable.
