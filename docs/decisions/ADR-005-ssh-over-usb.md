# ADR-005 — SSH over USB as the build interface

**Status:** Accepted · 2026-09-08

## Context

With the on-screen keyboard raised, the 2.8″ 480×640 display leaves roughly three visible lines of terminal. The alternative input is a T9 keypad. Neither is a viable way to type package installs, compile invocations, or shell scripts.

## Decision

Run `sshd` inside Termux and reach it from the MacBook through an `adb`-forwarded port over the USB cable.

```
# phone, once
pkg install openssh -y
passwd
whoami          # → u0_aXXX
sshd

# mac
adb forward tcp:8022 tcp:8022
ssh -p 8022 u0_aXXX@localhost
```

## Rejected alternatives

**Bluetooth keyboard.** Solves typing but not the three-line viewport, and adds hardware to carry.

**SSH over Wi-Fi.** Works, but needs the phone's IP, depends on both devices being on the same network, and exposes the port to that network. The USB tunnel needs none of that and works with the radios off.

**`adb shell`.** Runs as the `shell` user in Android's own environment, not Termux's — different paths, no access to the Termux package tree.

## Consequences

- All construction happens from the laptop: full keyboard, scrollback, copy-paste, multiple windows.
- Long builds run under `tmux` so they survive a dropped connection.
- `sshd` does not persist across reboots; Termux:Boot handles that in Phase 05.
- The keypad becomes what it should be — the field interface, not the construction interface.
