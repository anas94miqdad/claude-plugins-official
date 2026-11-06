---
name: sr-methodology
description: Evidence-based methodology and dental domain knowledge for systematic reviews in dentistry - PRISMA 2020 and extensions, Cochrane Handbook, AMSTAR 2, dual independent screening, kappa reporting, exclusion-reason hierarchy, dental classifications (2017 AAP/EFP periodontitis staging/grading, peri-implantitis, ICDAS, endodontic and dental-materials reporting guidelines) and responsible AI use (Cochrane/Campbell/JBI/CEE 2025 position statement). Use when planning, screening, documenting or writing up a dental systematic review, scoping review or meta-analysis, when defining eligibility criteria, or when the user mentions Reviewer A or Reviewer B.
---

# Methodik-Wissensbasis für zahnmedizinische Systematic Reviews

Gemeinsame, versionierte Wissensbasis von **Reviewer A** und **Reviewer B**
(`dental-sr-reviewers:reviewer-a`, `dental-sr-reviewers:reviewer-b`).

## Inhalt

| Datei | Wann lesen |
|---|---|
| `references/screening-protocol.md` | Immer vor dem Screening: verbindliche SOP (Kalibrierung, Ti/Ab, Volltext, Konflikte, Audit-Trail) |
| `references/dental-domain-knowledge.md` | Bei jeder Eligibility-Entscheidung: Klassifikationen, Designs, Endpunkte, Fallstricke |
| `references/evidence-base.md` | Bei jeder methodischen Aussage oder Zitation: verifizierte Quellen mit PMID/DOI |
| `references/reporting-templates.md` | Beim Schreiben: Methods/Results-Bausteine, KI-Offenlegung, Ausschluss-Tabelle, Checkliste |
| `references/changelog.md` | Versionsgeschichte der Wissensbasis |
| `${CLAUDE_PLUGIN_DATA}/evidence-updates.md` | Falls vorhanden: lokal nachgetragene, verifizierte neuere Evidenz |

## Kernregeln (gelten immer)

1. **Protokoll zuerst.** Kein Screening ohne freigegebene, operationalisierte Kriterien.
2. **Zwei unabhängige Reviewer** auf beiden Stufen; Konflikte per Konsens, sonst menschlicher Arbiter.
3. **Ti/Ab sensitiv:** im Zweifel weiterleiten; fehlender Abstract ist kein Ausschlussgrund.
4. **Ein Ausschlussgrund je Volltext** nach festgelegter Hierarchie; vollständige Ausschlussliste.
5. **Alles dokumentieren:** Entscheidungen, Begründungen, κ mit 95 %-KI, PRISMA-Zahlen, Log.
6. **Keine erfundenen Referenzen.** Nur verifizierte PMIDs/DOIs.
7. **KI-Nutzung offenlegen** und menschliche Verantwortung sicherstellen (evidence-base D1).

## Werkzeuge

- `/dental-sr-reviewers:screen` – vollständiger Workflow mit beiden Reviewern
- `/dental-sr-reviewers:prisma-report` – PRISMA-Flussdiagramm, Methods/Results-Texte, Tabellen
- `/dental-sr-reviewers:update-evidence` – Wissensbasis gegen aktuelle Literatur aktualisieren
- `${CLAUDE_PLUGIN_ROOT}/skills/screen/scripts/screening_tools.py` – Deduplikation, Batches,
  κ/PABAK, Konfliktliste, PRISMA-Konsistenzprüfung, ASReview-Export
