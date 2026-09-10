#!/data/data/com.termux/files/usr/bin/bash
# install.sh — put the field scripts into $PREFIX/bin.
# Run from the repo copy on the device, or after adb push.
# The card is noexec, so these must live on internal storage.
set -eu
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${PREFIX:?not running under Termux}/bin"

# adb push <dir> <dest> nests when <dest> already exists, so a second push
# lands at <dest>/scripts/ while the stale copies stay at <dest>/. Installing
# from the wrong one silently reinstalls old scripts — this catches that.
if [ -d "$SRC/scripts" ] && [ -f "$SRC/scripts/install.sh" ]; then
  echo "WARNING: $SRC/scripts/ also exists — you are probably running the STALE copy." >&2
  echo "         Newer files are likely in $SRC/scripts/. Compare timestamps before trusting this." >&2
  echo >&2
fi

for s in cap vs home status; do
  install -m 755 "$SRC/$s" "$DEST/$s"
  echo "installed $DEST/$s"
done

echo
echo "verify:"
for s in cap vs home status; do
  printf '  %-7s %s\n' "$s" "$(command -v "$s" || echo 'NOT ON PATH')"
done
