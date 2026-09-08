# Hardware

## Cat S22 Flip — as specified

| | |
|---|---|
| SoC | Qualcomm QM215 Snapdragon 215, 28 nm |
| CPU | 4 × Cortex-A53 @ 1.3 GHz, arm64 |
| GPU | Adreno 308 |
| RAM | 2 GB |
| Storage | 16 GB eMMC 5.1 + dedicated microSDXC slot |
| OS | Android 11 (Go edition) |
| Display | 2.8″ TFT, 480×640, ~286 ppi, Gorilla Glass 5 |
| External display | 1.44″ |
| Battery | Li-Ion 2000 mAh, removable |
| Wi-Fi | 802.11 b/g/n — 2.4 GHz only |
| Bluetooth | 4.2, A2DP |
| USB | Type-C 2.0 |
| Positioning | GPS, GLONASS, Galileo |
| Sensors | accelerometer, proximity, barometer |
| Cameras | 5 MP rear w/ LED flash, 2 MP front |
| Sealing | IP68 (1.5 m / 35 min), MIL-STD-810H, 1.8 m drop |
| Absent | NFC, 3.5 mm jack, 5 GHz Wi-Fi |

Manufacturer Bullitt Group closed January 2024. No vendor support, firmware, or warranty channel exists.

## Measured on this device

| Measurement | Value | How |
|---|---|---|
| SD card capacity after FAT32 format | 118 GB available | `adb shell df -h` |
| exFAT support | **None** — card rejected, device offered to reformat | Direct test |
| Python in Termux | 3.14.6 | `python --version` |
| git in Termux | 2.55.0 | `git --version` |
| Termux default mirror | `mirror.iscas.ac.cn` (China) | Observed during `pkg upgrade` |
| adb serial | `S226001221008442` | `adb devices` |
| SD volume ID | `0CEC-1F1B` | `adb shell ls /storage` |

## Unmeasured

| Question | Why it matters | Plan |
|---|---|---|
| llama.cpp tokens/sec | Decides whether the model is conversational or batch-only | `llama-bench` in Phase 03 |
| USB-C OTG support | Not stated in published specs | Test with a cheap adapter |
| Termux write access to SD | Documented as unavailable; worth confirming per-device | `touch ~/storage/external-1/…` |
| Real-world battery under inference | Determines how many spares to carry | Measure during the 48-hour trial |

## Kit

| Item | Why |
|---|---|
| microSD 128 GB | The library shelf. Onn/SDXC, reformatted FAT32 by the device. |
| USB-C cable (data, not charge-only) | adb, scp, and the SSH tunnel all ride it |
| Spare batteries ×2 | Removable pack, cheapest meaningful upgrade |
| Bluetooth keyboard | Optional once SSH-over-USB works; useful for field editing |
