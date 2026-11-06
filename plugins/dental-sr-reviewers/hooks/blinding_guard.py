#!/usr/bin/env python3
"""PreToolUse hook: enforces blinding between Reviewer A and Reviewer B.

Only acts on tool calls made *inside* the reviewer subagents
(agent_type ``dental-sr-reviewers:reviewer-a`` / ``...:reviewer-b``).
Every other tool call, including the coordinator's, passes untouched.

Rules for Reviewer X (other reviewer = Y):
  1. Never read or write anything in a ``reviewer_Y/`` folder or a file named
     ``decisions_Y_*``.
  2. Never read or write the coordinator's derived files
     (``merged_*``, ``conflicts_*``, ``final_*``, ``agreement_*``, ``consensus_*``)
     unless the coordinator has opened the consensus phase by creating the marker
     file ``.consensus_open`` in the screening folder.
  3. Never write into the coordinator's files at all (even during consensus);
     a reviewer writes only into its own folder.
  4. Shell and search tools (Bash, Glob, Grep) are denied while a screening folder
     exists, because they could reach the other reviewer's files indirectly.

Standard library only. Exit code 2 = block (reason on stderr).
"""

from __future__ import annotations

import json
import os
import re
import sys

DERIVED = re.compile(r"^(merged|conflicts|final|agreement|consensus)_", re.I)


def _reviewer(agent_type: str) -> str | None:
    at = (agent_type or "").lower()
    if at.endswith("reviewer-a"):
        return "A"
    if at.endswith("reviewer-b"):
        return "B"
    return None


def _block(msg: str) -> None:
    print(f"[Verblindung / blinding guard] {msg}", file=sys.stderr)
    sys.exit(2)


def _screening_root(path: str) -> str | None:
    """Return the nearest ancestor directory named 'screening' (or containing reviewer_* folders)."""
    p = os.path.abspath(path)
    cur = p if os.path.isdir(p) else os.path.dirname(p)
    while True:
        if os.path.basename(cur) == "screening" or os.path.isdir(os.path.join(cur, "reviewer_A")) \
                or os.path.isdir(os.path.join(cur, "reviewer_B")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def _consensus_open(path: str, cwd: str) -> bool:
    for base in (_screening_root(path), os.path.join(cwd, "screening")):
        if base and os.path.exists(os.path.join(base, ".consensus_open")):
            return True
    return False


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    me = _reviewer(data.get("agent_type", ""))
    if not me:
        sys.exit(0)
    other = "B" if me == "A" else "A"
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    cwd = data.get("cwd") or os.getcwd()

    if tool in ("Bash", "Glob", "Grep", "PowerShell"):
        if os.path.isdir(os.path.join(cwd, "screening")) or _screening_root(cwd):
            _block(
                f"Reviewer {me}: {tool} ist während des Screenings gesperrt, damit keine Dateien von "
                f"Reviewer {other} erreicht werden. Nutze Read/Write mit den exakten Pfaden, die dir "
                f"der Koordinator genannt hat."
            )
        sys.exit(0)

    path = ti.get("file_path") or ti.get("notebook_path") or ti.get("path") or ""
    if not path:
        sys.exit(0)
    full = os.path.normpath(os.path.join(cwd, path))
    parts = [s.lower() for s in full.replace("\\", "/").split("/")]
    name = os.path.basename(full)

    if f"reviewer_{other.lower()}" in parts or name.lower().startswith(f"decisions_{other.lower()}_"):
        _block(f"Reviewer {me} darf nicht auf Dateien von Reviewer {other} zugreifen: {path}")

    writing = tool in ("Write", "Edit", "MultiEdit", "NotebookEdit")
    if DERIVED.match(name):
        if writing and f"reviewer_{me.lower()}" not in parts:
            _block(
                f"Reviewer {me} schreibt nur in den eigenen Ordner screening/reviewer_{me}/ "
                f"(Konsens-Stellungnahmen als screening/reviewer_{me}/consensus_<stage>.csv)."
            )
        if not writing and f"reviewer_{me.lower()}" not in parts and not _consensus_open(full, cwd):
            _block(
                f"{name} ist erst in der Konsensphase lesbar (der Koordinator legt dafür "
                f"screening/.consensus_open an). Screene unabhängig weiter."
            )
    if writing and _screening_root(full) and f"reviewer_{me.lower()}" not in parts:
        _block(
            f"Reviewer {me} darf im Screening-Ordner nur unter screening/reviewer_{me}/ schreiben: {path}"
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
