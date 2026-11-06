#!/usr/bin/env python3
"""Build self-contained Agent Skills (ZIP) for claude.ai / Claude Desktop / Cowork.

claude.ai has no plugin subagents, so Reviewer A and Reviewer B are packaged as two
skills that each carry the shared methodology files and the screening script.
A third skill packages the coordinator workflow (merge, kappa, PRISMA).

Usage:  python3 scripts/build_claude_ai_skills.py [--out dist]
Upload: claude.ai -> Settings -> Capabilities -> Skills -> Upload skill (one ZIP per skill).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "skills" / "sr-methodology" / "references"
SCRIPT = ROOT / "skills" / "screen" / "scripts" / "screening_tools.py"

CLAUDE_AI_NOTE = """
## Nutzung in claude.ai (Projekte, Chat, Cowork)

- Die Methodikdateien liegen in diesem Skill unter `references/`, das Skript unter
  `scripts/screening_tools.py` (Code-Ausführung muss aktiviert sein).
- **Unabhängigkeit in claude.ai:** Reviewer A und Reviewer B jeweils in einem **eigenen Chat**
  arbeiten lassen (z. B. Chat „Reviewer A – Ti/Ab“ und Chat „Reviewer B – Ti/Ab“ im selben
  Projekt). Jeder Chat erzeugt seine eigene Entscheidungsdatei (CSV) zum Herunterladen. Der
  Abgleich (κ, Konflikte, PRISMA) erfolgt anschließend in einem dritten Chat mit dem Skill
  `dental-sr-coordinator`. Nie beide Rollen im selben Chat ausführen.
- Persistentes Wissen: Neuere, verifizierte Evidenz (`evidence-updates.md`) als Projektwissen
  hochladen; sie hat Vorrang vor `references/evidence-base.md`, wo sie Einträge ersetzt.
"""


def _split_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise SystemExit("missing frontmatter")
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[m.end():]


def _rewrite_paths(body: str) -> str:
    body = body.replace("${CLAUDE_PLUGIN_ROOT}/skills/sr-methodology/references/", "references/")
    body = body.replace("${CLAUDE_PLUGIN_ROOT}/skills/screen/scripts/", "scripts/")
    body = body.replace("${CLAUDE_PLUGIN_ROOT}/agents/", "(Skill) ")
    body = body.replace("`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`", "der Versionsangabe am Ende dieses Skills")
    body = body.replace(
        "`${CLAUDE_PLUGIN_DATA}/evidence-updates.md`",
        "die Projektwissen-Datei `evidence-updates.md`",
    )
    body = body.replace("${CLAUDE_PLUGIN_DATA}/evidence-updates.md", "evidence-updates.md (Projektwissen)")
    body = body.replace("/dental-sr-reviewers:update-evidence", "den Skill `dental-sr-update-evidence`")
    body = body.replace("/dental-sr-reviewers:prisma-report", "den Skill `dental-sr-coordinator` (PRISMA-Bericht)")
    body = body.replace("/dental-sr-reviewers:screen", "den Skill `dental-sr-coordinator`")
    return body


def _skill_md(name: str, description: str, body: str) -> str:
    description = description.replace("\n", " ").strip()
    if len(description) > 1024:
        description = description[:1020].rsplit(" ", 1)[0] + " ..."
    desc_yaml = json.dumps(description, ensure_ascii=False)
    return f"---\nname: {name}\ndescription: {desc_yaml}\n---\n{body}"


def _package(out: Path, name: str, skill_md: str, with_refs=True, with_script=True) -> Path:
    d = out / name
    if d.exists():
        shutil.rmtree(d)
    (d).mkdir(parents=True)
    (d / "SKILL.md").write_text(skill_md, encoding="utf-8")
    if with_refs:
        shutil.copytree(REFS, d / "references")
    if with_script:
        (d / "scripts").mkdir()
        shutil.copy2(SCRIPT, d / "scripts" / SCRIPT.name)
    z = out / f"{name}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(d.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(out))
    return z


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    version = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]
    built = []

    for agent, skill_name in (("reviewer-a", "dental-sr-reviewer-a"), ("reviewer-b", "dental-sr-reviewer-b")):
        fm, body = _split_frontmatter((ROOT / "agents" / f"{agent}.md").read_text(encoding="utf-8"))
        body = _rewrite_paths(body) + CLAUDE_AI_NOTE + f"\n_Version {version}_\n"
        built.append(_package(out, skill_name, _skill_md(skill_name, fm["description"], body)))

    # Coordinator = screen + prisma-report workflow
    _, screen = _split_frontmatter((ROOT / "skills" / "screen" / "SKILL.md").read_text(encoding="utf-8"))
    _, prisma = _split_frontmatter((ROOT / "skills" / "prisma-report" / "SKILL.md").read_text(encoding="utf-8"))
    coord_body = _rewrite_paths(
        screen.replace("Argumente des Nutzers: `$ARGUMENTS`", "")
        + "\n\n---\n\n"
        + prisma.replace("Argumente: `$ARGUMENTS` (Standardordner: `screening/`)", "")
    )
    coord_body += """
## Besonderheit claude.ai

Es gibt hier keine Subagenten. Starte die Reviewer daher nicht selbst, sondern bitte den Nutzer,
Reviewer A und Reviewer B in **getrennten Chats** (Skills `dental-sr-reviewer-a` /
`dental-sr-reviewer-b`) mit derselben Batch-Datei auszuführen und die beiden CSV-Dateien hier
hochzuladen. Danach Abgleich, κ, Konfliktliste und PRISMA mit `scripts/screening_tools.py`.
"""
    built.append(_package(out, "dental-sr-coordinator", _skill_md(
        "dental-sr-coordinator",
        "Coordinator for dual independent screening in dental systematic reviews with Reviewer A and "
        "Reviewer B: prepares and de-duplicates RIS/CSV exports into batches, merges the two reviewers' "
        "decision files, computes Cohen's kappa (95% CI) and PABAK, lists conflicts for consensus, "
        "checks PRISMA 2020 counts and drafts the flow diagram, Methods/Results text with AI-use "
        "disclosure and the excluded-studies table. Use when screening results need to be prepared, "
        "merged or reported.",
        coord_body + f"\n_Version {version}_\n")))

    _, upd = _split_frontmatter((ROOT / "skills" / "update-evidence" / "SKILL.md").read_text(encoding="utf-8"))
    upd = _rewrite_paths(upd.replace("Argumente: `$ARGUMENTS`", ""))
    upd += """
## Besonderheit claude.ai

Ergebnis als Datei `evidence-updates.md` erzeugen (bestehende Version aus dem Projektwissen
fortschreiben) und den Nutzer bitten, sie im Projekt als Wissen zu ersetzen.
"""
    built.append(_package(out, "dental-sr-update-evidence", _skill_md(
        "dental-sr-update-evidence",
        "Update the evidence base of the dental systematic-review reviewers (Reviewer A and B): searches "
        "PubMed for new methodological guidance (PRISMA, Cochrane, GRADE, risk-of-bias tools, AI in "
        "evidence synthesis, LLM screening studies) and new dental classifications, guidelines and core "
        "outcome sets since the last check, verifies every PMID/DOI and writes a dated, versioned "
        "evidence-updates.md. Use when asked to refresh or update the reviewers' knowledge.",
        upd + f"\n_Version {version}_\n"), with_script=False))

    for z in built:
        print(z)


if __name__ == "__main__":
    main()
