#!/usr/bin/env bash
# card-manifest.sh — run on the MAC with the card mounted.
#
# Termux cannot read Android/data on Android 11, so the phone can never count
# its own maps. The Mac can. This writes a record the phone CAN read, and a
# size manifest that makes bit rot and truncation detectable later.
#
#   ./card-manifest.sh                 record counts and file sizes
#   ./card-manifest.sh --checksums     also SHA-256 every map (slow: ~30 GB)
set -euo pipefail
CARD="${CARD:-/Volumes/CATSD}"
MAPS="$CARD/Android/data/net.osmand.plus/files"
ZIMS="$CARD/Kiwix"
REF="$CARD/Reference"

[ -d "$CARD" ] || { echo "card not mounted at $CARD" >&2; exit 1; }
[ -d "$MAPS" ] || { echo "no OsmAnd data dir at $MAPS" >&2; exit 1; }
mkdir -p "$REF"

obf=$(find "$MAPS" -maxdepth 1 -name '*.obf' | wc -l | tr -d ' ')
zim=$(find "$ZIMS" -maxdepth 1 -name '*.zim' 2>/dev/null | wc -l | tr -d ' ')
bytes=$(find "$MAPS" -maxdepth 1 -name '*.obf' -print0 | xargs -0 stat -f%z | awk '{s+=$1} END{print s+0}')

{
  echo "# written by card-manifest.sh — read by status(1) on the phone"
  echo "written=$(date '+%Y-%m-%d')"
  echo "count=$obf"
  echo "bytes=$bytes"
  echo "zims=$zim"
  echo "path=$MAPS"
} > "$REF/MAPS.manifest"

find "$MAPS" -maxdepth 1 -name '*.obf' -print0 \
  | xargs -0 stat -f'%z  %N' \
  | sed "s|$MAPS/||" | sort -k2 > "$REF/MAPS.sizes"

if [ "${1:-}" = "--checksums" ]; then
  echo "hashing $obf maps — this takes a while"
  ( cd "$MAPS" && shasum -a 256 ./*.obf ) > "$REF/MAPS.sha256"
  echo "wrote $REF/MAPS.sha256"
fi

echo "wrote $REF/MAPS.manifest  ($obf maps, $zim zims)"
echo "wrote $REF/MAPS.sizes"
