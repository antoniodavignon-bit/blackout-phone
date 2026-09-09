# Phase 04 — Offline library

**Status:** ✅ Complete · 2026-09-09 — **18 archives, 18 GB**

Goal: a reference library that works with the radios off. This, not the
language model, is what makes the device worth carrying.

## Install Kiwix — mind the ABI

Mainline `org.kiwix.kiwixmobile` targets arm64 and will not install on a 32-bit
userspace. Use the IzzyOnDroid armeabi-v7a build:

```bash
cd ~/Downloads
curl -L -O https://apt.izzysoft.de/fdroid/repo/org.kiwix.kiwixmobile.standalone_5231765.apk
adb install org.kiwix.kiwixmobile.standalone_5231765.apk
```

Grant **All files access** on first launch or the library will scan empty.

## Load the card via a reader, not the cable

18 GB over `adb` is slow for no reason. Eject the card from the phone (Settings
→ Storage → SD card → Eject), put it in the Mac's reader, and write directly.

> The phone's format wipes the volume label. It will mount as `NO NAME` —
> a space that breaks every unquoted path. Rename it once:
> `sudo diskutil rename "/Volumes/NO NAME" CATSD`

**Download straight to the card** rather than staging on the Mac. It has more
room, and a full build host silently truncates files (see below).

```bash
cd /Volumes/CATSD/Kiwix
O=https://download.kiwix.org/zim/other
W=https://download.kiwix.org/zim/wikibooks
P=https://download.kiwix.org/zim/wikipedia
```

## The library

| Pack | Size | Why |
|---|---|---|
| `trueprepper.com_en_all_2026-05` | 1.3 G | Survival, gear, scenarios, checklists |
| `appropedia_en_all_maxi_2026-02` | 555 M | Water treatment, food storage, off-grid |
| `wikibooks_en_all_nopic_2026-04` | 3.3 G | Manuals — foraging, first aid, knots |
| `mdwiki_en_all_maxi_2025-11` | 2.1 G | Medical reference |
| `wikem_en_all_maxi_2026-07` | 357 M | Emergency medicine, fast lookup |
| `wikispecies_en_all_maxi_2026-07` | 3.2 G | Species taxonomy |
| `theworldfactbook_en_all_2026-02` | 388 M | Country data |
| `wikipedia_en_simple_all_nopic_2026-05` | 937 M | All of Simple English Wikipedia |
| `wikipedia_en_100_2026-08` | 318 M | Core articles |
| `wikipedia_en_computer_maxi_2026-06` | 909 M | With images |
| `wikipedia_en_geography_maxi_2026-07` | 1.4 G | With images |
| `wikipedia_en_history_maxi_2026-07` | 2.2 G | With images |
| `wikipedia_en_medicine_mini_2026-04` | 155 M | |
| `wikipedia_en_mathematics_nopic_2026-06` | 327 M | |
| `wikipedia_en_physics_nopic_2026-07` | 304 M | |
| `wikipedia_en_chemistry_nopic_2026-07` | 124 M | |
| `wikipedia_en_climate-change_maxi_2026-07` | 207 M | |
| `wikipedia_en_sociology_nopic_2026-07` | 230 M | |

`maxi` variants — full articles with images — fit comfortably under the 4 GB
ceiling for topic packs. Only whole-of-Wikipedia builds are out of reach.

## Verify every archive — this step is not optional

**A truncated ZIM is structurally valid.** It opens in Kiwix, shows a proper
title and description, and is silently missing most of its content. Nothing in
the interface tells you.

```bash
cd /Volumes/CATSD/Kiwix
for f in *.zim; do
  case "$f" in wikibooks*) U="$W/$f";; wikipedia*) U="$P/$f";; *) U="$O/$f";; esac
  R=$(curl -sIL "$U" | grep -i '^content-length:' | tail -1 | awk '{print $2}' | tr -d '\r')
  L=$(stat -f%z "$f")
  [ "$L" = "$R" ] && echo "OK       $f" || echo "MISMATCH $f  local=$L remote=$R"
done
```

On this build Appropedia arrived at 39% of its true size and would have shipped
that way. It is the water-treatment archive.

**Check the build host's free space before starting.** `curl` writing to a full
disk produces partial files without failing loudly:

```bash
df -h /System/Volumes/Data
```

## Scripture

**AndBible** — install from the F-Droid app on the phone so it picks the
matching ABI automatically. Full translations, verse navigation, search.

**Plus plain text**, so it survives any app failure:

```bash
curl -L -o /Volumes/CATSD/Reference/kjv-bible.txt \
  https://www.gutenberg.org/cache/epub/10/pg10.txt
```

## Kiwix does not organise anything

It reads titles from ZIM metadata and shows one flat list — no folders, tags or
ordering, and renaming a file changes nothing because the label is embedded.

`Reference/CATALOG.md` fills that gap: a "where do I look for X" index pointing
each need at the archive that answers it, plus the honest limits. It is plain
markdown, so `vs` searches it offline.

## Eject cleanly

```bash
sudo mdutil -i off /Volumes/CATSD   # stop Spotlight indexing 18 GB
cd ~
diskutil unmountDisk /dev/disk4
```

Spotlight indexing is what blocks the eject. If the card is ever pulled without
unmounting, check it before trusting it — FAT32 has no journal:

```bash
diskutil verifyVolume /Volumes/CATSD
```

## Result

Card back in the phone, open Kiwix, pull down to refresh the Library tab.
Eighteen archives populate with real titles. Searching "water purification" in
Appropedia returns results with every radio off.

## Known gap

**No usable offline plant identification.** Wikispecies is taxonomy — Latin
names and classification, not edibility. Every plant-ID app does recognition in
the cloud. Carry a paper regional field guide.


---

# Maps — 83 US regions, 29.6 GiB

Kiwix answers "what is this." OsmAnd answers "where am I." Both had to move to
the card; only one of them was straightforward.

## Move OsmAnd's data folder first

Settings -> OsmAnd settings -> Data storage folder -> **External storage 2**.

"External storage 1" is the 11.38 GB internal volume, which cannot hold the US.
"External storage 2" is the card, with 99 GB free. Switching triggers a
migration of the existing map data — let it finish completely before touching
the card, and force-close OsmAnd and power the phone off before removing it.
FAT32 has no journal.

## The destination is not the obvious one

```
/Android/data/net.osmand.plus/files/
```

**`net.osmand.plus`**, not `net.osmand`. The suffix is the Play Store package
identifier; the F-Droid build uses a different one. Copy into the wrong
directory and the files sit on the card, occupying space, invisible to the app
forever.

Verify the real path on the card rather than assuming it:

```bash
ls -d /Volumes/CATSD/Android/data/*osmand*
```

## OsmAnd strips the `_2` suffix

Downloaded archives are named `Us_virginia_northamerica_2.obf.zip`. What OsmAnd
writes after installing is `Us_virginia_northamerica.obf` — the `_2` is a map
format version marker in the download name, not part of the installed name.

This was not guesswork. Virginia had already migrated to the card, and it was
byte-identical in size to the unzipped `_2` file on the Mac, with matching
hashes at head, middle and tail. Same file, different name.

**Copy all regions with `_2` stripped** so they match how OsmAnd names its own
downloads, and skip any region already present — otherwise the same map loads
twice under two names.

## Copy and verify

```bash
COPYFILE_DISABLE=1 cp ~/Downloads/osm/*.obf \
  /Volumes/CATSD/Android/data/net.osmand.plus/files/
dot_clean -m /Volumes/CATSD
```

`COPYFILE_DISABLE=1` suppresses AppleDouble sidecars. Without it macOS writes a
`._Us_alabama_northamerica.obf` next to every map and OsmAnd sees 166 files
instead of 83.

Every file was written as `NAME.obf.part` and renamed only after its byte count
matched the source. A killed or failed copy can never masquerade as a finished
map — the Phase 04 verification rule applied to writes as well as downloads.

## Result

| | |
|---|---|
| Regions on card | 83 states and metro areas + `World_basemap_mini` |
| Total | 29.57 GiB |
| Size verification | 83/83 exact match, 0 mismatches, 0 missing |
| Content spot-check | 7 files, head/middle/tail hashes, all matching |
| Largest single file | `Us_north-carolina_northamerica.obf`, 1.1 GB |
| Card remaining | 70 GB free |

No file approaches the FAT32 4 GB ceiling — the largest US region is 1.1 GB, so
maps never hit the constraint that forced curated sub-4 GB ZIM packs.

## A verification that passes on nothing is not a verification

The content spot-check initially reported `CONTENT-MATCH` for a New York file
that does not exist. Both hashes were `d41d8cd98f00b204e9800998ecf8427e` — the
MD5 of empty input. Two unreadable files hash identically and the comparison
returns true.

New York is not one region; it is five (`albany`, `buffalo`,
`new-york-city`, `syracuse`, `utica`). The guessed filename matched nothing on
either side, and the test reported success.

Any integrity check has to assert the input was non-empty before comparing:

```bash
[ ! -s "$a" ] || [ ! -s "$b" ] && { echo "SKIP-UNREADABLE"; continue; }
```

Fourth way a library lies, and this one was the test lying, not the data.
