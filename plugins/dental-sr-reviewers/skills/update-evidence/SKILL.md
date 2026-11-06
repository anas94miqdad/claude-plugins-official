---
name: update-evidence
description: Update the evidence base of Reviewer A and Reviewer B with newly published methodological guidance and dental research (PRISMA/Cochrane/GRADE/risk-of-bias updates, AI-in-evidence-synthesis guidance, LLM screening evaluations, new dental classifications, guidelines and reporting standards). Searches PubMed since the last update, verifies every PMID/DOI and records dated, versioned entries. Use when the user asks to update or refresh the reviewers' knowledge, or periodically (e.g. monthly).
argument-hint: "[optional topic, e.g. 'peri-implantitis' or 'ROBINS-I'] [--since YYYY-MM-DD]"
---

# Wissensbasis aktualisieren (evidenzbasiert, versioniert)

Argumente: `$ARGUMENTS`

Ziel: Reviewer A und B sollen methodisch und fachlich auf dem aktuellen Stand bleiben, ohne dass
je eine unbelegte Aussage in die Wissensbasis gelangt.

## Dateien

- Ausgelieferte Basis (nur lesen): `${CLAUDE_PLUGIN_ROOT}/skills/sr-methodology/references/evidence-base.md`
  – Stand-Datum steht im Kopf („Stand der Literaturprüfung“).
- Lokale Updates (persistent über Plugin-Updates hinweg): `${CLAUDE_PLUGIN_DATA}/evidence-updates.md`
  – Datei anlegen, falls nicht vorhanden. Kopf: `# Evidence updates` + Zeile `last_checked: <Datum>`.
- Optional (wenn der Nutzer im Plugin-Repository arbeitet und das wünscht): Änderungen direkt in
  `plugins/dental-sr-reviewers/skills/sr-methodology/references/evidence-base.md` und
  `changelog.md` einpflegen, Version erhöhen (`JJJJ.MM.n`), committen. Dann erhalten alle
  Installationen das Update.

## Ablauf

1. **Zeitraum bestimmen:** `--since` oder `last_checked` aus `evidence-updates.md`, sonst das
   Stand-Datum der Basis.
2. **Suchen** (PubMed-Connector bevorzugt; sonst Amass/Consensus/Websuche). Verwende
   Datumsfilter auf den Zeitraum. Standard-Suchblöcke:
   - Reporting/Methodik: `PRISMA[ti] AND (extension OR update OR statement)`;
     `Cochrane Handbook`; `AMSTAR`; `ROBIS`; `"risk of bias" AND tool AND (development OR version)`;
     `GRADE[ti] AND (guidance OR "Core GRADE")`; `CONSORT OR SPIRIT OR STROBE OR STARD OR TRIPOD` (Updates).
   - KI in Evidenzsynthese: `(large language model* OR ChatGPT OR GPT-4 OR Claude OR LLM) AND
     (systematic review* OR screening) AND (title OR abstract OR eligibility)`;
     `artificial intelligence AND evidence synthesis AND (guidance OR position statement OR RAISE)`.
   - Zahnmedizin-Methodik: `(dentistry OR dental OR periodont* OR endodont* OR orthodont* OR
     implant*) AND (systematic reviews as topic OR "methodological quality" OR "reporting quality")`.
   - Zahnmedizin-Klassifikationen/Leitlinien: `(consensus report OR S3 guideline OR classification)
     AND (periodont* OR peri-implant* OR caries OR endodont* OR temporomandibular)`;
     Core Outcome Sets: `core outcome set AND (dental OR periodontal OR implant OR endodontic)`.
   - Projektspezifisch: das vom Nutzer genannte Thema.
3. **Filtern:** Nur aufnehmen, was die Screening- oder Berichtspraxis tatsächlich ändert
   (neue/aktualisierte Leitlinie, neues Tool, Positionspapier, hochwertige Methodenstudie,
   Metaanalyse zu KI-Screening, neue Klassifikation/Falldefinition). Keine Einzelfall-Studien
   zu klinischen Fragen.
4. **Verifizieren:** Für jeden Kandidaten Metadaten über PubMed (PMID) bzw. DOI abrufen. Titel,
   Journal, Jahr, Band/Seiten exakt übernehmen. Retraction-Status prüfen. Nicht verifizierbar →
   nicht aufnehmen (höchstens in „Kandidaten, unverifiziert“ ohne Zitierfreigabe).
5. **Bewerten:** Kurz begründen, was sich für die Reviewer ändert (1–2 Sätze), und ob ein
   bestehender Eintrag **ersetzt** wird (z. B. „ersetzt E3 ROBINS-I V2 Tool-Dokument“).
6. **Schreiben** in `${CLAUDE_PLUGIN_DATA}/evidence-updates.md`:

   ```
   ## <Datum> – Update <JJJJ.MM.n>
   | # | Quelle (Vancouver) | PMID | DOI | Kategorie (A–H) | Konsequenz für das Screening | ersetzt |
   ```

   und `last_checked` aktualisieren. Auch „keine relevanten Neuerungen gefunden“ dokumentieren
   (mit Suchstrings und Trefferzahlen) – das ist ein Nachweis der Aktualität.
7. **Offene Verifikationen** aus `evidence-base.md` Abschnitt I abarbeiten, wenn Zeit ist.
8. **Bericht an den Nutzer** (Deutsch): neue Einträge, geänderte Empfehlungen, ob laufende
   Projekte betroffen sind (z. B. Protokoll-Amendment nötig?).

## Regelmäßige Aktualisierung

Empfehle dem Nutzer bei Bedarf eine monatliche Ausführung (z. B. als geplante Aufgabe in
Claude Code oder durch erneuten Aufruf dieses Skills). Für claude.ai-Projekte: das Ergebnis
`evidence-updates.md` als Projektwissen hochladen oder die Skills neu bauen
(siehe README, Abschnitt „claude.ai“).

## Regeln

- Keine Referenz ohne Verifikation. Keine PMIDs/DOIs aus dem Gedächtnis.
- Bestehende Einträge nicht löschen; ersetzte Einträge als „ersetzt durch …“ markieren.
- Preprints (medRxiv/bioRxiv) nur als „Preprint – nicht peer-reviewed“ kennzeichnen.
