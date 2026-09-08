# Phase 01 — Prep

**Status:** ✅ Complete · 2026-09-08

Goal: a device you control, a card that mounts, and a working pipe from the Mac.

## Steps

### 1. Clear the device

Factory reset, skip optional sign-ins. Every synced account is background RAM this device does not have.

> **If Factory Reset Protection blocks you:** FRP wants the exact Google account last signed in *on the phone* — which may not be one of yours if anyone else used it. Check `myaccount.google.com → Security → Your devices` on each account you own to identify it. Removing a device from your account's device list does **not** clear FRP.

### 2. Developer access

Settings → About phone → tap **Build number** ×7 → System → Developer options → enable **USB debugging**.

### 3. adb on the Mac

```bash
brew install --cask android-platform-tools
adb devices
```

A serial with `device` beside it. `unauthorized` means the RSA prompt is waiting on the phone — unlock it, check "Always allow from this computer", Allow.

### 4. Format the card — portable, never internal

Insert the microSD. When the phone offers to set it up, choose **portable storage**.

> **Internal (adoptable) storage encrypts the card with a key stored only on this phone.** The Mac can never read it again and the contents are unrecoverable if the phone is reset. See [ADR-004](../decisions/ADR-004-fat32-library.md).

This device rejects exFAT and formats FAT32 — readable and writable from macOS, with a 4 GB per-file ceiling.

### 5. Verify and scaffold over adb

```bash
adb shell ls /storage              # → the card's volume ID, e.g. 0CEC-1F1B
export SD=/storage/0CEC-1F1B       # save yourself the retyping
adb shell df -h $SD
adb shell mkdir -p $SD/Kiwix $SD/Maps $SD/Reference
adb shell ls -la $SD/
```

### 6. Prove the pipe

```bash
echo "blackout build test" > /tmp/bbtest.txt
adb push /tmp/bbtest.txt $SD/Reference/
adb shell cat $SD/Reference/bbtest.txt
```

### 7. Reduce the resident footprint

```bash
adb shell pm list packages | sort
adb shell pm uninstall --user 0 <package>
```

Only remove packages you can positively identify. Recoverable by factory reset — which means redoing this phase.

### 8. Remove the Google account

Once the F-Droid apps are installed (Phase 02), Settings → Accounts → remove the Google account. Nothing in this build needs Play Store, and no account at reset time means FRP never arms again.

## Result

```
$ adb shell df -h /storage/0CEC-1F1B
Filesystem     Size  Used Avail Use% Mounted on
/dev/fuse      118G  1.0M  118G   1% /storage/0CEC-1F1B
```
