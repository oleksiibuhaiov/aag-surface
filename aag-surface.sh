#!/bin/sh
set -eu
aag_surface_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
exec python3 "$aag_surface_root/scripts/aag-surface.py" "$@"
