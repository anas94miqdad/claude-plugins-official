# Changelog der Wissensbasis

Format: `JJJJ.MM.n` – Datum – Änderung – geprüft von. Jede inhaltliche Änderung an
`evidence-base.md`, `screening-protocol.md` oder `dental-domain-knowledge.md` wird hier eingetragen.

## 2026.11.1 – 2026-11-06 – Paralleles, technisch verblindetes Screening

- Reviewer A und B arbeiten gleichzeitig in getrennten Arbeitsbereichen
  (`screening/reviewer_A/`, `screening/reviewer_B/`, eine Datei pro Batch); bei großen
  Datenmengen mehrere Instanzen pro Reviewer.
- Plugin-Hook `blinding_guard.py` erzwingt die Verblindung (kein Zugriff auf Dateien des anderen
  Reviewers oder Abgleichsdateien vor der Konsensphase; Bash/Glob/Grep für Reviewer gesperrt).
- Konsensphase ebenfalls parallel: unabhängige Stellungnahmen, automatische Zusammenführung,
  Rest an den menschlichen Arbiter.
- `screening_tools.py`: neue Befehle `status`, `make-batches`, `consensus-merge`; `merge` liest
  Batch-Ordner; `apply-consensus` akzeptiert mehrere Dateien.

## 2026.11.0 – 2026-11-06 – Erstversion

- Evidenzbasis mit 70+ Quellen angelegt; alle PMIDs/DOIs am 2026-11-06 gegen PubMed
  (bzw. Crossref, wo vermerkt) verifiziert.
- Neu berücksichtigt: Positionspapier Cochrane/Campbell/JBI/CEE zu KI (2025), LLM-Screening-
  Studien 2024–2026 inkl. zahnmedizinischer Evaluation (Rokhshad 2025), Metaanalyse Xie 2026,
  CONSORT 2025, SPIRIT 2025, PRISMA-LSR 2024, Core GRADE 2025, ROBINS-I V2 (Tool-Dokument),
  ID-COSM 2023.
- Korrekturen gegenüber häufigen Fehlzitaten: RoBDEMAT in J Dent (nicht Dent Mater);
  PRIRATE = randomisierte Studien, PRICE = Fallberichte; SPIRIT 2025 Erstautor Chan AW.
- Offene Verifikationen in `evidence-base.md` Abschnitt I.
