# Screening-Protokoll (Standard Operating Procedure)

Gilt für Reviewer A und Reviewer B gleichermaßen. Grundlage: PRISMA 2020 (Items 5, 8, 16a/b),
Cochrane Handbook (Kap. 3 „Defining the criteria“ und Kap. 4 „Searching for and selecting
studies“), PRISMA-P 2015, AMSTAR 2 (Items 5 und 7), RAISE-Empfehlungen zur KI-Nutzung.
Vollständige Belege: `evidence-base.md`.

---

## 0. Voraussetzungen – ohne diese wird NICHT gescreent

| Voraussetzung | Warum | Beleg |
|---|---|---|
| Schriftliches, datiertes Protokoll mit Forschungsfrage (PICO/PECO/PIRD/PCC) | Verhindert post-hoc-Entscheidungen; AMSTAR 2 Item 2 (kritisch) | PRISMA-P; AMSTAR 2 |
| Registrierung (PROSPERO, OSF, INPLASY) oder begründeter Verzicht | Von den meisten Dental-Journals verlangt (z. B. J Dent Res, J Clin Periodontol, J Dent, Clin Oral Implants Res) | PRISMA 2020 Item 24a |
| Operationalisierte Ein-/Ausschlusskriterien je Domäne (P, I/E, C, O, Studiendesign, Setting, Zeitraum, Sprache, Publikationsstatus) | Reproduzierbarkeit; PRISMA 2020 Item 5 | PRISMA 2020 E&E |
| Hierarchisch geordnete Ausschlussgründe (siehe §4) | Eindeutige Zuordnung im Flussdiagramm | PRISMA 2020 Item 16a |
| Pilot-/Kalibrierungsrunde abgeschlossen (§2) | Konsistenz zwischen Reviewern | Cochrane Handbook Kap. 4; Polanin 2019 |

Fehlt eines davon, erstellen die Reviewer zuerst einen **Vorschlag** (z. B. Kriterien-Tabelle) und
legen ihn dem Nutzer zur Freigabe vor. Ohne Freigabe der Kriterien wird nicht gescreent.

---

## 1. Unabhängigkeit und Verblindung

1. Reviewer A und B screenen **unabhängig**: getrennte Kontexte, kein Zugriff auf die
   Entscheidungsdatei des jeweils anderen, bevor beide ihre Runde abgeschlossen haben.
2. Keine Kommunikation über einzelne Datensätze vor dem Abgleich.
3. Entscheidungen werden nach Abschluss nicht mehr verändert; Korrekturen erfolgen nur
   dokumentiert in der Konsensphase (Audit-Trail).
4. Einschränkung (ehrlich dokumentieren): Beide Reviewer sind Instanzen desselben
   Sprachmodells mit unterschiedlichen Expertenprofilen. Ihre Fehler sind daher **nicht
   statistisch unabhängig** wie die zweier Menschen. Das muss in der Methodik offengelegt
   werden (siehe `reporting-templates.md`, Abschnitt „KI-Offenlegung“), und mindestens ein
   menschlicher Reviewer muss die Ergebnisse verantworten.

---

## 2. Kalibrierung (Pilotphase)

- Zufallsstichprobe von 50–100 Datensätzen (bei < 500 Treffern: 10 %), von beiden Reviewern
  unabhängig gescreent.
- Ziel: Cohen's κ ≥ 0,60 auf Titel/Abstract-Ebene (praktisch üblicher Schwellenwert;
  McHugh 2012 empfiehlt für Gesundheitsforschung eher ≥ 0,80 als „starke“ Übereinstimmung).
- Unterhalb des Ziels: Diskrepanzen analysieren, unklare Kriterien präzisieren (als
  **Protokoll-Amendment mit Datum** dokumentieren), Pilot wiederholen.
- Zusätzlich empfohlen: Der menschliche Hauptautor screent dieselbe Pilotstichprobe; die
  Sensitivität der KI-Reviewer gegenüber dem Menschen wird berichtet.

---

## 3. Stufe 1 – Titel/Abstract (Ti/Ab)

**Grundsatz: Im Zweifel einschließen.** Ziel ist maximale Sensitivität; Ausschluss nur, wenn
mindestens ein Kriterium **eindeutig** verletzt ist (Cochrane Handbook Kap. 4).

Entscheidungslogik pro Datensatz:

1. Lies Titel, Abstract, Keywords, Publikationstyp, Journal, Jahr.
2. Prüfe die Kriterien in der festgelegten Hierarchie (§4). Der **erste eindeutig**
   verletzte Punkt ist der Ausschlussgrund.
3. Entscheidung:
   - `include` – alle Kriterien erfüllt oder wahrscheinlich erfüllt.
   - `unclear` – Information fehlt (kein Abstract, Design/Population nicht erkennbar) → geht
     in den Volltext. **Fehlender Abstract allein ist nie ein Ausschlussgrund.**
   - `exclude` – mindestens ein Kriterium eindeutig verletzt.
4. Konfidenz: `high` / `medium` / `low`. `low` + `exclude` ist nicht erlaubt → dann `unclear`.
5. Begründung (`rationale`): 1–2 Sätze, mit wörtlichem Kurzzitat aus Titel/Abstract als Beleg
   (z. B. `"in vitro" – Studiendesign nicht eingeschlossen`).

Typische Fallen in der Zahnmedizin (siehe `dental-domain-knowledge.md`):
- „Clinical study“ im Titel, tatsächlich aber In-vitro/ex-vivo (extrahierte Zähne!).
- Split-mouth-Design als RCT – ist ein RCT, aber Analyseeinheit beachten.
- Abstract nennt „patients“, untersucht aber Implantate/Zähne als Einheit.
- Kongressabstracts (z. B. J Dent Res IADR-Supplement, Clin Oral Implants Res EAO-Supplement):
  laut Protokoll behandeln; nie stillschweigend ausschließen.
- Sekundäranalysen/Follow-up-Publikationen derselben Kohorte (→ „Reports“ vs. „Studies“).

---

## 4. Ausschlussgründe – Hierarchie (Standardvorlage, im Protokoll anpassen)

Bei mehreren Gründen wird **nur der höchstrangige** gezählt (eindeutige PRISMA-Zahlen).

| Code | Grund (Englisch, für Manuskript) | Domäne |
|---|---|---|
| E1 | Not a primary study / wrong publication type (review, editorial, letter, protocol w/o results) | Publikationstyp |
| E2 | Wrong study design | S |
| E3 | Wrong population / condition | P |
| E4 | Wrong intervention / exposure / index test | I/E |
| E5 | Wrong comparator | C |
| E6 | No relevant outcome / outcome not measured as defined | O |
| E7 | Wrong setting / follow-up too short | T |
| E8 | Duplicate / overlapping report (linked, not excluded as study) | – |
| E9 | Full text not retrievable (only stage 2; → "reports not retrieved") | – |
| E10 | Language / date outside protocol limits (only if pre-specified!) | L |
| E11 | Retracted publication | – |

Hinweis: Sprachrestriktionen sollten vermieden werden (Cochrane); falls angewandt,
begründen und in der Limitation diskutieren.

---

## 5. Stufe 2 – Volltext

1. Für jeden weitergeleiteten Datensatz Volltext beschaffen (PubMed Central, Verlag,
   Fernleihe, Kontakt zu Autoren – Kontaktversuche dokumentieren, Frist z. B. 2 Wochen,
   1 Erinnerung).
2. Beide Reviewer beurteilen unabhängig anhand des **gesamten** Dokuments (Methoden-
   und Ergebnisteil, Supplement, Registereintrag).
3. Pro Ausschluss: **genau ein** Grund nach Hierarchie §4 + Fundstelle (Seite/Abschnitt).
4. Mehrfachpublikationen: Einen „Primary report“ bestimmen, weitere als „linked reports“
   zuordnen. PRISMA 2020 unterscheidet *studies* und *reports*.
5. Prüfe Retraction Watch / PubMed-Retraction-Hinweise sowie Hinweise auf
   „Problematic studies“ (Cochrane Policy, z. B. unplausible Daten, fehlende Registrierung bei
   RCTs) – markieren, nicht stillschweigend ausschließen; im Team entscheiden.
6. Liste der ausgeschlossenen Volltexte **mit Gründen** ist Pflichtbestandteil
   (PRISMA 2020 Item 16b; AMSTAR 2 Item 7 – kritische Domäne).

---

## 6. Konfliktlösung

Reihenfolge (im Protokoll vorab festlegen):

1. Automatischer Abgleich (`screening_tools.py merge`).
2. Jede Diskrepanz: Beide Reviewer sehen nun beide Begründungen und nehmen in einem
   **Konsensgespräch** Stellung (dokumentiert: ursprüngliche Entscheidungen, Argumente,
   Endentscheidung, „resolved_by: consensus“).
3. Kein Konsens → **dritter Reviewer / Arbiter = menschliche Person** (Standard:
   der Nutzer bzw. Senior-Autor). KI darf in dieser Stufe nicht final entscheiden.
4. Ti/Ab-Stufe, bei verbleibender Unklarheit: in den Volltext weiterleiten.

---

## 7. Dokumentation (Audit Trail)

Pro Projekt im Ordner `screening/`:

| Datei | Inhalt |
|---|---|
| `protocol_snapshot.md` | Freigegebene Kriterien + Datum + Version, alle Amendments |
| `records.csv` / `records_all.csv` | Dedupliziertes / vollständiges Set mit `record_id` |
| `decisions_A_<stage>.csv`, `decisions_B_<stage>.csv` | Unabhängige Entscheidungen (unverändert) |
| `merged_<stage>.csv`, `conflicts_<stage>.csv` | Abgleich |
| `consensus_<stage>.csv` | Konfliktlösungen mit `resolved_by` |
| `final_<stage>.csv` | Endentscheidungen |
| `agreement_<stage>.json` | κ, 95 %-KI, PABAK, %-Übereinstimmung |
| `excluded_fulltexts.md` | Tabelle ausgeschlossener Volltexte mit Grund (Supplement) |
| `prisma/` | Zählungen, SVG-Flussdiagramm |
| `screening_log.md` | Chronologisches Log: Datum, Schritt, wer, Modell/Version, Prompt-Version |

Format jeder Entscheidungszeile:

```
record_id,reviewer,stage,decision,exclusion_reason,criterion,confidence,rationale
R00017,A,tiab,exclude,E2 Wrong study design,S,high,"""in vitro study on extracted molars"""
```

---

## 8. Qualitätsindikatoren, die berichtet werden

- Cohen's κ (mit 95 %-KI) und prozentuale Übereinstimmung je Stufe; bei schiefer Prävalenz
  zusätzlich PABAK (Prävalenz- und Bias-Index angeben).
- Anzahl Konflikte und wie gelöst.
- Optional (empfohlen bei KI-Beteiligung): Sensitivität/Spezifität der KI-Reviewer gegenüber
  einer menschlichen Referenzstichprobe; Anteil `unclear`.

---

## 9. Was die Reviewer ausdrücklich NICHT tun

- Kriterien während des Screenings eigenmächtig ändern.
- Studien nach Ergebnis (signifikant / nicht signifikant) beurteilen.
- Studien wegen niedriger Qualität im Screening ausschließen (das ist Risk-of-Bias-
  Bewertung, nicht Eligibility – außer das Protokoll legt es explizit fest).
- Literaturstellen, PMIDs oder DOIs erfinden. Jede Quelle wird über PubMed/DOI verifiziert.
- Die Entscheidung des anderen Reviewers vor Abschluss der eigenen Runde lesen.
