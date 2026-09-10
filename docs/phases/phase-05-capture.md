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

From the Mac, wiping the destination first:

```bash
adb shell rm -rf /sdcard/blackout-scripts
adb push scripts /sdcard/blackout-scripts
```

Then on the phone:

```bash
bash /sdcard/blackout-scripts/install.sh
```

`bash <path>` rather than `./install.sh` — `/sdcard` is `noexec`, but bash
reading a file as data is unaffected. The scripts themselves install to
`$PREFIX/bin` on internal storage, because nothing executable runs from
external storage.

> **`adb push` nests on a second run.** `adb push scripts /sdcard/blackout-scripts`
> creates the directory the first time and copies the files into it. Run it again
> and the destination already exists, so adb copies the *folder* inside —
> producing `/sdcard/blackout-scripts/scripts/`. The stale files stay at the top
> level, and `install.sh` keeps installing them.
>
> This cost four rounds of "the push worked, the installer ran, nothing changed."
> Both halves were true. They were pointed at different directories.
>
> Wipe the destination first, or push `scripts/.` instead of `scripts`.
> `install.sh` now warns when it sees a nested copy beside itself.

### Verified on hardware 2026-09-10

```
--- vault (1) ---
inbox/capture.md:1:- [2026-09-10 15:47] first capture on the device

--- reference ---
kjv-bible.txt  (606 matches)
    25:The First Book of Moses: Called Genesis
    … 603 more

CATALOG.md  (3 matches)
    20:**First aid and injuries**
```

```
library
  OK    zims: 18
  WARN  no MAPS.manifest — run scripts/mac/card-manifest.sh with the card in the Mac
  OK    CATALOG.md present
```

`cap`, `vs` and `status` all confirmed on the device. `home` is written but not
yet configured or run.

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

## Persist sshd across reboots — verified 2026-09-10

```bash
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start-sshd <<'BOOT'
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
sshd
BOOT
chmod +x ~/.termux/boot/start-sshd
```

Launch the Termux:Boot app once from the app drawer — it stays disarmed until
it has been opened at least once. Set Termux to **Unrestricted** under battery
optimization as well; Android Go reaps background processes and would otherwise
kill `sshd` shortly after it starts.

### Verified

```
$ adb reboot
$ adb forward tcp:8022 tcp:8022 && ssh -p 8022 u0_a195@localhost
Connection closed by 127.0.0.1 port 8022      # still booting
$ ssh -p 8022 u0_a195@localhost
u0_a195@localhost's password:                 # sshd came back on its own
```

**The first attempt failing is normal and not a failure.** Termux:Boot runs on
`BOOT_COMPLETED`, which Android 11 does not deliver until the device has been
unlocked once after boot. Retry after unlocking before concluding anything.

The `adb forward` does not survive a reboot either — it has to be re-run every
time, which looks like a phone-side problem and is not one.

This clears one of the four defined trial failures.

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
