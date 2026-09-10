#!/data/data/com.termux/files/usr/bin/bash
# install.sh — put the field scripts into $PREFIX/bin.
# Run from the repo copy on the device, or after adb push.
# The card is noexec, so these must live on internal storage.
set -eu
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${PREFIX:?not running under Termux}/bin"

for s in cap vs home status; do
  install -m 755 "$SRC/$s" "$DEST/$s"
  echo "installed $DEST/$s"
done

echo
echo "verify:"
for s in cap vs home status; do
  printf '  %-7s %s\n' "$s" "$(command -v "$s" || echo 'NOT ON PATH')"
done
