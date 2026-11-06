# Dental SR Reviewers – Reviewer A & Reviewer B

Zwei KI-Senior-Reviewer mit zahnmedizinischer Expertise für das **duale, unabhängige Screening**
in Systematic Reviews nach **PRISMA 2020**, Cochrane Handbook (v6.5) und AMSTAR 2. Dazu gehören
eine verifizierte, versionierte Evidenzbasis, die sich aktualisieren lässt, sowie publikationsreife
Dokumentation: κ-Statistik, PRISMA-Flussdiagramm, Textbausteine für Methods und Results,
KI-Offenlegung und eine Tabelle der ausgeschlossenen Studien.

| | Reviewer A | Reviewer B |
|---|---|---|
| Klinik | Parodontologie, Implantologie, Oralchirurgie, Oralmedizin | Zahnerhaltung/Kariologie, Endodontie, Prothetik, Dentalmaterialien, KFO, Kinderzahnheilkunde, digitale Zahnmedizin |
| Methodik | Klinische Epidemiologie, RCT/Kohorte, RoB 2, ROBINS-I/-E, GRADE | Biostatistik/Metaanalyse, diagnostische Genauigkeit (QUADAS-2), In-vitro (RoBDEMAT), Tierstudien (SYRCLE) |
| Regeln | identisches Protokoll, identische Entscheidungsregeln | ← |
| Arbeitsweise | **parallel und gleichzeitig**, eigener Ordner `screening/reviewer_A/` | **parallel und gleichzeitig**, eigener Ordner `screening/reviewer_B/` |

## Parallel und unabhängig – wie das garantiert wird

1. **Gleichzeitiger Start:** Der Koordinator (`/dental-sr-reviewers:screen`) startet Reviewer A und
   Reviewer B in derselben Nachricht als Hintergrund-Agenten auf denselben Batches. Bei vielen
   Datensätzen laufen mehrere Instanzen pro Reviewer, bis zu 6 Agenten je Welle.
2. **Getrennte Arbeitsbereiche:** Jeder Reviewer schreibt nur in seinen eigenen Ordner, und zwar
   eine Datei pro Batch. Es gibt keine gemeinsamen Dateien und damit keine Schreibkonflikte.
3. **Technische Verblindung:** Der Plugin-Hook `hooks/blinding_guard.py` blockiert jeden Zugriff
   eines Reviewers auf den Ordner des anderen und auf die Abgleichsdateien (`merged_*`,
   `conflicts_*`, `final_*` …). Bash, Glob und Grep sind für die Reviewer gesperrt. Erst wenn der
   Koordinator `screening/.consensus_open` anlegt, dürfen beide die Konfliktliste lesen.
4. **Paralleler Konsens:** Zu jedem Konflikt geben beide Reviewer gleichzeitig und unabhängig
   eine Stellungnahme ab. Stimmen sie überein, gilt das als Konsens; alles andere entscheidest du
   als Arbiter.
5. **Fortschritt:** `screening_tools.py status --stage tiab` zeigt pro Batch, ob A und B fertig sind.
   Erst bei `ready_to_merge: true` wird abgeglichen.

Voraussetzung für den Hook: `python3` (oder `python`) im PATH. Ohne Python greift die
technische Sperre nicht; die Verblindung beruht dann nur auf den Anweisungen an die Reviewer.

> **Wichtig – wissenschaftliche Integrität.** Beide Reviewer sind Instanzen desselben
> Sprachmodells. Ihre Fehler können deshalb korreliert sein, und sie ersetzen **nicht** zwei
> unabhängige menschliche Reviewer. Laut dem Positionspapier von Cochrane, Campbell, JBI und CEE
> (2025) darf KI nur unter menschlicher Aufsicht eingesetzt werden, jede urteilende KI-Nutzung
> muss offengelegt werden, und die Autoren tragen die Verantwortung. Die Evidenz zum
> LLM-Screening in der Zahnmedizin ist bisher schwach (Rokhshad et al., J Dent 2025).
> Empfohlene Nutzung: KI-Reviewer A/B als zusätzliche Screener oder als Zweitscreener neben
> einem menschlichen Reviewer, menschliche Arbitration und eine Validierung an einer
> Stichprobe. Textbausteine dafür liefert `reporting-templates.md` §2.

---

## Inhalt

```
dental-sr-reviewers/
├── agents/
│   ├── reviewer-a.md            # Senior Reviewer A (Subagent, persistentes Memory)
│   └── reviewer-b.md            # Senior Reviewer B
├── hooks/
│   ├── hooks.json               # PreToolUse-Hook
│   └── blinding_guard.py        # erzwingt die Verblindung zwischen A und B
├── skills/
│   ├── sr-methodology/          # gemeinsame Wissensbasis (wird automatisch genutzt)
│   │   └── references/
│   │       ├── screening-protocol.md       # SOP: Kalibrierung, Ti/Ab, Volltext, Konflikte, Audit-Trail
│   │       ├── dental-domain-knowledge.md  # Klassifikationen, Designs, Endpunkte, Fallstricke
│   │       ├── evidence-base.md            # 71 verifizierte Quellen (PMID/DOI), Version 2026.11.0
│   │       ├── reporting-templates.md      # Methods/Results, KI-Offenlegung, Tabellen, Checkliste
│   │       └── changelog.md
│   ├── screen/                  # /dental-sr-reviewers:screen – kompletter Workflow
│   │   └── scripts/screening_tools.py      # Deduplikation, Batches, Status, κ/PABAK, Konsens, PRISMA, ASReview-Export
│   ├── prisma-report/           # /dental-sr-reviewers:prisma-report
│   └── update-evidence/         # /dental-sr-reviewers:update-evidence
└── scripts/build_claude_ai_skills.py       # baut ZIP-Skills für claude.ai
```

---

## Installation

### A) Claude Code (Terminal, Desktop-App, VS Code) – für alle Projekte

```text
/plugin marketplace add https://raw.githubusercontent.com/anas94miqdad/claude-plugins-official/refs/heads/claude/dental-systematic-review-reviewer-lsbwht/plugins/dental-sr-reviewers/.claude-plugin/marketplace.json
/plugin install dental-sr-reviewers@dental-sr-tools
```

Als Scope **„Install for you (user scope)“** wählen. Dann stehen Reviewer A und B in **jedem**
Projekt auf diesem Rechner zur Verfügung.

Alternative ohne Marketplace (eine Sitzung): `claude --plugin-dir <pfad>/plugins/dental-sr-reviewers`

> Hinweis: Das Repository ist ein Fork von `claude-plugins-official`. Dieser Marketplace-Name ist
> für Anthropic reserviert, deshalb hat das Plugin einen eigenen Mini-Marketplace
> (`dental-sr-tools`). Nach einem Merge in `main` in `marketplace.json` den `ref` auf `main`
> ändern und die URL entsprechend anpassen.

### B) claude.ai / Claude Desktop / Cowork – Skills für alle Chats und Projekte

1. ZIP-Dateien bauen: `python3 scripts/build_claude_ai_skills.py` → `dist/`
   - `dental-sr-reviewer-a.zip`, `dental-sr-reviewer-b.zip`,
     `dental-sr-coordinator.zip`, `dental-sr-update-evidence.zip`
2. claude.ai → **Settings → Capabilities → Skills → Upload skill**, jede ZIP-Datei einzeln hochladen.
   „Code execution and file creation“ muss aktiviert sein.
3. Die Skills sind dann in allen Chats und Projekten deines Accounts verfügbar. Parallel und
   unabhängig heißt hier: Reviewer A und Reviewer B laufen gleichzeitig in **zwei eigenen Chats**
   (z. B. zwei Browser-Tabs) mit derselben Batch-Datei, und der Abgleich folgt in einem dritten Chat
   mit `dental-sr-coordinator`. Hooks gibt es in claude.ai nicht; die Trennung entsteht durch die
   getrennten Chats.

---

## Nutzung (Claude Code)

| Aufgabe | Befehl / Aufruf |
|---|---|
| Gesamtes Screening starten oder fortsetzen | `/dental-sr-reviewers:screen pubmed.ris embase.ris wos.csv` |
| Nur Pilot/Kalibrierung | `/dental-sr-reviewers:screen screening/ --pilot` |
| Volltextstufe | `/dental-sr-reviewers:screen screening/ --stage fulltext` |
| PRISMA-Bericht | `/dental-sr-reviewers:prisma-report` |
| Wissen aktualisieren | `/dental-sr-reviewers:update-evidence` (optional Thema, z. B. `periimplantitis`) |
| Einzelnen Reviewer direkt ansprechen | `@agent-dental-sr-reviewers:reviewer-a Prüfe meine Einschlusskriterien …` |

Der Workflow legt im Projekt einen Ordner `screening/` mit vollständigem Audit-Trail an
(Protokoll-Snapshot, getrennte Reviewer-Ordner A/B mit einer Datei pro Batch, Konflikte, Konsens, finale Entscheidungen,
κ-Statistik, PRISMA-Zahlen und SVG, Screening-Log).

Das Skript funktioniert auch eigenständig (nur Python-Standardbibliothek):

```bash
python3 skills/screen/scripts/screening_tools.py prepare export.ris --out screening
python3 skills/screen/scripts/screening_tools.py status --stage tiab
python3 skills/screen/scripts/screening_tools.py merge --a screening/reviewer_A/tiab --b screening/reviewer_B/tiab --stage tiab --out screening
python3 skills/screen/scripts/screening_tools.py prisma --counts screening/prisma/counts.json --out screening/prisma
python3 skills/screen/scripts/screening_tools.py export-asreview --records screening/records.csv --final screening/final_tiab.csv --out asreview_import.csv
```

---

## Wie das Wissen aktuell bleibt

1. **Versionierte Basis** (`evidence-base.md`, Version `JJJJ.MM.n`): Jede Quelle ist mit Datum gegen
   PubMed bzw. Crossref verifiziert. Wird diese Datei im Repository aktualisiert, bekommen alle
   Installationen das Update (in Claude Code: `/plugin` → Marketplaces → Update, oder
   Auto-Update aktivieren).
2. **Lokale Updates** mit `/dental-sr-reviewers:update-evidence`: Das Skill durchsucht PubMed
   seit der letzten Prüfung, verifiziert jede PMID/DOI und schreibt datierte Einträge nach
   `~/.claude/plugins/data/…/evidence-updates.md` (`${CLAUDE_PLUGIN_DATA}`). Die Datei bleibt bei
   Plugin-Updates erhalten, und beide Reviewer lesen sie vor jeder Aufgabe.
3. **Persistentes Reviewer-Memory** (`memory: user`): Jeder Reviewer hält projektübergreifende
   Lernpunkte fest, z. B. wiederkehrende Fallstricke. Projektspezifische Entscheidungen landen
   dort nie.
4. **Empfehlung:** monatlich `update-evidence` ausführen, etwa als geplante Aufgabe.

---

## Grundlagen (Auszug, vollständig in `evidence-base.md`)

- Page MJ, et al. PRISMA 2020 statement. BMJ 2021;372:n71. PMID 33782057
- Shea BJ, et al. AMSTAR 2. BMJ 2017;358:j4008. PMID 28935701
- Waffenschmidt S, et al. Single vs. double screening. BMC Med Res Methodol 2019;19:132. PMID 31253092
- Flemyng E, et al. Position statement on AI use in evidence synthesis (Cochrane/Campbell/JBI/CEE). Campbell Syst Rev 2025;21:e70074. PMID 41230118
- Rokhshad R, et al. LLMs for the screening step in SRs in dentistry. J Dent 2025;160:105877. PMID 40480310
- Papapanou PN, et al. / Tonetti MS, et al. 2017 World Workshop – Periodontitis, Staging & Grading. J Clin Periodontol 2018. PMIDs 29926490, 29926495

## Lizenz

Apache 2.0 (siehe `LICENSE`).
