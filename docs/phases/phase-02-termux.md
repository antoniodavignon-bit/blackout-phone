# Phase 02 — Termux

**Status:** ✅ Complete · 2026-09-08

Goal: a real Linux userland on the phone, reachable from the Mac keyboard.

## Steps

### 1. F-Droid

```bash
# mac
cd ~/Downloads
curl --remote-name https://f-droid.org/F-Droid.apk
ls -lh F-Droid.apk        # ~12 MB
adb install F-Droid.apk
```

### 2. Termux and add-ons — all from F-Droid

Install **Termux**, **Termux:API**, **Termux:Boot**.

> The Play Store build of Termux is abandoned and fails on package installs. All three must come from the same source — mixed signatures and the add-ons silently refuse to connect to the main app.

Grab **OsmAnd** in the same session. Kiwix's APK is large and may time out over 2.4 GHz Wi-Fi; sideload it from the Mac instead if so.

### 3. Fix the mirror before installing anything

```bash
termux-change-repo     # select main repo → North America group
pkg update
```

Termux defaulted to a mirror in China. From the US east coast, on 2.4 GHz Wi-Fi, on a 1.3 GHz A53, that is three stacked bottlenecks and this is the free one.

### 4. Base system

```bash
pkg upgrade -y
```

> Stops on dpkg conffile prompts (`*** openssl.cnf (Y/I/N/O/D/Z) [default=N]`) and waits. On a three-line viewport this looks like a hang. Enter accepts the default, which is correct on a fresh system.

### 5. SSH — get off the keypad

```bash
# phone
pkg install openssh -y
passwd
whoami                 # → u0_aXXX
sshd
```

```bash
# mac
adb forward tcp:8022 tcp:8022
ssh -p 8022 u0_aXXX@localhost
```

The Mac terminal is now the phone's shell. See [ADR-005](../decisions/ADR-005-ssh-over-usb.md).

### 6. Toolchain — paste this, don't thumb it

```bash
pkg install -y git cmake clang python nano rsync termux-api libandroid-spawn tmux
termux-setup-storage
```

`termux-setup-storage` fires an Android permission dialog on the phone. The SSH session waits until you tap Allow. If nothing appears, bring Termux to the foreground on the device and re-run.

### 7. Vault skeleton

```bash
mkdir -p ~/storage/shared/DMG/{inbox,vault,scripts}
mkdir -p ~/models
```

## Result

```
$ python --version && git --version && ls ~/storage/
Python 3.14.6
git version 2.55.0
dcim  downloads  external-1  movies  music  pictures  shared
```

`external-1` is the SD card, visible for reads.
