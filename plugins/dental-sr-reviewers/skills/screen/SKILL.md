---
name: screen
description: Run a complete dual, independent and parallel PRISMA 2020-compliant screening workflow for a dental systematic review - Reviewer A and Reviewer B screen the same records simultaneously in separate, technically blinded workspaces (protocol check, de-duplication, calibration, title/abstract screening, parallel consensus statements, human arbitration, full-text screening, audit trail with Cohen's kappa). Use when the user asks to screen search results (RIS/CSV export) or to start/continue screening for a systematic review.
argument-hint: "[path to RIS/CSV export(s) or screening folder] [--stage pilot|tiab|fulltext]"
---

# Paralleles, unabhängiges Doppelscreening mit Reviewer A und Reviewer B

Argumente des Nutzers: `$ARGUMENTS`

Du bist der **Koordinator** (nicht selbst Reviewer). Du bereitest Daten vor, startest Reviewer A
und Reviewer B **gleichzeitig und unabhängig**, überwachst den Fortschritt, führst Abgleich und
Statistik durch und hältst den Audit-Trail. Eligibility-Entscheidungen treffen ausschließlich
Reviewer A, Reviewer B und – bei ungelösten Konflikten – der menschliche Arbiter (Nutzer).

- Werkzeug: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/screen/scripts/screening_tools.py <subcommand>`
  (im Folgenden `ST`)
- Methodik: `${CLAUDE_PLUGIN_ROOT}/skills/sr-methodology/references/screening-protocol.md`
- Agenten (Agent-Tool, `subagent_type`): `dental-sr-reviewers:reviewer-a`, `dental-sr-reviewers:reviewer-b`.
  Nur diese beiden verwenden: Die technische Verblindung (Plugin-Hook
  `${CLAUDE_PLUGIN_ROOT}/hooks/blinding_guard.py`) greift nur für diese Agenten-Typen. Sind sie nicht
  verfügbar, abbrechen und den Nutzer bitten, das Plugin zu installieren/aktivieren.

## Ordnerstruktur (parallel, kollisionsfrei)

```
screening/
├── protocol_snapshot.md            # freigegebenes Protokoll (Version, Datum, Amendments)
├── records.csv, records_all.csv    # nach Deduplikation / vollständig
├── batches/  batches_pilot/  batches_fulltext/          # Eingaben (von dir erzeugt)
├── reviewer_A/  pilot/ tiab/ fulltext/  consensus_<stage>.csv  log.md   # nur Reviewer A schreibt hier
├── reviewer_B/  pilot/ tiab/ fulltext/  consensus_<stage>.csv  log.md   # nur Reviewer B schreibt hier
├── merged_*, conflicts_*, agreement_*, consensus_*, arbiter_*, final_*  # nur du schreibst hier
├── .consensus_open                 # Marker: existiert nur während der Konsensphase
└── screening_log.md                # dein Koordinations-Log
```

Jede Reviewer-Ergebnisdatei heißt wie der Eingabe-Batch (`batch_007.csv`). Kein gemeinsames
Anhängen an Dateien → keine Schreibkonflikte bei paralleler Arbeit.

---

## Schritt 0 – Projekt und Protokoll

1. Arbeitsordner `screening/` (oder vom Nutzer genannter Pfad). Existiert er, lies
   `screening/screening_log.md` und führe `ST status --stage <stage>` aus, um an der richtigen
   Stelle fortzusetzen.
2. Prüfe `screening/protocol_snapshot.md`. Fehlt es:
   - Forschungsfrage, PICO/PECO/PIRD, Designs, Registrierung, Sprach-/Zeitlimits erfragen.
   - **Reviewer A und B parallel** (zwei Agent-Aufrufe in derselben Nachricht) je einen
     unabhängigen Kriterien-Entwurf schreiben lassen (`screening/reviewer_<X>/protocol_draft.md`).
   - Beide Entwürfe vergleichen, Unterschiede als Entscheidungsfragen dem Nutzer vorlegen,
     nach **Freigabe** `protocol_snapshot.md` (v1.0, Datum) schreiben. Ohne Freigabe kein Screening.
3. Log-Eintrag: Datum, Modell, Plugin-Version (`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`),
   Protokollversion.

## Schritt 1 – Daten vorbereiten

```
ST prepare <exports...> --out screening --batch-size 40
```

Zusammenfassung berichten; auf konservative Deduplikation hinweisen (endgültig im
Literaturverwaltungsprogramm bestätigen). Zahlen für PRISMA notieren.

## Schritt 2 – So startest du die Reviewer parallel (gilt für alle Stufen)

1. **Arbeitspakete bilden:** Batches der Stufe auf Pakete verteilen. Standard: alle Batches in
   **ein Paket je Reviewer**; bei > 5 Batches mehrere Pakete (je 3–5 Batches) – dann laufen
   mehrere Instanzen desselben Reviewers gleichzeitig. Reviewer A und B bekommen **dieselbe
   Paketaufteilung**.
2. **Gleichzeitig starten:** Alle Agent-Aufrufe einer Welle in **einer einzigen Nachricht** senden,
   jeweils mit `run_in_background: true`. Pro Welle höchstens 6 Agenten (z. B. 3× A + 3× B).
   Prompt je Agent (nur Pfade, keine Informationen über den anderen Reviewer):

   > Stage: `<pilot|tiab|fulltext>`. Projektprotokoll: `screening/protocol_snapshot.md`.
   > Deine Eingabe-Batches: `screening/batches/batch_001.csv`, `…_002.csv`.
   > Schreibe je Batch `screening/reviewer_<X>/<stage>/<gleicher Dateiname>`, Log in
   > `screening/reviewer_<X>/log.md`. Screene unabhängig gemäß deiner SOP.

   Volltext-Stufe: zusätzlich die Spalte `fulltext_path` in den Batches nennen (PDFs unter
   `screening/fulltexts/<record_id>.pdf`).
3. **Warten statt pollen:** Du wirst benachrichtigt, wenn ein Agent fertig ist. Danach
   `ST status --stage <stage>`. Offene/unvollständige Batches (`open_A`, `open_B`) in einer neuen
   Welle gezielt nachreichen – nur an den Reviewer, dem sie fehlen.
4. **Nie** einem Reviewer Ergebnisse, Zählungen oder Auffälligkeiten des anderen weitergeben,
   bevor `ready_to_merge: true` erreicht ist. Kriterienprobleme, die ein Reviewer meldet, sammelst
   du und legst sie erst nach der Runde dem Nutzer vor (ggf. Amendment für die **nächste** Stufe).

## Schritt 3 – Kalibrierung (Pilot)

1. `ST make-batches pilot --records screening/records.csv --out screening/batches_pilot`
   (Stichprobe: 50–100 bzw. 10 % bei < 500; Seed wird ausgegeben → im Log notieren).
2. Reviewer A und B parallel nach Schritt 2 (Stage `pilot`).
3. `ST status --stage pilot` → bei `ready_to_merge`:
   `ST merge --a screening/reviewer_A/pilot --b screening/reviewer_B/pilot --stage pilot --records screening/records.csv --out screening`
4. κ ≥ 0,60? Sonst Konflikte analysieren, Kriterien-Amendment dem Nutzer vorlegen (v1.1 …),
   neue Stichprobe (`--seed` ändern), Pilot wiederholen.
5. Empfehlen: Der Nutzer screent dieselbe Stichprobe selbst → Sensitivität/Spezifität der
   KI-Reviewer gegenüber menschlichem Urteil berichten (evidence-base D1, D8).

## Schritt 4 – Titel/Abstract-Screening

1. Reviewer A und B parallel nach Schritt 2 (Stage `tiab`, Batches `screening/batches/`).
2. Wiederholen, bis `ST status --stage tiab` `ready_to_merge: true` meldet.
3. `ST merge --a screening/reviewer_A/tiab --b screening/reviewer_B/tiab --stage tiab --records screening/records.csv --out screening`
4. Berichten: Übereinstimmung, κ (95 %-KI), PABAK, Anzahl Konflikte.

## Schritt 5 – Konsens (ebenfalls parallel und unabhängig)

1. Konsensphase öffnen: leere Datei `screening/.consensus_open` anlegen (erst jetzt dürfen die
   Reviewer `conflicts_<stage>.csv` lesen).
2. Reviewer A und B **parallel** beauftragen: „Konsensphase Stage `<stage>`: Lies
   `screening/conflicts_<stage>.csv` und schreibe deine Stellungnahmen nach
   `screening/reviewer_<X>/consensus_<stage>.csv`.“
3. `ST consensus-merge --conflicts screening/conflicts_<stage>.csv --a screening/reviewer_A/consensus_<stage>.csv --b screening/reviewer_B/consensus_<stage>.csv --stage <stage> --out screening/consensus_<stage>.csv --arbiter-out screening/arbiter_<stage>.csv`
   – gleiche Positionen = Konsens; Ti/Ab ohne Ausschlussvotum → Volltext.
4. Verbleibende Fälle (`arbiter_<stage>.csv`) dem Nutzer als **Arbiter** vorlegen (beide Argumente
   zeigen; AskUserQuestion bei wenigen Fällen, sonst Tabelle). Entscheidungen in die Datei
   eintragen (`final_decision`, `exclusion_reason`, `resolved_by` = `arbiter (<Initialen>)`).
5. `ST apply-consensus --merged screening/merged_<stage>.csv --consensus screening/consensus_<stage>.csv screening/arbiter_<stage>.csv --out screening/final_<stage>.csv`
6. Konsensphase schließen: `screening/.consensus_open` löschen.

## Schritt 6 – Volltext-Screening

1. `ST make-batches fulltext --records screening/records.csv --final screening/final_tiab.csv --out screening/batches_fulltext --batch-size 10`
2. Volltexte beschaffen: Nutzer legt PDFs als `screening/fulltexts/<record_id>.pdf` ab; frei
   verfügbare Volltexte ggf. über PubMed Central. Nicht beschaffbare → `reports_not_retrieved`
   (Kontaktversuche dokumentieren) und aus den Batches nehmen.
3. Reviewer A und B parallel nach Schritt 2 (Stage `fulltext`); genau ein hierarchischer
   Ausschlussgrund + Fundstelle.
4. Abgleich und Konsens wie Schritte 4–5 mit `--stage fulltext`.
5. Zuordnung Reports → Studien in `screening/study_report_links.csv`;
   `screening/excluded_fulltexts.md` gemäß `reporting-templates.md` §4.

## Schritt 7 – Abschluss

- `/dental-sr-reviewers:prisma-report` (Flussdiagramm, Methods/Results, KI-Offenlegung).
- Optional: `ST export-asreview --records screening/records.csv --final screening/final_tiab.csv --out screening/asreview_import.csv`.
- Abschlussbericht (Deutsch): Zahlen je Stufe, κ-Werte, Konflikte und Lösung, offene Punkte,
  Hinweis auf menschliche Verantwortung und Offenlegungspflicht.

## Regeln für dich als Koordinator

- Verändere niemals Dateien in `reviewer_A/` oder `reviewer_B/`.
- `.consensus_open` existiert nur zwischen Schritt 5.1 und 5.6 – nie während einer Screening-Runde.
- Alle Zahlen in Berichten stammen aus Skript-Ausgaben, nicht aus Schätzungen.
- Jeder Schritt (Welle, Pakete, Agenten, Status) wird in `screening/screening_log.md` protokolliert.
