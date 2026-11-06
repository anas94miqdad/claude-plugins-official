---
name: prisma-report
description: Produce publication-ready PRISMA 2020 outputs for a dental systematic review from the screening audit trail - consistency-checked flow diagram (SVG), Methods text for the selection process including AI-use disclosure, Results text for study selection with kappa values, table of excluded full-text reports with reasons, and a screening-related submission checklist. Use after screening with Reviewer A and B, or when the user asks for a PRISMA flow diagram or selection-process write-up.
argument-hint: "[screening folder, default ./screening]"
---

# PRISMA-2020-Bericht aus dem Screening-Audit-Trail

Argumente: `$ARGUMENTS` (Standardordner: `screening/`)

Vorlagen: `${CLAUDE_PLUGIN_ROOT}/skills/sr-methodology/references/reporting-templates.md`
Werkzeug: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/screen/scripts/screening_tools.py`

## Ablauf

1. **Zahlen sammeln** – ausschließlich aus Dateien:
   - Identifikation je Datenbank/Register: vom Nutzer (Suchprotokoll) bzw. `prepare_summary.json`
   - Duplikate: `prepare_summary.json` bzw. Angabe aus dem Literaturverwaltungsprogramm
   - Ti/Ab: `final_tiab.csv`; Volltext: `final_fulltext.csv`, `fulltext_list.csv`
   - Ausschlussgründe Volltext: Zählung der `final_reason` in `final_fulltext.csv`
   - Studien vs. Reports: `study_report_links.csv`
   Fehlende Angaben beim Nutzer erfragen, nicht schätzen.
2. **`screening/prisma/counts.json` schreiben** mit den Schlüsseln:
   `databases` (Objekt), `registers` (Objekt), `duplicates_removed`, `automation_removed`,
   `other_removed`, `records_screened`, `records_excluded`, `reports_sought`,
   `reports_not_retrieved`, `reports_assessed`, `reports_excluded` (Objekt Grund → n),
   `studies_included`, `reports_included`; optional `other_sources` (Objekt),
   `other_reports_sought`, `other_reports_not_retrieved`, `other_reports_assessed`,
   `other_reports_excluded` (Objekt).
3. `prisma --counts screening/prisma/counts.json --out screening/prisma`
   Bei Konsistenzfehlern: Ursache finden und beheben, **nicht** Zahlen anpassen, bis es passt.
4. **Texte erzeugen** (Englisch) nach `reporting-templates.md` §1–3 mit echten Zahlen und κ-Werten
   aus `agreement_tiab.json` / `agreement_fulltext.json` → `screening/prisma/methods_results_draft.md`.
   Die KI-Offenlegung (§2) ist Pflicht, sobald Reviewer A/B beteiligt waren; Modell und Zeitraum
   aus `screening_log.md`.
5. **Tabelle ausgeschlossener Volltexte** → `screening/prisma/excluded_fulltexts_table.md`
   (Autor, Jahr, DOI, ein Grund, Detail).
6. **Checkliste** (`reporting-templates.md` §7) abarbeiten und offene Punkte auflisten.
7. Dem Nutzer berichten: Pfade der Dateien, Prüfergebnis der Zahlen, offene Punkte. Hinweis: Für
   die finale Abbildung die offizielle PRISMA-2020-Vorlage oder das R-Paket „PRISMA2020“
   verwenden; die SVG ist ein konsistenzgeprüfter Entwurf.
