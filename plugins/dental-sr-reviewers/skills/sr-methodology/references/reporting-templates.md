# Publikationsreife Textbausteine und Tabellen (Englisch, Journal-Standard)

Platzhalter in `[eckigen Klammern]` ersetzen. Alle Zahlen kommen aus den Dateien in
`screening/` (`agreement_*.json`, `prisma/prisma_counts.md`), nie aus dem Gedächtnis.
Referenznummern beziehen sich auf `evidence-base.md`.

---

## 1. Methods – Selection process (PRISMA 2020 Item 8)

> **Selection process.** Records retrieved from all sources were imported into
> [reference manager, e.g. EndNote 21 / Zotero 7] and duplicates were removed
> [automatically and manually] following [method, e.g. Bramer et al.]. Screening was performed
> in two stages (title/abstract, then full text) against the eligibility criteria pre-specified in
> the registered protocol ([PROSPERO CRDXXXXXXXX]). Before formal screening, a calibration
> exercise on a random sample of [n] records was conducted; screening began once agreement
> reached Cohen's κ ≥ [0.60] [after X rounds; criteria clarifications were documented as protocol
> amendments dated (date)].
> At both stages, two reviewers ([initials human reviewer 1], [initials human reviewer 2 or
> "an AI-assisted reviewer, see below"]) screened all records independently and in duplicate.
> At the title/abstract stage, records were retained for full-text assessment if either reviewer
> judged them potentially eligible or if the information was insufficient. Full-text reports were
> assessed independently by both reviewers; reasons for exclusion were recorded using a
> pre-specified hierarchy, assigning a single (highest-ranking) reason per report.
> Disagreements were resolved by discussion and, where consensus could not be reached,
> by a third reviewer ([initials]). Authors of [n] studies were contacted for missing
> information; [n] responded. Inter-rater agreement was quantified using Cohen's κ with
> 95% confidence intervals and percentage agreement [and the prevalence-adjusted
> bias-adjusted kappa (PABAK)], and interpreted according to [Landis and Koch / McHugh].

## 2. Methods – Offenlegung der KI-Unterstützung (PRISMA 2020 Item 8; Positionspapier D1)

PRISMA 2020 Item 8 verlangt die Angabe von Automatisierungs-Tools und wie sie eingesetzt
wurden. Das Positionspapier von Cochrane, Campbell, JBI und CEE (2025, D1) verlangt volle
Offenlegung jeder KI-Nutzung, die Urteile trifft oder vorschlägt.

> **Use of artificial intelligence.** A large language model–based screening assistant
> ([model name and version, e.g. "Claude (Anthropic), model claude-…, accessed via Claude Code
> v…"], [dates of use]) was used as [a second / an additional] independent screener at the
> [title/abstract and/or full-text] stage. Two separately instructed instances ("Reviewer A" and
> "Reviewer B", with distinct dental-specialty profiles but identical eligibility criteria and
> decision rules) screened records in isolated sessions without access to each other's
> decisions. The complete prompts, decision logs and version history are provided in
> Supplementary File [X]. Because both instances share the same underlying model, their errors
> may be correlated; therefore, [all AI decisions were verified by a human reviewer / every
> record was additionally screened by at least one human reviewer ([initials])], and all
> disagreements and all final decisions were made by human reviewers. AI performance was
> evaluated against human screening on [n] records (sensitivity [x]%, specificity [y]%).
> The authors take full responsibility for all eligibility decisions. AI tools were not used to
> generate scientific conclusions [adapt if used for writing assistance, per journal policy].

**Journal-Hinweise:** Die meisten Verlage (Elsevier, Wiley, Springer Nature, Quintessence, BMJ)
verlangen zusätzlich eine Erklärung zur KI-Nutzung im Abschnitt „Declaration of generative AI“
oder in den Acknowledgements; KI kann kein Autor sein (ICMJE, COPE). Vor Einreichung die
„Guide for Authors“ des Zieljournals prüfen.

## 3. Results – Study selection (PRISMA 2020 Items 16a/16b)

> **Study selection.** The searches identified [N] records ([n] MEDLINE, [n] Embase, [n] Web of
> Science, [n] CENTRAL, [n] registers) and [n] records from other methods. After removal of [n]
> duplicates, [n] records were screened by title and abstract, of which [n] were excluded.
> Of [n] reports sought for retrieval, [n] could not be retrieved. [n] full-text reports were
> assessed for eligibility; [n] were excluded ([n] wrong study design, [n] wrong population,
> [n] …; Supplementary Table [X]). Finally, [n] studies (reported in [n] reports) were included
> (Figure 1). Agreement between reviewers was [x]% (κ = [x], 95% CI [x–x]) at the
> title/abstract stage and [x]% (κ = [x], 95% CI [x–x]) at the full-text stage.
> [Studies that might appear to meet the inclusion criteria but were excluded are cited with
> reasons in Table [X] (Item 16b).]

**Figure 1 caption:**
> PRISMA 2020 flow diagram of study selection. Adapted from Page MJ, et al. BMJ 2021;372:n71.

Für die Endfassung des Diagramms empfiehlt sich die offizielle PRISMA-2020-Vorlage
(prisma-statement.org) oder die Shiny-App/R-Paket „PRISMA2020“; die mit
`screening_tools.py prisma` erzeugte SVG dient als geprüfter Entwurf mit konsistenten Zahlen.

## 4. Supplementary Table – Excluded full-text reports (AMSTAR 2 Item 7)

| # | Study (first author, year) | Reference / DOI | Reason for exclusion (single, hierarchical) | Detail |
|---|---|---|---|---|
| 1 | [Author 2019] | [doi] | Wrong study design | Retrospective case series without control group |
| 2 | [Author 2021] | [doi] | Wrong population | Mixed sample; data for periodontitis patients not reported separately; authors contacted [date], no reply |

## 5. Supplementary – Screening log (Reproduzierbarkeit)

| Date | Stage | Step | Performed by | Tool / model + version | Prompt/protocol version | Output file |
|---|---|---|---|---|---|---|
| 2026-11-06 | tiab | Calibration (n = 100) | Reviewer A, Reviewer B | [model] | protocol v1.0 | decisions_A_pilot.csv |

## 6. Limitations – Bausteine

- > Screening was assisted by a large language model; although decisions were made independently
  > in isolated sessions and verified by human reviewers, the two AI instances share the same
  > underlying model and may therefore make correlated errors.
- > Restriction to [English-language] publications may have introduced language bias.
- > The search was limited to [databases]; grey literature [was / was not] searched.

## 7. Checkliste vor Einreichung (Screening-bezogen)

- [ ] Protokoll registriert, Registernummer im Abstract und Methods (PRISMA Item 24a)
- [ ] Abweichungen vom Protokoll berichtet und begründet (Item 24c)
- [ ] Selektionsprozess mit Anzahl Reviewer, Unabhängigkeit, Konfliktlösung (Item 8)
- [ ] Automatisierungs-/KI-Tools mit Version und Rolle offengelegt (Item 8; D1)
- [ ] Flussdiagramm mit konsistenten Zahlen (Item 16a) – `screening_tools.py prisma` ohne Fehler
- [ ] Tabelle ausgeschlossener Volltexte mit Gründen (Item 16b; AMSTAR 2 Item 7)
- [ ] κ-Werte mit 95 %-KI je Stufe
- [ ] Rohdaten der Entscheidungen als Supplement oder in Repository (OSF/Zenodo)
- [ ] KI-Erklärung gemäß Verlagsrichtlinie
