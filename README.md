# Blackout Phone

Turning a drawer-bound rugged flip phone into a fully offline terminal, knowledge vault, and on-device AI host — no signal, no cloud, no account required.

Built in public. Every constraint below was measured on the actual hardware, not assumed.

---

## The premise

A Cat S22 Flip is a full Android computer that happens to fold. It sideloads, runs a real Linux userland via Termux, compiles C++ on-device, and survives a 1.8 m drop while sealed to IP68.

It also has **2 GB of RAM on an Android 11 Go build**, which leaves roughly one gigabyte usable. That number is the design constraint behind every decision in this repo.

The goal is not a second smartphone. It's a device that does useful work when there is no network at all.

## Hardware

| | |
|---|---|
| Device | Cat S22 Flip |
| SoC | Qualcomm QM215 Snapdragon 215, 28 nm |
| CPU | 4 × Cortex-A53 @ 1.3 GHz — ARMv8-A silicon, **32-bit armv7l userspace** |
| RAM | 2 GB — **the binding constraint** |
| Storage | 16 GB eMMC + dedicated microSD slot |
| OS | Android 11 (Go edition) |
| Display | 2.8″ 480×640 touch + 1.44″ external |
| Battery | 2000 mAh, removable |
| Wireless | Wi-Fi b/g/n (2.4 GHz only), Bluetooth 4.2 |
| Sealing | IP68, MIL-STD-810H, 1.8 m drop rated |
| Not present | NFC, 3.5 mm jack, 5 GHz Wi-Fi |

The manufacturer, Bullitt Group, closed in January 2024. There is no vendor support, no firmware source, and no warranty channel. Everything here is built on what the device shipped with.

## Architecture

```
┌─────────────────────────────────────────────┐
│  Cat S22 Flip                               │
│                                             │
│  Internal 16 GB          microSD 128 GB     │
│  ├── Termux rootfs       ├── Kiwix/  (ZIM)  │
│  ├── ~/llama.cpp/        ├── Maps/          │
│  │   (binaries only)     ├── Reference/     │
│  └── shared/DMG/         └── models/ (GGUF) │
│      ├── inbox/                             │
│      └── vault/                             │
└─────────────────────────────────────────────┘
              │
              │  USB — adb + SSH over forwarded port
              ▼
        MacBook Air M4
        (build host, library source, sync target)
```

**Why the split:** the card is mounted `noexec`, so nothing executable can run from it — the build and every binary stay on internal storage. Everything else is data and can live on the card, which measured fully writable from Termux at 19.5 MB/s. See [ADR-003](docs/decisions/ADR-003-storage-split.md).

## Status

| Phase | What it covers | Status |
|---|---|---|
| [01 — Prep](docs/phases/phase-01-prep.md) | Device access, adb, microSD, debloat | ✅ Complete |
| [02 — Termux](docs/phases/phase-02-termux.md) | F-Droid, Termux, toolchain, SSH access | ✅ Complete |
| [03 — On-device model](docs/phases/phase-03-model.md) | llama.cpp compile, GGUF, benchmark | ✅ Complete — **0.6 tok/s** |
| [04 — Offline library](docs/phases/phase-04-library.md) | Kiwix ZIMs, offline maps, own docs | ✅ Complete — **18 archives, 18 GB** |
| [05 — Capture & sync](docs/phases/phase-05-capture.md) | Field scripts, voice capture, rsync home | ⏳ Planned |

Running narrative with dates and dead ends: **[docs/engineering-log.md](docs/engineering-log.md)**

## Decisions

- [ADR-001 — Offline-first, not a thin client](docs/decisions/ADR-001-offline-first.md)
- [ADR-002 — Sub-1B model ceiling](docs/decisions/ADR-002-model-ceiling.md)
- [ADR-003 — Internal/SD storage split](docs/decisions/ADR-003-storage-split.md)
- [ADR-004 — FAT32 and the 4 GB library problem](docs/decisions/ADR-004-fat32-library.md)
- [ADR-005 — SSH over USB as the build interface](docs/decisions/ADR-005-ssh-over-usb.md)

## Measured constraints

Things that are true of this hardware and will not be engineered away:

| Constraint | Cause | How the build works with it |
|---|---|---|
| ~1 GB usable RAM | 2 GB total, Android 11 Go | One workload at a time. Compile with `-j 2`, not `-j 4`. |
| **0.6 tok/s generation** | 4 × A53 @ 1.3 GHz, 28 nm, 32-bit | Model is for tiny outputs only — not conversation. |
| 32-bit armv7l userspace | Android Go build on 64-bit silicon | llama.cpp needs patching; its test suite won't compile; mainline Kiwix won't install (use the IzzyOnDroid armeabi-v7a build). |
| Card is `noexec` | FAT32 carries no permission bits; `chmod +x` does not stick | Binaries and the build stay internal. Data — models included — can live on the card. |
| No exFAT support | Device rejects exFAT cards outright | FAT32, and a hard 4 GB per-file ceiling. |
| Full Wikipedia impossible | `wikipedia_en_all_mini` is 12 GB; split-ZIM support in Kiwix is unmaintained and unreliable | Curated sub-4 GB topic packs — `maxi` variants with images do fit. |
| Truncated downloads open silently | A partial ZIM is structurally valid and shows a normal title | Verify every archive's byte count against the server before trusting it. |
| Slow package installs | Termux defaults to a geographically distant mirror | `termux-change-repo` → North America. |
| 2.4 GHz Wi-Fi only | b/g/n radio | Download on the Mac, `scp`/`adb push` across. |
| 2000 mAh battery | Small pack, hungry workloads | Removable — carry spares. |

## Repo layout

```
docs/
  engineering-log.md    running build log, newest first
  hardware.md           full spec sheet and measurements
  phases/               one file per build phase
  decisions/            ADRs for the calls that shaped the build
scripts/                field scripts that live on the device
```

## Reproducing this

The build targets one specific device, but nothing in it is Cat-specific except the spec sheet. Any Android device with 2 GB+ RAM, a microSD slot, and Termux support runs the same phases. Start at [Phase 01](docs/phases/phase-01-prep.md).

## License

MIT — see [LICENSE](LICENSE).
