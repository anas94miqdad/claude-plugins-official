# Zahnmedizinisches Fachwissen für Eligibility-Entscheidungen

Diese Datei enthält das Domänenwissen, das beim Screening über die reine Methodik hinaus
nötig ist: anerkannte Klassifikationen, Falldefinitionen, typische Studiendesigns und
Endpunkte sowie fachspezifische Fallstricke. Quellen mit PMID/DOI: `evidence-base.md`.
Bei Widerspruch gilt immer das projektspezifische Protokoll.

---

## 1. Klassifikationen und Falldefinitionen (prüfen, ob Studienpopulation passt)

### Parodontologie
- **2017 World Workshop (AAP/EFP)** – aktuelle Klassifikation parodontaler und
  periimplantärer Erkrankungen (Caton et al. 2018; Papapanou et al. 2018; Tonetti et al. 2018).
  - Parodontitis: **Stadien I–IV** (Schweregrad/Komplexität: CAL, Knochenabbau, Zahnverlust)
    und **Grade A–C** (Progressionsrate; Modifikatoren Rauchen, Diabetes/HbA1c).
  - Falldefinition „Parodontitis“: interdentaler CAL ≥ 2 Zähne nicht benachbart, oder bukkaler/
    oraler CAL ≥ 3 mm mit ST > 3 mm an ≥ 2 Zähnen (Ausschluss anderer Ursachen).
  - Gingivitis am intakten / reduzierten Parodont: BOP ≥ 10 % ohne Attachmentverlust bzw.
    nach erfolgreicher Therapie.
  - Ältere Studien nutzen **Armitage 1999** (chronische/aggressive Parodontitis) oder
    **CDC/AAP-Falldefinitionen (Page & Eke 2007; Eke 2012)** für Epidemiologie.
    → Nicht automatisch ausschließen! Protokoll muss regeln, ob Studien mit alten
    Klassifikationen eingeschlossen werden (in der Regel ja, mit Mapping-Hinweis).
- **EFP S3-Leitlinien**: Stadium I–III (Sanz et al. 2020), Stadium IV (Herrera et al. 2022),
  periimplantäre Erkrankungen (Herrera et al. 2023). Therapiestufen 1–4 (z. B. Stufe 2 =
  subgingivale Instrumentierung) helfen, Interventionen korrekt zuzuordnen.

### Implantologie / periimplantäre Erkrankungen
- Periimplantäre Mukositis vs. **Periimplantitis** (Berglundh et al. 2018): Periimplantitis =
  BOP/Pus + zunehmende ST + progressiver Knochenverlust über initiale Remodellierung hinaus;
  ohne Ausgangsbefund: Knochenniveau ≥ 3 mm und/oder ST ≥ 6 mm mit Blutung.
- Ältere Studien: uneinheitliche Definitionen (z. B. Albrektsson-Erfolgskriterien 1986) –
  Protokoll muss festlegen, ob diese akzeptiert werden.
- Einheiten: Patient vs. Implantat; Implantat-**Überleben** ≠ Implantat-**Erfolg**.
- Sofortimplantation/-belastung: Definitionen nach ITI-Konsensus (Typ 1–4 Implantation;
  Belastungsprotokolle sofort/früh/konventionell).

### Kariologie / Zahnerhaltung
- **ICDAS** (Codes 0–6), ICCMS; **DMFT/DMFS**, dmft/dmfs (Milchgebiss), WHO-Kriterien.
- Füllungsbewertung: **FDI-Kriterien** (Hickel 2007/2010, Update 2023), **USPHS / modifizierte
  Ryge-Kriterien** – beide gängig, Protokoll legt Akzeptanz fest.
- Caries-Management: non-/mikroinvasiv (Versiegelung, Infiltration), selektive Exkavation.

### Endodontologie
- Pulpadiagnosen nach AAE-Konsensus (2009) bzw. neuere Klassifikationen (z. B. Wolters 2017,
  ESE-Positionspapiere). PAI (Periapical Index, Ørstavik 1986); CBCT-PAI.
- Erfolg „strict“ vs. „loose“ (Strindberg-Kriterien); **Überleben** des Zahnes ≠ Heilung.
- Spezifische Reporting-Guidelines: PRILE (Labor), PRIASE (Tier), PROBE (Beobachtungsstudien),
  PRIRATE (Fallberichte) – nützlich zur Erkennung des Studientyps.

### Prothetik / Dentalmaterialien
- Überlebens-/Komplikationsraten (Pjetursson-/Sailer-Systematik), technische vs. biologische
  Komplikationen; Chipping, Debonding, Fraktur.
- In-vitro-Studien (Bruchlast, Haftverbund, Verschleiß, Farbstabilität): eigenes
  Risk-of-Bias-Instrument **RoBDEMAT**; Reporting **CRIS**. Nur einschließen, wenn das
  Protokoll In-vitro-Studien vorsieht.

### Kieferorthopädie
- Malokklusionsindizes: PAR, IOTN, ICON, DAI; Angle-Klassen.
- Häufiges Design: retrospektive Kohorten aus Archivmaterial; Split-mouth bei Verankerung;
  Kephalometrie (Messfehler, Dahlberg).

### Kinderzahnheilkunde
- Verhaltensführung (Frankl-Skala), MIH (Weerheijm/EAPD-Kriterien), frühkindliche Karies (ECC).

### Oralchirurgie / Oralmedizin
- Weisheitszahnchirurgie: Schwierigkeitsklassifikationen (Pell & Gregory, Winter),
  postoperative Endpunkte (Schmerz VAS, Schwellung, Trismus, Alveolitis).
- MRONJ: AAOMS-Stadien (Positionspapier 2022). OPMD/Leukoplakie: WHO-Klassifikation.
- Präoperative Antibiotikaprophylaxe, Knochenaugmentation (GBR, Sinuslift, Socket
  Preservation).

### Funktionsdiagnostik / CMD
- **DC/TMD** (Schiffman et al. 2014) – Standard; RDC/TMD (1992) in älteren Studien.

### Digitale Zahnmedizin / KI
- Diagnostische Genauigkeit (Sensitivität/Spezifität, AUC) → QUADAS-2 bzw. QUADAS-AI;
  Reporting: STARD 2015, CLAIM, TRIPOD+AI; Checklist für KI in der Zahnmedizin
  (Schwendicke et al. 2021).

---

## 2. Studiendesigns – sichere Erkennung

| Merkmal im Abstract | Wahrscheinliches Design | Achtung |
|---|---|---|
| „randomly allocated“, „randomized“, „split-mouth“, „parallel-arm“ | RCT | Quasi-randomisiert (alternierend, Geburtsdatum) ≠ RCT |
| „patients treated between … were retrospectively analysed“ | Retrospektive Kohorte / Fallserie | Ohne Vergleichsgruppe = Fallserie |
| „extracted teeth“, „specimens“, „bovine incisors“, „artificial saliva“ | In vitro / ex vivo | Oft „clinical relevance“ im Titel |
| „rats“, „dogs“, „minipigs“, „critical-size defect“ | Tierstudie | → SYRCLE RoB, ARRIVE 2.0 |
| „finite element analysis“, „simulation“ | In silico | meist ausschließen |
| „cross-sectional“, „survey“, „questionnaire“ | Querschnitt | Kausale Fragen → meist nicht geeignet |
| „sensitivity“, „specificity“, „reference standard“ | Diagnostische Genauigkeitsstudie | QUADAS-2 |
| „we report a case“, „case series of n = 4“ | Fallbericht/-serie | meist ausschließen |

Analyseeinheit prüfen: Patient, Kiefer, Quadrant, Zahn, Fläche, Implantat. Clustering
beeinflusst später die Datensynthese, ist aber kein Screening-Ausschlussgrund.

---

## 3. Endpunkte (Outcome-Domäne)

- **Parodontal**: CAL-Gewinn (primär bei Parodontitistherapie), ST-Reduktion, BOP, Zahnverlust,
  Taschenschluss („pocket closure“, ST ≤ 4 mm ohne BOP) als patientenrelevanter Surrogat-Endpunkt.
- **Implantat**: Überleben, Erfolg, marginaler Knochenverlust (radiologisch), periimplantäre
  Gesundheit, PROMs (OHIP-14, OHIP-G), Ästhetik (PES/WES).
- **Restaurativ/prothetisch**: Überleben, Erfolg (FDI), Komplikationen, AFR (annual failure rate).
- **Endodontisch**: Heilung (klinisch + radiologisch), Zahnüberleben, postoperativer Schmerz.
- **Patientenberichtete Endpunkte (PROMs)**: OHIP-49/-14, OHRQoL, Zufriedenheit, Schmerz (VAS/NRS).
- Core Outcome Sets beachten (COMET-Datenbank), z. B. für Parodontitistherapie und
  Implantattherapie (EFP/ITI-Konsensusberichte).

Wichtig für Ti/Ab-Screening: Outcome-Angaben fehlen in Abstracts häufig. Fehlt der Endpunkt
im Abstract, aber Population/Intervention passen → `unclear`, nicht `exclude`.

---

## 4. Datenbanken und Suchquellen in der Zahnmedizin

- MEDLINE (PubMed), Embase, Cochrane CENTRAL (inkl. Cochrane Oral Health Trials Register),
  Web of Science, Scopus; ergänzend LILACS/BBO (lateinamerikanische Dentalliteratur), CINAHL.
- Register: ClinicalTrials.gov, WHO ICTRP, DRKS (Deutschland), ISRCTN.
- Graue Literatur: OpenGrey (archiviert), Dissertationen (ProQuest), Kongressabstracts
  (IADR/AADOCR, EAO, EuroPerio).
- Handsuche in Kernzeitschriften (z. B. J Clin Periodontol, J Periodontol, Clin Oral Implants Res,
  J Dent Res, J Dent, Int Endod J, J Endod, Dent Mater, Eur J Orthod, Am J Orthod Dentofacial
  Orthop, Caries Res, Int J Prosthodont, J Prosthet Dent) – im Protokoll festlegen.

---

## 5. Fachspezifische Fallstricke beim Screening

1. **Synonyme / Terminologiewandel**: „aggressive periodontitis“ → heute Grad C;
   „chronic periodontitis“ → heute Stadium/Grad; „peri-implant disease“ umfasst Mukositis
   und Periimplantitis.
2. **Industrienahe Studien** (Implantatsysteme, Materialien): nicht ausschließen, aber
   Finanzierung für spätere RoB/Interessenkonflikt-Analyse notieren.
3. **Gleiche Kohorte, mehrere Follow-ups** (1, 3, 5, 10 Jahre): als *eine* Studie mit
   mehreren *reports* führen.
4. **Mehrere Indikationen in einer Studie** (z. B. Implantate bei Parodontitis- und
   Nicht-Parodontitispatienten): einschließen, wenn Subgruppendaten wahrscheinlich
   verfügbar → `unclear`, Volltext prüfen.
5. **Zahnmedizinische Studien in nicht-zahnmedizinischen Journals** (Diabetologie, Kardiologie,
   Gynäkologie bei Parodontitis-Assoziationsstudien) – nicht wegen Journal ausschließen.
6. **Chinesische, brasilianische, iranische, indische, türkische Literatur** ist in der
   Zahnmedizin umfangreich; Sprachrestriktion vermeiden, Übersetzung organisieren.
7. **Problematic studies / Paper Mills**: Auffällige Muster (identische Methodentexte,
   unplausible Effektgrößen, fehlende Registrierung bei RCTs nach 2005) markieren.
