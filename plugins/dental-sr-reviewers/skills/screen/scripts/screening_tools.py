#!/usr/bin/env python3
"""Screening utilities for dual independent screening in systematic reviews.

Standard library only (Python >= 3.9), so it runs anywhere Claude can run Python.

Subcommands
-----------
prepare         Normalise a RIS/CSV/TSV export into records.csv, flag likely
                duplicates and split the records into batches for the reviewers.
merge           Merge the independent decision files of Reviewer A and B,
                compute agreement statistics (Cohen's kappa with 95% CI, PABAK,
                percentage agreement, prevalence/bias indices) and list conflicts.
status          Progress of the parallel screening: which batches Reviewer A and
                Reviewer B have completed, missing/duplicate records, ready to merge?
make-batches    Create pilot (random sample) or full-text batches for both reviewers.
consensus-merge Combine the two reviewers' independent consensus statements; list the
                remaining conflicts for the human arbiter.
apply-consensus Add consensus/arbiter decisions to the merged file -> final decisions.
prisma          Build PRISMA 2020 flow-diagram counts (JSON + SVG + Markdown).
export-asreview Write a CSV that ASReview LAB can import with prior labels
                (column ``asreview_label``: 1 = include, 0 = exclude).

Parallel layout (each reviewer writes only into its own folder, one file per batch)
-----------------------------------------------------------------------------------
screening/batches/batch_001.csv            input batches (title/abstract)
screening/batches_pilot/batch_pilot.csv    calibration sample
screening/batches_fulltext/batch_001.csv   full-text batches
screening/reviewer_A/<stage>/batch_001.csv Reviewer A decisions   (stage: pilot|tiab|fulltext)
screening/reviewer_B/<stage>/batch_001.csv Reviewer B decisions

Decision file format (one row per record and reviewer)
------------------------------------------------------
record_id, reviewer, stage, decision, exclusion_reason, criterion, confidence, rationale
  stage     : tiab | fulltext
  decision  : include | exclude | unclear
  criterion : the eligibility domain that failed (P, I/E, C, O, S, T, L, other)
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import html
import json
import math
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

DECISIONS = ("include", "exclude", "unclear")
DECISION_COLUMNS = [
    "record_id",
    "reviewer",
    "stage",
    "decision",
    "exclusion_reason",
    "criterion",
    "confidence",
    "rationale",
]

# --------------------------------------------------------------------------- #
# Reading bibliographic exports
# --------------------------------------------------------------------------- #

RIS_MAP = {
    "TI": "title",
    "T1": "title",
    "AB": "abstract",
    "N2": "abstract",
    "AU": "authors",
    "A1": "authors",
    "PY": "year",
    "Y1": "year",
    "DA": "year",
    "DO": "doi",
    "JO": "journal",
    "JF": "journal",
    "T2": "journal",
    "KW": "keywords",
    "AN": "accession",
    "UR": "url",
    "LA": "language",
    "M3": "publication_type",
    "PT": "publication_type",
}


def _read_ris(path: Path) -> list[dict]:
    records, cur = [], {}
    tag_re = re.compile(r"^([A-Z][A-Z0-9])  - ?(.*)$")
    with path.open(encoding="utf-8-sig", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\n\r")
            m = tag_re.match(line)
            if not m:
                continue
            tag, val = m.group(1), m.group(2).strip()
            if tag == "ER":
                if cur:
                    records.append(cur)
                cur = {}
                continue
            field = RIS_MAP.get(tag)
            if not field:
                continue
            if field in ("authors", "keywords"):
                cur.setdefault(field, []).append(val)
            elif field == "year":
                y = re.search(r"(1[89]|20)\d\d", val)
                if y and "year" not in cur:
                    cur["year"] = y.group(0)
            elif field not in cur or not cur[field]:
                cur[field] = val
    if cur:
        records.append(cur)
    out = []
    for r in records:
        r = dict(r)
        for k in ("authors", "keywords"):
            if isinstance(r.get(k), list):
                r[k] = "; ".join(r[k])
        acc = r.pop("accession", "")
        if acc and acc.isdigit():
            r.setdefault("pmid", acc)
        out.append(r)
    return out


def _read_table(path: Path) -> list[dict]:
    delim = "\t" if path.suffix.lower() in (".tsv", ".txt") else ","
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delim)
        rows = []
        for row in reader:
            norm = {}
            for k, v in row.items():
                if k is None:
                    continue
                key = k.strip().lower().replace(" ", "_")
                key = {
                    "primary_title": "title",
                    "abstract_note": "abstract",
                    "notes_abstract": "abstract",
                    "author": "authors",
                    "publication_year": "year",
                    "source_title": "journal",
                    "publication_title": "journal",
                    "journal/book": "journal",
                    "pubmed_id": "pmid",
                }.get(key, key)
                norm[key] = (v or "").strip()
            rows.append(norm)
        return rows


def read_records(path: Path) -> list[dict]:
    if path.suffix.lower() in (".ris", ".nbib", ".enw"):
        if path.suffix.lower() == ".nbib":
            sys.exit("MEDLINE .nbib: please export as RIS or CSV from PubMed.")
        return _read_ris(path)
    return _read_table(path)


# --------------------------------------------------------------------------- #
# prepare
# --------------------------------------------------------------------------- #


def _norm_title(t: str) -> str:
    t = html.unescape(t or "").lower()
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _norm_doi(d: str) -> str:
    d = (d or "").strip().lower()
    d = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", d)
    return d


def cmd_prepare(a: argparse.Namespace) -> None:
    recs = []
    for p in a.inputs:
        src = Path(p)
        for r in read_records(src):
            r["source_file"] = src.name
            recs.append(r)
    if not recs:
        sys.exit("No records read.")

    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    seen_doi, seen_title = {}, {}
    fields = [
        "record_id",
        "title",
        "abstract",
        "authors",
        "year",
        "journal",
        "doi",
        "pmid",
        "keywords",
        "publication_type",
        "language",
        "source_file",
        "duplicate_of",
    ]
    rows = []
    for i, r in enumerate(recs, start=1):
        rid = f"R{i:05d}"
        doi = _norm_doi(r.get("doi", ""))
        tkey = (_norm_title(r.get("title", "")), (r.get("year") or "")[:4])
        dup = ""
        if doi and doi in seen_doi:
            dup = seen_doi[doi]
        elif tkey[0] and len(tkey[0]) > 20 and tkey in seen_title:
            dup = seen_title[tkey]
        if doi and doi not in seen_doi:
            seen_doi[doi] = rid
        if tkey[0] and tkey not in seen_title:
            seen_title[tkey] = rid
        row = {f: r.get(f, "") for f in fields}
        row.update(record_id=rid, doi=doi, duplicate_of=dup)
        rows.append(row)

    with (out_dir / "records_all.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    unique = [r for r in rows if not r["duplicate_of"]]
    with (out_dir / "records.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(unique)

    bdir = out_dir / "batches"
    bdir.mkdir(exist_ok=True)
    n_batches = 0
    for start in range(0, len(unique), a.batch_size):
        n_batches += 1
        chunk = unique[start : start + a.batch_size]
        with (bdir / f"batch_{n_batches:03d}.csv").open(
            "w", newline="", encoding="utf-8"
        ) as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(chunk)

    summary = {
        "records_identified": len(rows),
        "duplicates_flagged_automatically": len(rows) - len(unique),
        "records_after_deduplication": len(unique),
        "per_source_file": dict(Counter(r["source_file"] for r in rows)),
        "batches": n_batches,
        "batch_size": a.batch_size,
        "missing_abstract": sum(1 for r in unique if not r["abstract"].strip()),
        "note": "Automatic de-duplication is conservative (exact DOI or exact "
        "normalised title+year). Check records_all.csv and use a reference "
        "manager (EndNote/Zotero/Rayyan/Covidence) for the final de-duplication.",
        "created": _dt.datetime.now().isoformat(timespec="seconds"),
    }
    (out_dir / "prepare_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


# --------------------------------------------------------------------------- #
# Agreement statistics
# --------------------------------------------------------------------------- #


def cohen_kappa(pairs: list[tuple[str, str]], categories: list[str]) -> dict:
    """Cohen's kappa with the large-sample SE (Fleiss, Cohen & Everitt 1969)."""
    n = len(pairs)
    if n == 0:
        return {"n": 0}
    k = len(categories)
    idx = {c: i for i, c in enumerate(categories)}
    m = [[0] * k for _ in range(k)]
    for x, y in pairs:
        m[idx[x]][idx[y]] += 1
    p = [[m[i][j] / n for j in range(k)] for i in range(k)]
    row = [sum(p[i]) for i in range(k)]
    col = [sum(p[i][j] for i in range(k)) for j in range(k)]
    po = sum(p[i][i] for i in range(k))
    pe = sum(row[i] * col[i] for i in range(k))
    res = {
        "n": n,
        "categories": categories,
        "matrix_rowsA_colsB": m,
        "percent_agreement": round(100 * po, 1),
        "expected_agreement": round(pe, 4),
    }
    if pe >= 1:
        res.update(kappa=None, note="Kappa undefined (only one category used).")
        return res
    kappa = (po - pe) / (1 - pe)
    # Asymptotic variance of kappa (Fleiss et al. 1969)
    a_term = sum(
        p[i][i] * (1 - (row[i] + col[i]) * (1 - kappa)) ** 2 for i in range(k)
    )
    b_term = (1 - kappa) ** 2 * sum(
        p[i][j] * (col[i] + row[j]) ** 2 for i in range(k) for j in range(k) if i != j
    )
    c_term = (kappa - pe * (1 - kappa)) ** 2
    var = max((a_term + b_term - c_term) / (n * (1 - pe) ** 2), 0.0)
    se = math.sqrt(var)
    pabak = (k * po - 1) / (k - 1)
    res.update(
        kappa=round(kappa, 3),
        se=round(se, 4),
        ci95=[round(max(-1.0, kappa - 1.96 * se), 3), round(min(1.0, kappa + 1.96 * se), 3)],
        pabak=round(pabak, 3),
        interpretation_landis_koch=_landis_koch(kappa),
        interpretation_mchugh=_mchugh(kappa),
    )
    if k == 2:
        a_, b_, c_, d_ = m[0][0], m[0][1], m[1][0], m[1][1]
        res["prevalence_index"] = round(abs(a_ - d_) / n, 3)
        res["bias_index"] = round(abs(b_ - c_) / n, 3)
    return res


def _landis_koch(k: float) -> str:
    if k < 0:
        return "poor"
    for lim, lab in ((0.20, "slight"), (0.40, "fair"), (0.60, "moderate"), (0.80, "substantial")):
        if k <= lim:
            return lab
    return "almost perfect"


def _mchugh(k: float) -> str:
    for lim, lab in ((0.20, "none"), (0.39, "minimal"), (0.59, "weak"), (0.79, "moderate"), (0.90, "strong")):
        if k <= lim:
            return lab
    return "almost perfect"


# --------------------------------------------------------------------------- #
# merge
# --------------------------------------------------------------------------- #


def _decision_files(path: Path) -> list[Path]:
    if path.is_dir():
        files = sorted(p for p in path.glob("*.csv") if not p.name.startswith("."))
        if not files:
            sys.exit(f"{path}: no decision CSV files found")
        return files
    if not path.exists():
        sys.exit(f"{path}: not found")
    return [path]


def _read_decisions(path: Path, stage: str) -> "OrderedDict[str, dict]":
    """Read one decision CSV or a folder of per-batch decision CSVs."""
    out: "OrderedDict[str, dict]" = OrderedDict()
    for f in _decision_files(path):
        _read_decision_file(f, stage, out)
    return out


def _read_decision_file(path: Path, stage: str, out: "OrderedDict[str, dict]") -> None:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            row = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
            row_stage = row.get("stage", stage).lower() or stage
            if row_stage != stage and not (stage == "tiab" and row_stage == "pilot"):
                continue
            dec = row.get("decision", "").lower()
            dec = {"in": "include", "ex": "exclude", "maybe": "unclear", "?": "unclear"}.get(dec, dec)
            if dec not in DECISIONS:
                sys.exit(f"{path}: invalid decision '{row.get('decision')}' for {row.get('record_id')}")
            row["decision"] = dec
            rid = row.get("record_id", "")
            if not rid:
                sys.exit(f"{path}: row without record_id")
            if rid in out:
                sys.exit(f"{path}: duplicate decision for {rid} (record screened twice by the same reviewer)")
            out[rid] = row


def cmd_merge(a: argparse.Namespace) -> None:
    label = a.stage
    if a.stage == "pilot":
        a.stage = "tiab"
    A = _read_decisions(Path(a.a), a.stage)
    B = _read_decisions(Path(a.b), a.stage)
    missing_a = sorted(set(B) - set(A))
    missing_b = sorted(set(A) - set(B))
    if (missing_a or missing_b) and not a.allow_missing:
        sys.exit(
            f"Decision sets differ. Missing in A: {missing_a[:10]}... "
            f"Missing in B: {missing_b[:10]}... (use --allow-missing to continue)"
        )
    ids = [r for r in A if r in B]

    titles = {}
    if a.records:
        for r in _read_table(Path(a.records)):
            titles[r.get("record_id", "")] = r.get("title", "")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    merged, conflicts = [], []
    for rid in ids:
        da, db = A[rid]["decision"], B[rid]["decision"]
        if a.stage == "tiab":
            # At title/abstract level 'unclear' is forwarded to full text.
            fa = "exclude" if da == "exclude" else "forward"
            fb = "exclude" if db == "exclude" else "forward"
            agree = fa == fb
            status = ("forward_to_fulltext" if fa == "forward" else "excluded") if agree else "conflict"
        else:
            agree = da == db and da != "unclear"
            status = {"include": "included", "exclude": "excluded"}.get(da, "conflict") if agree else "conflict"
        row = {
            "record_id": rid,
            "title": titles.get(rid, ""),
            "decision_A": da,
            "reason_A": A[rid].get("exclusion_reason", ""),
            "confidence_A": A[rid].get("confidence", ""),
            "rationale_A": A[rid].get("rationale", ""),
            "decision_B": db,
            "reason_B": B[rid].get("exclusion_reason", ""),
            "confidence_B": B[rid].get("confidence", ""),
            "rationale_B": B[rid].get("rationale", ""),
            "agreement": "yes" if agree else "no",
            "status": status,
        }
        merged.append(row)
        if not agree:
            conflicts.append(row)

    cols = list(merged[0].keys()) if merged else ["record_id"]
    for name, data in (("merged_" + label, merged), ("conflicts_" + label, conflicts)):
        with (out / f"{name}.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(data)

    if a.stage == "tiab":
        bin_pairs = [
            ("exclude" if A[r]["decision"] == "exclude" else "forward",
             "exclude" if B[r]["decision"] == "exclude" else "forward")
            for r in ids
        ]
        primary = cohen_kappa(bin_pairs, ["forward", "exclude"])
    else:
        bin_pairs = [(A[r]["decision"], B[r]["decision"]) for r in ids]
        primary = cohen_kappa(bin_pairs, list(DECISIONS))
    three = cohen_kappa([(A[r]["decision"], B[r]["decision"]) for r in ids], list(DECISIONS))

    stats = {
        "stage": a.stage,
        "records_compared": len(ids),
        "missing_in_A": missing_a,
        "missing_in_B": missing_b,
        "decisions_A": dict(Counter(A[r]["decision"] for r in ids)),
        "decisions_B": dict(Counter(B[r]["decision"] for r in ids)),
        "conflicts": len(conflicts),
        "status_counts": dict(Counter(r["status"] for r in merged)),
        "kappa_primary": primary,
        "kappa_three_category": three,
        "exclusion_reasons_A": dict(Counter(A[r].get("exclusion_reason", "") for r in ids if A[r]["decision"] == "exclude")),
        "exclusion_reasons_B": dict(Counter(B[r].get("exclusion_reason", "") for r in ids if B[r]["decision"] == "exclude")),
        "created": _dt.datetime.now().isoformat(timespec="seconds"),
    }
    stats["stage"] = label
    (out / f"agreement_{label}.json").write_text(json.dumps(stats, indent=2))

    k = primary.get("kappa")
    ci = primary.get("ci95", ["NA", "NA"])
    print(json.dumps({k_: stats[k_] for k_ in ("stage", "records_compared", "conflicts", "status_counts")}, indent=2))
    print(
        f"\nReporting sentence: Inter-rater agreement at the "
        f"{ {'pilot': 'calibration (pilot)', 'tiab': 'title/abstract', 'fulltext': 'full-text'}[label] } stage was "
        f"{primary.get('percent_agreement')}% (Cohen's kappa = {k}, 95% CI {ci[0]} to {ci[1]}; "
        f"PABAK = {primary.get('pabak')}), n = {len(ids)} records."
    )


# --------------------------------------------------------------------------- #
# status (parallel progress)
# --------------------------------------------------------------------------- #


def _batch_ids(path: Path) -> list[str]:
    return [r.get("record_id", "") for r in _read_table(path) if r.get("record_id")]


def cmd_status(a: argparse.Namespace) -> None:
    root = Path(a.root)
    bdir = Path(a.batches) if a.batches else root / {"tiab": "batches", "pilot": "batches_pilot", "fulltext": "batches_fulltext"}[a.stage]
    batches = sorted(bdir.glob("*.csv"))
    if not batches:
        sys.exit(f"No input batches in {bdir}")
    report, todo = [], {"A": [], "B": []}
    for b in batches:
        ids = set(_batch_ids(b))
        line = {"batch": b.name, "records": len(ids)}
        for rev in ("A", "B"):
            f = root / f"reviewer_{rev}" / a.stage / b.name
            if not f.exists():
                line[rev] = "open"
                todo[rev].append(b.name)
                continue
            got = OrderedDict()
            try:
                _read_decision_file(f, "tiab" if a.stage == "pilot" else a.stage, got)
            except SystemExit as e:
                line[rev] = f"INVALID ({e})"
                todo[rev].append(b.name)
                continue
            missing, extra = ids - set(got), set(got) - ids
            if missing or extra:
                line[rev] = f"incomplete (missing {len(missing)}, foreign {len(extra)})"
                todo[rev].append(b.name)
            else:
                line[rev] = "done"
        report.append(line)
    print(f"{'batch':<22}{'n':>5}  {'Reviewer A':<34}{'Reviewer B':<34}")
    for r in report:
        print(f"{r['batch']:<22}{r['records']:>5}  {r['A']:<34}{r['B']:<34}")
    ready = not todo["A"] and not todo["B"]
    summary = {"stage": a.stage, "batches": len(batches), "open_A": todo["A"], "open_B": todo["B"], "ready_to_merge": ready}
    print(json.dumps(summary, indent=2))
    sys.exit(0 if ready else 3)


# --------------------------------------------------------------------------- #
# make-batches (pilot sample / full-text set)
# --------------------------------------------------------------------------- #


def _write_batches(rows: list[dict], fields: list[str], out: Path, size: int, prefix: str = "batch") -> int:
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for start in range(0, len(rows), size):
        n += 1
        name = f"{prefix}_{n:03d}.csv"
        with (out / name).open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows[start : start + size])
    return n


def cmd_make_batches(a: argparse.Namespace) -> None:
    import random

    recs = _read_table(Path(a.records))
    fields = list(recs[0].keys()) if recs else ["record_id"]
    if a.kind == "pilot":
        if a.n:
            n = a.n
        elif len(recs) >= 500:
            n = max(50, min(100, round(len(recs) * 0.1)))
        else:
            n = max(1, round(len(recs) * 0.1))
        n = min(n, len(recs))
        rnd = random.Random(a.seed)
        sample = sorted(rnd.sample(recs, n), key=lambda r: r.get("record_id", ""))
        nb = _write_batches(sample, fields, Path(a.out), a.batch_size or n, prefix="batch_pilot")
        print(json.dumps({"kind": "pilot", "records": n, "seed": a.seed, "batches": nb, "out": a.out}, indent=2))
        return
    if not a.final:
        sys.exit("--final final_tiab.csv is required for full-text batches")
    keep = {r["record_id"] for r in _read_table(Path(a.final)) if r.get("final_decision") == "include"}
    rows = [r for r in recs if r.get("record_id") in keep]
    for r in rows:
        r["fulltext_path"] = f"fulltexts/{r['record_id']}.pdf"
    fields = fields + (["fulltext_path"] if "fulltext_path" not in fields else [])
    nb = _write_batches(rows, fields, Path(a.out), a.batch_size or 10)
    print(json.dumps({"kind": "fulltext", "records": len(rows), "batches": nb, "out": a.out}, indent=2))


# --------------------------------------------------------------------------- #
# apply-consensus
# --------------------------------------------------------------------------- #


def cmd_apply_consensus(a: argparse.Namespace) -> None:
    merged = _read_table(Path(a.merged))
    cons = {}
    for cf in a.consensus:
        with Path(cf).open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                row = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
                if row.get("final_decision", "").lower() in ("include", "exclude"):
                    cons[row["record_id"]] = row
    unresolved = []
    for r in merged:
        if r["status"] != "conflict":
            r["final_decision"] = {"forward_to_fulltext": "include", "included": "include"}.get(r["status"], "exclude")
            r["resolved_by"] = "agreement"
            r["final_reason"] = r.get("reason_a") or r.get("reason_b") or ""
            continue
        c = cons.get(r["record_id"])
        if not c or c.get("final_decision", "").lower() not in ("include", "exclude"):
            unresolved.append(r["record_id"])
            r["final_decision"], r["resolved_by"], r["final_reason"] = "", "", ""
            continue
        r["final_decision"] = c["final_decision"].lower()
        r["resolved_by"] = c.get("resolved_by", "consensus")
        r["final_reason"] = c.get("exclusion_reason", "")
    out = Path(a.out)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(merged[0].keys()))
        w.writeheader()
        w.writerows(merged)
    print(json.dumps({
        "final_include": sum(1 for r in merged if r["final_decision"] == "include"),
        "final_exclude": sum(1 for r in merged if r["final_decision"] == "exclude"),
        "resolved_by": dict(Counter(r["resolved_by"] for r in merged)),
        "unresolved": unresolved,
    }, indent=2))
    if unresolved:
        sys.exit(f"{len(unresolved)} conflicts still unresolved.")


# --------------------------------------------------------------------------- #
# consensus-merge: combine both reviewers' (parallel) consensus statements
# --------------------------------------------------------------------------- #


def cmd_consensus_merge(a: argparse.Namespace) -> None:
    conflicts = _read_table(Path(a.conflicts))
    stA = {r["record_id"]: r for r in _read_table(Path(a.a))}
    stB = {r["record_id"]: r for r in _read_table(Path(a.b))}
    out_rows, arb = [], []
    for c in conflicts:
        rid = c["record_id"]
        da = (stA.get(rid, {}).get("decision") or "").lower()
        db = (stB.get(rid, {}).get("decision") or "").lower()
        if da and da == db and da in ("include", "exclude"):
            reason = stA[rid].get("exclusion_reason") or stB[rid].get("exclusion_reason") or ""
            out_rows.append({"record_id": rid, "final_decision": da, "exclusion_reason": reason if da == "exclude" else "", "resolved_by": "consensus"})
        elif a.stage in ("tiab", "pilot") and "exclude" not in (da, db) and (da or db):
            out_rows.append({"record_id": rid, "final_decision": "include", "exclusion_reason": "", "resolved_by": "consensus (unclear -> full text)"})
        else:
            arb.append({"record_id": rid, "title": c.get("title", ""),
                        "A_position": da, "A_argument": stA.get(rid, {}).get("argument", ""),
                        "B_position": db, "B_argument": stB.get(rid, {}).get("argument", "")})
    with Path(a.out).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["record_id", "final_decision", "exclusion_reason", "resolved_by"])
        w.writeheader()
        w.writerows(out_rows)
    if arb:
        with Path(a.arbiter_out).open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(arb[0].keys()) + ["final_decision", "exclusion_reason", "resolved_by"])
            w.writeheader()
            w.writerows(arb)
    print(json.dumps({"conflicts": len(conflicts), "resolved_by_consensus": len(out_rows),
                      "needs_human_arbiter": len(arb), "arbiter_file": a.arbiter_out if arb else None}, indent=2))


# --------------------------------------------------------------------------- #
# prisma
# --------------------------------------------------------------------------- #

PRISMA_KEYS = [
    "databases",               # {"MEDLINE (PubMed)": 512, "Embase": 640, ...}
    "registers",               # {"CENTRAL": 80, "ClinicalTrials.gov": 12}
    "duplicates_removed",
    "automation_removed",      # removed by automation tools before screening
    "other_removed",
    "records_screened",
    "records_excluded",
    "reports_sought",
    "reports_not_retrieved",
    "reports_assessed",
    "reports_excluded",        # {"wrong population": 3, "wrong design": 7, ...}
    "studies_included",
    "reports_included",
    # optional "other methods" arm
    "other_sources",           # {"Citation searching": 20, "Websites": 3}
    "other_reports_sought",
    "other_reports_not_retrieved",
    "other_reports_assessed",
    "other_reports_excluded",
]


def _sum(v) -> int:
    if isinstance(v, dict):
        return sum(int(x) for x in v.values())
    return int(v or 0)


def _check_prisma(c: dict) -> list[str]:
    errs = []
    ident = _sum(c.get("databases")) + _sum(c.get("registers"))
    removed = _sum(c.get("duplicates_removed")) + _sum(c.get("automation_removed")) + _sum(c.get("other_removed"))
    if c.get("records_screened") is not None and ident - removed != _sum(c["records_screened"]):
        errs.append(f"identified ({ident}) - removed ({removed}) != screened ({c['records_screened']})")
    if c.get("reports_sought") is not None and _sum(c["records_screened"]) - _sum(c.get("records_excluded")) != _sum(c["reports_sought"]):
        errs.append("screened - excluded != reports sought")
    if c.get("reports_assessed") is not None and _sum(c["reports_sought"]) - _sum(c.get("reports_not_retrieved")) != _sum(c["reports_assessed"]):
        errs.append("sought - not retrieved != assessed")
    inc_db = _sum(c.get("reports_assessed")) - _sum(c.get("reports_excluded"))
    inc_other = _sum(c.get("other_reports_assessed")) - _sum(c.get("other_reports_excluded"))
    if c.get("reports_included") is not None and inc_db + inc_other != _sum(c["reports_included"]):
        errs.append(f"assessed - excluded ({inc_db}+{inc_other}) != reports included ({c['reports_included']})")
    return errs


def _box(x, y, w, h, lines, fill="#ffffff"):
    t = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#000" stroke-width="1"/>']
    ty = y + 18
    for ln in lines:
        weight = "bold" if ln.startswith("**") else "normal"
        indent = 20 if ln.startswith(" ") else 0
        ln = ln.strip("*").strip()
        t.append(f'<text x="{x + 8 + indent}" y="{ty}"font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="{weight}">{html.escape(ln)}</text>')
        ty += 16
    return "\n".join(t)


def _arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" stroke-width="1.2" marker-end="url(#ah)"/>'


def _dict_lines(prefix: str, v) -> list[str]:
    if isinstance(v, dict):
        return [f"{prefix} (n = {_sum(v)})"] + [f"   {k} (n = {n})" for k, n in v.items()]
    return [f"{prefix} (n = {_sum(v)})"]


def render_prisma_svg(c: dict) -> str:
    W, BW, X1, X2 = 900, 380, 20, 480
    other = bool(c.get("other_sources"))
    parts = []
    ident = _dict_lines("Records identified from databases", c.get("databases", {}))
    if c.get("registers"):
        ident += _dict_lines("Records identified from registers", c["registers"])
    rem = [
        "Records removed before screening:",
        f"   Duplicate records (n = {_sum(c.get('duplicates_removed'))})",
        f"   Marked ineligible by automation tools (n = {_sum(c.get('automation_removed'))})",
        f"   Removed for other reasons (n = {_sum(c.get('other_removed'))})",
    ]
    h1 = max(len(ident), len(rem)) * 16 + 14
    y = 60
    parts.append(_box(X1, y, BW, h1, ident))
    parts.append(_box(X2, y, BW, h1, rem))
    parts.append(_arrow(X1 + BW, y + h1 / 2, X2, y + h1 / 2))
    rows = [
        ([f"Records screened (n = {_sum(c.get('records_screened'))})"],
         [f"Records excluded (n = {_sum(c.get('records_excluded'))})"]),
        ([f"Reports sought for retrieval (n = {_sum(c.get('reports_sought'))})"],
         [f"Reports not retrieved (n = {_sum(c.get('reports_not_retrieved'))})"]),
        ([f"Reports assessed for eligibility (n = {_sum(c.get('reports_assessed'))})"],
         _dict_lines("Reports excluded", c.get("reports_excluded", {}))),
    ]
    prev_bottom = y + h1
    for left, right in rows:
        y = prev_bottom + 40
        h = max(len(left), len(right)) * 16 + 14
        parts.append(_arrow(X1 + BW / 2, prev_bottom, X1 + BW / 2, y))
        parts.append(_box(X1, y, BW, h, left))
        parts.append(_box(X2, y, BW, h, right))
        parts.append(_arrow(X1 + BW, y + h / 2, X2, y + h / 2))
        prev_bottom = y + h
    y = prev_bottom + 40
    inc = [
        f"Studies included in review (n = {_sum(c.get('studies_included'))})",
        f"Reports of included studies (n = {_sum(c.get('reports_included'))})",
    ]
    parts.append(_arrow(X1 + BW / 2, prev_bottom, X1 + BW / 2, y))
    parts.append(_box(X1, y, BW, len(inc) * 16 + 14, inc))
    total_h = y + len(inc) * 16 + 14 + 30
    width = W
    if other:
        # simple "other methods" column on the far right
        X3, BW3 = 900, 340
        width = X3 + BW3 + 20
        oy = 60
        ol = _dict_lines("Records identified from other methods", c["other_sources"])
        oh = len(ol) * 16 + 14
        parts.append(_box(X3, oy, BW3, oh, ol, fill="#f2f2f2"))
        blocks = [
            [f"Reports sought for retrieval (n = {_sum(c.get('other_reports_sought'))})"],
            [f"Reports not retrieved (n = {_sum(c.get('other_reports_not_retrieved'))})"],
            [f"Reports assessed for eligibility (n = {_sum(c.get('other_reports_assessed'))})"],
            _dict_lines("Reports excluded", c.get("other_reports_excluded", {})),
        ]
        pb = oy + oh
        for b in blocks:
            by = pb + 30
            bh = len(b) * 16 + 14
            parts.append(_arrow(X3 + BW3 / 2, pb, X3 + BW3 / 2, by))
            parts.append(_box(X3, by, BW3, bh, b, fill="#f2f2f2"))
            pb = by + bh
        total_h = max(total_h, pb + 30)
    header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_h}" viewBox="0 0 {width} {total_h}">'
        '<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
        '<path d="M0,0 L8,4 L0,8 z" fill="#000"/></marker></defs>'
        f'<rect width="{width}" height="{total_h}" fill="#fff"/>'
        '<text x="20" y="35" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="bold">'
        "PRISMA 2020 flow diagram - identification of studies via databases and registers"
        f"{' and other methods' if other else ''}</text>"
    )
    return header + "\n".join(parts) + "</svg>"


def cmd_prisma(a: argparse.Namespace) -> None:
    c = json.loads(Path(a.counts).read_text())
    unknown = sorted(set(c) - set(PRISMA_KEYS) - {"_comment"})
    errs = _check_prisma(c)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "prisma_flow.svg").write_text(render_prisma_svg(c), encoding="utf-8")
    md = ["| PRISMA 2020 box | n |", "|---|---|"]
    for k in PRISMA_KEYS:
        if k in c:
            v = c[k]
            if isinstance(v, dict):
                md.append(f"| {k} | {_sum(v)} |")
                md += [f"| &nbsp;&nbsp;{kk} | {vv} |" for kk, vv in v.items()]
            else:
                md.append(f"| {k} | {v} |")
    (out / "prisma_counts.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    if unknown:
        print(f"\nWARNING: unknown keys ignored: {unknown}")
    if errs:
        print("\nCONSISTENCY ERRORS (fix before publication):")
        for e in errs:
            print(" -", e)
        sys.exit(2)
    print("\nAll PRISMA counts are internally consistent. SVG written to", out / "prisma_flow.svg")


# --------------------------------------------------------------------------- #
# export-asreview
# --------------------------------------------------------------------------- #


def cmd_export_asreview(a: argparse.Namespace) -> None:
    recs = _read_table(Path(a.records))
    final = {}
    for r in _read_table(Path(a.final)):
        fd = r.get("final_decision", "")
        if fd in ("include", "exclude"):
            final[r["record_id"]] = 1 if fd == "include" else 0
    cols = ["record_id", "title", "abstract", "authors", "year", "journal", "doi", "keywords", "asreview_label"]
    labels = Counter()
    with Path(a.out).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in recs:
            r["asreview_label"] = final.get(r.get("record_id", ""), "")
            labels[r["asreview_label"]] += 1
            w.writerow(r)
    unknown = len(set(final) - {r.get("record_id", "") for r in recs})
    print(f"Wrote {a.out}: {labels[1]} included, {labels[0]} excluded, "
          f"{labels['']} unlabeled.")
    if unknown:
        print(f"WARNING: {unknown} decisions refer to record_ids not present in {a.records}.")


# --------------------------------------------------------------------------- #


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("prepare")
    s.add_argument("inputs", nargs="+", help="RIS/CSV/TSV exports")
    s.add_argument("--out", default="screening")
    s.add_argument("--batch-size", type=int, default=40)
    s.set_defaults(fn=cmd_prepare)

    s = sub.add_parser("merge")
    s.add_argument("--a", required=True, help="Reviewer A decision CSV")
    s.add_argument("--b", required=True, help="Reviewer B decision CSV")
    s.add_argument("--stage", choices=["pilot", "tiab", "fulltext"], default="tiab")
    s.add_argument("--records", help="records.csv (adds titles to the output)")
    s.add_argument("--out", default="screening")
    s.add_argument("--allow-missing", action="store_true")
    s.set_defaults(fn=cmd_merge)

    s = sub.add_parser("status")
    s.add_argument("--root", default="screening")
    s.add_argument("--stage", choices=["pilot", "tiab", "fulltext"], default="tiab")
    s.add_argument("--batches", help="input batch folder (default derived from stage)")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("make-batches")
    s.add_argument("kind", choices=["pilot", "fulltext"])
    s.add_argument("--records", required=True)
    s.add_argument("--final", help="final_tiab.csv (full-text batches)")
    s.add_argument("--out", required=True)
    s.add_argument("--n", type=int, help="pilot sample size")
    s.add_argument("--seed", type=int, default=20261106)
    s.add_argument("--batch-size", type=int)
    s.set_defaults(fn=cmd_make_batches)

    s = sub.add_parser("apply-consensus")
    s.add_argument("--merged", required=True)
    s.add_argument("--consensus", required=True, nargs="+",
                   help="CSV(s): record_id, final_decision, exclusion_reason, resolved_by (consensus file, completed arbiter file)")
    s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_apply_consensus)

    s = sub.add_parser("consensus-merge")
    s.add_argument("--conflicts", required=True)
    s.add_argument("--a", required=True, help="screening/reviewer_A/consensus_<stage>.csv")
    s.add_argument("--b", required=True, help="screening/reviewer_B/consensus_<stage>.csv")
    s.add_argument("--stage", choices=["pilot", "tiab", "fulltext"], default="tiab")
    s.add_argument("--out", required=True, help="consensus_<stage>.csv")
    s.add_argument("--arbiter-out", required=True, help="arbiter_<stage>.csv (to be completed by a human)")
    s.set_defaults(fn=cmd_consensus_merge)

    s = sub.add_parser("prisma")
    s.add_argument("--counts", required=True, help="JSON with PRISMA 2020 counts")
    s.add_argument("--out", default="screening/prisma")
    s.set_defaults(fn=cmd_prisma)

    s = sub.add_parser("export-asreview")
    s.add_argument("--records", required=True)
    s.add_argument("--final", required=True, help="final decisions CSV from apply-consensus")
    s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_export_asreview)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
