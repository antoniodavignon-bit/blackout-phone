# Engineering log

Newest first. Written as the build happens, including the parts that did not work.

---

## 2026-09-08 — Phase 02 complete: it's a Linux machine now

Termux is up, the toolchain is installed, and the phone is reachable from the MacBook over SSH.

**Verified on device:**

```
$ python --version && git --version && ls ~/storage/
Python 3.14.6
git version 2.55.0
dcim  downloads  external-1  movies  music  pictures  shared
```

**The ergonomic problem, and the fix.** The first Termux session on the device made something obvious: with the on-screen keyboard up, a 2.8″ 480×640 display leaves roughly three visible lines of terminal. Typing a package install line on a T9 keypad is not a workflow.

The fix turned out to be better than a Bluetooth keyboard. Termux ships `sshd`, and `adb` can forward a TCP port over the USB cable — so no Wi-Fi IP, no network config, no exposure:

```
# phone
pkg install openssh -y && passwd && whoami && sshd

# mac
adb forward tcp:8022 tcp:8022
ssh -p 8022 u0_aXXX@localhost
```

From that point the Mac terminal *is* the phone's shell. Full keyboard, real screen, copy-paste. Every phase after this gets built from the laptop and the phone just gets carried. Written up as [ADR-005](decisions/ADR-005-ssh-over-usb.md).

**Termux ships a distant mirror.** The first `pkg upgrade` pulled every package from `mirror.iscas.ac.cn` — a Chinese mirror, from Virginia, over 2.4 GHz Wi-Fi, onto a 1.3 GHz A53. Three stacked bottlenecks, one of them free to fix:

```
termux-change-repo   # select main repo → North America group
pkg update
```

Worth doing before anything that installs at volume.

**Also learned:** `pkg upgrade` stops on dpkg conffile prompts (`*** openssl.cnf (Y/I/N/O/D/Z)`) and waits indefinitely. On a screen showing three lines this is easy to mistake for a hang. Default (Enter) is correct on a fresh system.

**Note for Phase 04:** `~/storage/external-1` appears in the Termux storage listing and points at the SD card. Whether it is writable is being tested — the documented behavior is read-only, but measuring beats assuming.

---

## 2026-09-08 — Phase 01 complete: device access and the card

**Factory Reset Protection cost two days.** The device had been reset without removing its Google account, arming FRP. None of the accounts I owned were accepted.

The resolution was mundane and worth recording because the technical rabbit holes were all dead ends: a family member had used the phone and signed in with *his* Google account. FRP was asking for his, not mine. He supplied it and the device opened in thirty seconds.

Things that were **not** the answer, verified:
- Removing devices from your Google account's device list does **not** clear FRP. FRP is device-side and checks the account last signed in *on the phone*.
- The manufacturer cannot help. Bullitt Group closed January 2024; `catphones.com` no longer resolves. No firmware, no support, no unlock path.
- The carrier (a Lifeline MVNO) can reissue a SIM but has no FRP tooling — it's not the OEM.

**Design consequence:** for a device whose entire purpose is working with no network, a Google account is a liability, not a feature. Every app this build needs — Termux, Kiwix, OsmAnd — comes from F-Droid or a direct APK. So once setup is done the account comes off the device entirely. No account at reset time means FRP never arms again and the phone can be wiped and rebuilt freely for the rest of its life.

**The SD card had a previous life.** A 128 GB card that macOS refused to mount. `diskutil list` explained it:

```
/dev/disk4 (external, physical):
   0:  GUID_partition_scheme            *126.4 GB   disk4
   1:  19A710A2-B3CA-11E4-B026-10604B889DCF   16.8 MB   disk4s1
   2:  193D1EA4-B3CA-11E4-B075-10604B889DCF   126.4 GB  disk4s2
```

Those two type GUIDs are Android's `android_meta` and `android_expand` — the card had been formatted as **adoptable storage** by some previous Android device. The expand partition is dm-crypt encrypted (`aes-cbc-essiv:sha256`) with a key stored only on that phone's `/data` partition. Unreadable anywhere else, permanently.

Healthy hardware, wrong identity. Erased and rebuilt:

```
diskutil unmountDisk force /dev/disk4
sudo diskutil eraseDisk ExFAT CATSD MBRFormat /dev/disk4
```

**Then the device rejected exFAT.** The Cat S22 Flip refused to mount the exFAT card and offered to format it. exFAT support on Android is vendor-dependent and this device doesn't have it — a possibility flagged before testing, now confirmed on hardware.

Reformatted in the phone as **portable** storage (never internal — that is exactly the adoptable-storage state that made this card unreadable in the first place). Result: FAT32, mounted, 118 GB available, still fully read/write from macOS.

```
$ adb shell df -h /storage/0CEC-1F1B
Filesystem     Size  Used Avail Use% Mounted on
/dev/fuse      118G  1.0M  118G   1% /storage/0CEC-1F1B
```

The cost is a hard 4 GB per-file ceiling, which reshapes the entire library plan. See [ADR-004](decisions/ADR-004-fat32-library.md).

---

## 2026-09-07 — Scoping: what this hardware can actually do

Before writing any build steps, established what the device is and isn't.

**The temptation was to make it an AI device.** A Snapdragon 215 with 2 GB of Go-edition RAM leaves roughly a gigabyte usable. That rules out anything near a useful general model. The honest ceiling is a sub-1B quantized GGUF — Qwen2.5-0.5B-Instruct at Q4_K_M is 491 MB and fits with room for a small context window.

I could not find a published tokens-per-second figure for llama.cpp on a Snapdragon 215 and declined to invent one. Phase 03 includes a `llama-bench` step; the measured number goes in this log and sets what the model is actually used for.

**The rejected alternative** was making the phone a thin client to the Ollama stack already running on the MacBook — full 8B models from a rugged pocket device. Better output, and rejected anyway: it needs a network, and a device that needs a network to be useful is not an offline device. See [ADR-001](decisions/ADR-001-offline-first.md).

**What the hardware is genuinely good at**, once the AI ambition is right-sized: a pocket Linux terminal, an offline reference library on a 128 GB card, a rugged GPS unit with offline maps, and a capture device that survives being dropped. The model is a small utility inside that, not the headline.
