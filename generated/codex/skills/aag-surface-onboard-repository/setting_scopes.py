#!/usr/bin/env python3
"""Report where each editor setting key is contributed and at which scope.

Usage: python3 setting_scopes.py <key> [<key> ...]

Scans the manifests of installed Cursor/VS Code extensions and the built-in
extensions shipped with the application. For each key prints the contributing
extension, the declared scope, and whether the key may be set in a folder's
.vscode/settings.json inside a multi-root workspace. Keys that are not found
are reported so they are not written blindly.

Only resource, language-overridable, and machine-overridable scopes take
effect in folder settings. window, machine, and application scopes must live
in the .code-workspace settings block or user settings.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
import glob
import json
import os
import shutil
import sys

FOLDER_OK = {"resource", "language-overridable", "machine-overridable"}


def manifest_paths(editor: str, profile: str | None = None) -> list[str]:
    executable = shutil.which(editor)
    if not executable:
        raise ValueError(f"Editor not found: {editor}")
    command = [executable]
    if profile:
        # Listing extensions must target an existing profile; callers confirm it first.
        command += ["--profile", profile]
    def run(*args):
        result = subprocess.run(command + list(args), text=True, capture_output=True, timeout=30)
        if result.returncode:
            raise ValueError(result.stderr.strip() or "Editor discovery failed")
        return result.stdout.strip()
    paths = []
    for entry in run("--list-extensions", "--show-versions").splitlines():
        if "@" not in entry:
            raise ValueError(f"Unexpected extension listing: {entry}")
        identifier, version = entry.rsplit("@", 1)
        location = Path(run("--locate-extension", identifier))
        manifest = location / "package.json"
        data = json.loads(manifest.read_text())
        if data.get("version") != version:
            raise ValueError(f"Extension version mismatch: {identifier}")
        paths.append(str(manifest))
    app = Path(executable).resolve().parent.parent / "resources" / "app" / "extensions"
    if not app.is_dir():
        raise ValueError("Cannot locate built-in extensions for selected editor")
    paths += [str(path) for path in sorted(app.glob("*/package.json"))]
    return paths


def main(keys: list[str], editor: str, profile: str | None = None) -> int:
    if not keys:
        print(__doc__.strip())
        return 2
    # Core declaration inherits LANGUAGE_OVERRIDABLE from editorConfigurationBaseNode:
    # https://github.com/microsoft/vscode/blob/main/src/vs/editor/common/config/editorConfigurationSchema.ts
    found: dict[str, tuple[str, str]] = {"editor.defaultFormatter": ("editor-core", "language-overridable")}
    conflicts = set()
    for path in manifest_paths(editor, profile):
        try:
            with open(path, encoding="utf-8") as handle:
                manifest = json.load(handle)
        except (OSError, ValueError) as error:
            raise ValueError(f"Cannot read manifest {path}: {error}") from error
        conf = manifest.get("contributes", {}).get("configuration", [])
        if isinstance(conf, dict):
            conf = [conf]
        for block in conf:
            for key, spec in block.get("properties", {}).items():
                if key in keys:
                    scope = spec.get("scope", "window")
                    value = (manifest.get("publisher", "") + "." + manifest.get("name", ""), scope)
                    if key in found and found[key] != value:
                        conflicts.add(key)
                    found[key] = value
    status = 0
    for key in keys:
        if key in conflicts:
            print(f"{key}\t-\tAMBIGUOUS\t-")
            status = 1
        elif key in found:
            ext, scope = found[key]
            where = "folder-ok" if scope in FOLDER_OK else "NOT-FOLDER"
            print(f"{key}\t{scope}\t{where}\t{ext}")
        else:
            print(f"{key}\t-\tNOT-FOUND\t-")
            status = 1
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor", choices=("cursor", "code"), required=True)
    parser.add_argument("--profile", help="Existing local profile name")
    parser.add_argument("keys", nargs="+")
    args = parser.parse_args()
    try:
        sys.exit(main(args.keys, args.editor, args.profile))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Discovery failed: {error}", file=sys.stderr)
        sys.exit(2)
