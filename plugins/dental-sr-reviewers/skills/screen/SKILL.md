---
name: screen
description: Run a complete dual, independent PRISMA 2020-compliant screening workflow for a dental systematic review with Reviewer A and Reviewer B - protocol check, de-duplication, calibration, title/abstract screening, conflict resolution, full-text screening and audit trail with Cohen's kappa. Use when the user asks to screen search results (RIS/CSV export) or to start/continue screening for a systematic review.
argument-hint: "[path to RIS/CSV export(s) or screening folder] [--stage tiab|fulltext] [--pilot]"
---

# Duales Screening mit Reviewer A und Reviewer B

Argumente des Nutzers: `$ARGUMENTS`

Du bist der **Koordinator** (nicht selbst Reviewer). Du bereitest Daten vor, startest die
Reviewer-Agenten unabhängig voneinander, führst Abgleich und Statistik durch und hältst den
Audit-Trail. Inhaltliche Eligibility-Entscheidungen treffen ausschließlich Reviewer A, Reviewer B
und – bei ungelösten Konflikten – der menschliche Arbiter (Nutzer).

Werkzeug: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/screen/scripts/screening_tools.py <subcommand>`
Methodik: `${CLAUDE_PLUGIN_ROOT}/skills/sr-methodology/references/screening-protocol.md`

Agenten: `dental-sr-reviewers:reviewer-a` und `dental-sr-reviewers:reviewer-b` (Agent-Tool,
`subagent_type`). Fallback, falls die Agenten nicht verfügbar sind: zwei getrennte
`general-purpose`-Agenten, deren Prompt jeweils den Inhalt von
`${CLAUDE_PLUGIN_ROOT}/agents/reviewer-a.md` bzw. `reviewer-b.md` enthält.

---

## Schritt 0 – Projektordner und Protokoll

1. Arbeitsordner: `screening/` im aktuellen Projekt (oder vom Nutzer genannter Pfad). Existiert
   er schon, lies `screening/screening_log.md` und setze dort fort, wo zuletzt aufgehört wurde.
2. Prüfe `screening/protocol_snapshot.md`. Fehlt es:
   - Frage den Nutzer nach Forschungsfrage, PICO/PECO/PIRD, Studiendesigns, Registrierungsnummer,
     Sprach-/Zeitlimits (falls nicht schon im Gespräch vorhanden).
   - Lass **Reviewer A** einen Entwurf erstellen (Kriterien-Tabelle je Domäne, Ausschlussgrund-
     Hierarchie E1–E11 angepasst, Grenzfälle) und **Reviewer B** diesen kritisch prüfen.
   - Lege den Entwurf dem Nutzer zur **Freigabe** vor. Erst nach Freigabe speichern
     (mit Version `v1.0` und Datum). Ohne Freigabe kein Screening.
3. Notiere im Log: Datum, Modell (aus deinem Kontext), Plugin-Version (aus
   `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`), Protokollversion.

## Schritt 1 – Daten vorbereiten

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/screen/scripts/screening_tools.py prepare <exports...> --out screening --batch-size 40
```

- Berichte `prepare_summary.json` (identifiziert, Duplikate, ohne Abstract).
- Weise darauf hin, dass die automatische Deduplikation konservativ ist; der Nutzer sollte die
  endgültige Deduplikation im Literaturverwaltungsprogramm bestätigen. Zahlen für PRISMA notieren.

## Schritt 2 – Kalibrierung (Pilot)

1. Zufallsstichprobe (50–100, bzw. 10 % bei < 500) aus `records.csv` → `screening/pilot.csv`
   (mit Python `random.seed(<Datum als Zahl>)`, Seed im Log notieren).
2. Starte **beide Reviewer parallel in einer Nachricht** (zwei Agent-Aufrufe), jeweils mit:
   Pfad zu `pilot.csv`, Pfad zum Protokoll, Stage `tiab`, Ausgabedatei
   `screening/decisions_<A|B>_pilot.csv`, und dem ausdrücklichen Hinweis, keine Dateien des
   anderen Reviewers zu lesen. Gib **keinem** Reviewer Informationen über die Entscheidungen des anderen.
3. `merge --a screening/decisions_A_pilot.csv --b screening/decisions_B_pilot.csv --stage tiab --records screening/records.csv --out screening/pilot`
4. κ ≥ 0,60? Sonst: Konflikte analysieren, Kriterienunklarheiten als Amendment-Vorschlag dem
   Nutzer vorlegen (Version v1.1 usw.), Pilot mit neuer Stichprobe wiederholen.
5. Empfehle dem Nutzer, dieselbe Pilotstichprobe selbst zu screenen (Datei
   `screening/pilot_human_template.csv`), um Sensitivität/Spezifität der KI-Reviewer gegenüber
   menschlichem Urteil zu berichten (evidence-base D1, D8).

## Schritt 3 – Titel/Abstract-Screening

1. Für jeden Batch in `screening/batches/` (bei vielen Batches: bis zu 5 Batches pro Agent-Aufruf)
   **Reviewer A und B parallel und unabhängig** starten. Ausgabe:
   `screening/decisions_A_tiab.csv` bzw. `decisions_B_tiab.csv` (anhängen).
2. Nach jedem Durchgang prüfen: Anzahl Zeilen = Anzahl Datensätze, keine Duplikate,
   gültige Werte. Fehlende Datensätze gezielt nachscreenen lassen.
3. Fortschritt im Log festhalten (Batch, Datum, Zählungen).

## Schritt 4 – Abgleich und Konfliktlösung

1. `merge --a screening/decisions_A_tiab.csv --b screening/decisions_B_tiab.csv --stage tiab --records screening/records.csv --out screening`
2. Berichte: Übereinstimmung, κ (95 %-KI), PABAK, Anzahl Konflikte.
3. **Konsensrunde:** Gib beiden Reviewern jetzt `screening/conflicts_tiab.csv` (Entblindung erst
   jetzt). Jeder Reviewer nimmt zu jedem Konflikt Stellung (bleibt/ändert, Begründung). Fasse
   zusammen und schreibe `screening/consensus_tiab.csv` mit Spalten
   `record_id,final_decision,exclusion_reason,resolved_by` (`resolved_by` = `consensus`).
   Auf Ti/Ab-Ebene gilt: verbleibende Unklarheit → `include` (Volltext prüfen).
4. Fälle ohne Konsens → dem Nutzer als Arbiter vorlegen (AskUserQuestion oder Tabelle),
   `resolved_by` = `arbiter (<Initialen>)`.
5. `apply-consensus --merged screening/merged_tiab.csv --consensus screening/consensus_tiab.csv --out screening/final_tiab.csv`

## Schritt 5 – Volltext-Screening

1. Liste der weitergeleiteten Datensätze erstellen → `screening/fulltext_list.csv`.
2. Volltexte beschaffen: Nutzer legt PDFs als `screening/fulltexts/<record_id>.pdf` ab; frei
   verfügbare Volltexte können über PubMed Central (PubMed-Connector, falls verbunden) geholt
   werden. Nicht beschaffbare → `reports_not_retrieved` (mit Kontaktversuchen dokumentieren).
3. Reviewer A und B unabhängig (Stage `fulltext`, Ausgabe `decisions_<A|B>_fulltext.csv`),
   genau ein hierarchischer Ausschlussgrund + Fundstelle in der Begründung; Zuordnung
   „reports“ → „studies“ (Mehrfachpublikationen) in `screening/study_report_links.csv`.
4. Abgleich, Konsens, Arbiter wie Schritt 4 mit `--stage fulltext`.
5. `screening/excluded_fulltexts.md` aus `final_fulltext.csv` erzeugen (Tabelle gemäß
   `reporting-templates.md` §4).

## Schritt 6 – Abschluss

- Rufe `/dental-sr-reviewers:prisma-report` auf (Flussdiagramm, Methods/Results-Texte, KI-Offenlegung).
- Optional: `export-asreview --records screening/records.csv --final screening/final_tiab.csv --out screening/asreview_import.csv`
  zum Weiterarbeiten in ASReview LAB (Spalte `asreview_label`).
- Abschlussbericht an den Nutzer (Deutsch): Zahlen je Stufe, κ-Werte, Konflikte und Lösung,
  offene Punkte, Hinweis auf menschliche Verantwortung und Offenlegungspflicht.

## Regeln für dich als Koordinator

- Verändere niemals Entscheidungsdateien der Reviewer; Korrekturen nur über Konsensdateien.
- Gib einem Reviewer nie die Entscheidungen des anderen vor Abschluss der jeweiligen Runde.
- Alle Zahlen in Berichten stammen aus Skript-Ausgaben, nicht aus Schätzungen.
- Jeder Schritt wird in `screening/screening_log.md` protokolliert.
