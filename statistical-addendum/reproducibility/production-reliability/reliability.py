#!/usr/bin/env python3
r"""
reliability.py — real inter-coder reliability (Fleiss' kappa + Krippendorff's alpha)
across the captured 3-coder outputs, for the methods section.

Why this exists: capture_and_icr.py reports RAW percent agreement (not chance-corrected),
which is not comparable to published kappa/alpha cutoffs. This computes the defensible
statistics:
  - Krippendorff's alpha  — ORDINAL for the 0-5 anchored fields (eth_*, *_strength,
    *_intensity, alignment), NOMINAL for categorical fields (value type, actor crosswalks,
    journal_source_type, etc.), and presence/absence for the 0/1 binary indicators.
  - Fleiss' kappa         — chance-corrected agreement for 3 raters (nominal), per field.
  - percent agreement     — for reference / bridge to the capture output.

Missing-value convention (matches findings.py): codes 8 (unclear) and 9 (N/A) are treated
as MISSING for reliability — they are missing-value markers, not points on the substantive
scale. Layer-N/A fields (e.g. gov_* for journals) therefore drop out automatically.

Units = documents; raters = claude/codex/pxy. Per-field N is small (4 docs/layer), so the
PER-FIELD numbers are noisy — read the POOLED instrument-level alphas as the headline, and
expect both to stabilise as the corpus grows.

Benchmarks (printed alongside): Krippendorff alpha >= .80 reliable, .667-.80 tentative;
Landis-Koch kappa .61-.80 substantial, .81-1.0 almost perfect, .41-.60 moderate.

Usage:
    python reliability.py --layer JRN
    python reliability.py --layer GOV
    python reliability.py --layer ALL      # pools GOV+JRN+FRM+INS (per-field still computed where applicable)

Methodology: DPPRA v2.9 FROZEN. Reads the filed 02_CODING_OUTPUTS tree.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import numpy as np
import krippendorff
from statsmodels.stats.inter_rater import fleiss_kappa

ROOT = Path(r"C:\Users\C_Sin\Full Dataset Project")
OUT = ROOT / "20_Coding_Pipeline" / "02_CODING_OUTPUTS"
REL = ROOT / "20_Coding_Pipeline" / "06_RELIABILITY"
CODERS = ["Claude", "Codex", "PXY"]   # default; override with --coders (v2.11 uses Claude,Codex,Gemini)
RATERS = tuple(c.lower() for c in CODERS)
MISSING = {8, 9}  # treated as NaN for reliability

# process/meta judgments — reported separately, excluded from the substantive headline
PROCESS = {"coding_confidence_code", "final_confidence_code", "human_review_flag_code"}

# v2.11 dropped these 7 presence binaries (degenerate ~100% constant, undefined alpha;
# adversarial RUN_02 Finding D). They no longer exist in v2.11+ data. Pass --exclude-deprecated
# to drop them when pooling mixed v2.10/v2.11 data; default OFF reproduces the v2.10 headline.
DEPRECATED_V211 = {
    "dppra_d_presence_code", "dppra_p1_presence_code", "dppra_p2_presence_code",
    "dppra_r_presence_code", "dppra_a_presence_code",
    "cb_cost_presence_binary_code", "cb_benefit_presence_binary_code",
}

# fields that share the 0-5 ordinal anchor set (pooled into the headline ordinal alpha)
NOMINAL_EXPLICIT = {
    "dominant_value_type_code", "responsibility_concentration_code", "cb_balance_code",
    "cb_distribution_direction_code", "cb_cost_evidence_label_code", "cb_benefit_evidence_label_code",
    "cb_primary_cost_bearer_code", "cb_primary_material_beneficiary_code", "cb_primary_value_capturer_code",
    "journal_source_type_code", "journal_method_type_code", "journal_method_evidence_label_code",
    "journal_level_of_analysis_code",
    # forum (FRM) categoricals — v2.8
    "learner_posture_code", "assessment_object_code", "external_link_boundary_code",
    "overall_dominant_valence_code",
}
ORDINAL_OTHER = {"decoupling_signal_code", "market_capture_signal_code"}  # ordinal but not 0-5 range


def classify(field: str) -> str:
    if field in NOMINAL_EXPLICIT:
        return "nominal"
    if field in ORDINAL_OTHER:
        return "ordinal_other"
    if field.endswith("_intensity_code") or field.endswith("_strength_code"):
        return "ordinal05"
    if field.startswith("eth_") and field.endswith("_code"):
        return "ordinal05"
    if field == "dppra_alignment_score_code":
        return "ordinal05"
    if field.endswith("_presence_code") or field.endswith("_binary_code") or field.endswith("_flag_code"):
        return "binary"
    if field.startswith("cb_cost_") or field.startswith("cb_benefit_"):
        return "binary"  # the 0/1 indicator subfields (label/intensity/strength already caught above)
    return "nominal"


def load_layer(layer: str):
    """Return {src: {coder_lower: {field: int}}} for a layer (or both if ALL)."""
    layers = ["GOV", "JRN", "FRM", "INS", "COR"] if layer == "ALL" else [layer]
    data = {}
    for lyr in layers:
        for src_dir in sorted((OUT / lyr / "Claude").glob("SRC_*")):
            src = src_dir.name
            rec = {}
            ok = True
            for coder in CODERS:
                fp = OUT / lyr / coder / src / f"{src}__coding_output.json"
                if not fp.is_file():
                    ok = False
                    break
                codes = json.load(open(fp, encoding="utf-8")).get("codes", {})
                clean = {}
                for k, v in codes.items():
                    if not k.endswith("_code"):
                        continue
                    try:
                        clean[k] = int(v)
                    except (TypeError, ValueError):
                        continue
                rec[coder.lower()] = clean
            if ok:
                data[f"{lyr}:{src}"] = rec
    return data


def _val(x):
    return np.nan if (x is None or int(x) in MISSING) else float(x)


def field_matrix(data, field):
    """3 x N matrix (raters x docs) of substantive values, NaN for missing/8/9/absent."""
    cols = []
    for src, rec in data.items():
        col = [_val(rec[c].get(field)) for c in RATERS]
        if sum(1 for v in col if not np.isnan(v)) >= 2:  # need >=2 raters to inform reliability
            cols.append(col)
    if not cols:
        return None
    return np.array(cols).T  # shape (3, N)


def alpha(mat, level):
    try:
        a = krippendorff.alpha(reliability_data=mat, level_of_measurement=level)
        return None if (a is None or np.isnan(a)) else round(float(a), 3)
    except Exception:
        return None


def fleiss(mat):
    """Fleiss kappa on docs where all 3 raters present; nominal."""
    complete = [mat[:, j] for j in range(mat.shape[1]) if not np.isnan(mat[:, j]).any()]
    if len(complete) < 2:
        return None
    cats = sorted({int(v) for col in complete for v in col})
    if len(cats) < 2:
        return None  # no variance -> kappa undefined
    idx = {c: i for i, c in enumerate(cats)}
    table = np.zeros((len(complete), len(cats)), dtype=int)
    for i, col in enumerate(complete):
        for v in col:
            table[i, idx[int(v)]] += 1
    try:
        return round(float(fleiss_kappa(table)), 3)
    except Exception:
        return None


def pct_agree(mat):
    complete = [mat[:, j] for j in range(mat.shape[1]) if not np.isnan(mat[:, j]).any()]
    if not complete:
        return None
    return round(sum(1 for col in complete if len(set(col)) == 1) / len(complete) * 100)


def kripp_band(a):
    if a is None: return "n/a"
    if a >= .80: return "reliable"
    if a >= .667: return "tentative"
    return "below threshold"


def pooled(data, fields, level, remap, raters=None):
    """Stack all (doc,field) into one reliability matrix and compute one alpha.
    Pass a 2-coder `raters` tuple to get the pairwise / coder-excluded value."""
    if raters is None:
        raters = RATERS
    cols = []
    for src, rec in data.items():
        for fi, field in enumerate(fields):
            col = [_val(rec[c].get(field)) for c in raters]
            if sum(1 for v in col if not np.isnan(v)) >= 2:
                if remap:  # make categories disjoint across fields so marginals stay clean
                    col = [v if np.isnan(v) else fi * 1000 + v for v in col]
                cols.append(col)
    if not cols:
        return None, 0
    mat = np.array(cols).T
    return alpha(mat, level), mat.shape[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", required=True, choices=["GOV", "JRN", "FRM", "INS", "COR", "ALL"])
    ap.add_argument("--exclude-deprecated", action="store_true",
                    help="drop the 7 v2.11-dropped presence binaries (use for v2.11+ pooled "
                         "analysis; default OFF preserves the v2.10 headline numbers)")
    ap.add_argument("--coders", default="Claude,Codex,PXY",
                    help="comma-separated 3-coder roster (v2.11: Claude,Codex,Gemini). "
                         "Only docs with ALL three present are included.")
    ap.add_argument("--run", default="",
                    help="run subfolder under 02_CODING_OUTPUTS (e.g. _RUN_04_v2.12); "
                         "default reads the base layer folders.")
    args = ap.parse_args()
    global CODERS, RATERS, OUT
    if args.run:
        OUT = OUT / args.run
    CODERS = [c.strip() for c in args.coders.split(",")]
    RATERS = tuple(c.lower() for c in CODERS)
    data = load_layer(args.layer)
    if not data:
        print(f"No captured 3-coder outputs found for {args.layer}.")
        return
    n_docs = len(data)

    # all candidate fields = union of code fields across coders, minus process fields
    drop = PROCESS | (DEPRECATED_V211 if args.exclude_deprecated else set())
    fields = sorted({k for rec in data.values() for c in rec.values() for k in c} - drop)
    if args.exclude_deprecated:
        print("[reliability] --exclude-deprecated: dropped 7 v2.11 presence binaries from scoring.")

    rows = []
    for f in fields:
        kind = classify(f)
        mat = field_matrix(data, f)
        if mat is None:
            continue  # field is N/A for this layer (all 8/9/absent)
        lvl = "ordinal" if kind in ("ordinal05", "ordinal_other") else "nominal"
        rows.append({
            "field": f, "type": kind, "n_docs": mat.shape[1],
            "pct_agree": pct_agree(mat),
            "fleiss_kappa": fleiss(mat),
            "kripp_alpha": alpha(mat, lvl),
        })

    # pooled instrument-level headline
    ord05 = [f for f in fields if classify(f) == "ordinal05"]
    nomf = [f for f in fields if classify(f) == "nominal"]
    binf = [f for f in fields if classify(f) == "binary"]
    a_ord, n_ord = pooled(data, ord05, "ordinal", remap=False)
    a_nom, n_nom = pooled(data, nomf, "nominal", remap=True)
    a_bin, n_bin = pooled(data, binf, "nominal", remap=False)  # shared 0/1 = absent/present

    # pairwise / coder-excluded sensitivity (each pair = reliability with the 3rd coder dropped)
    r0, r1, r2 = RATERS
    PAIRS = [(r0, r1), (r0, r2), (r1, r2)]
    EXCL = {(r0, r1): r2, (r0, r2): r1, (r1, r2): r0}
    GROUPS = [("ordinal_0_5", ord05, "ordinal", False),
              ("nominal", nomf, "nominal", True),
              ("binary", binf, "nominal", False)]
    pairwise = {g: {f"{a}+{b}": pooled(data, fl, lv, rm, raters=(a, b))[0] for a, b in PAIRS}
                for g, fl, lv, rm in GROUPS}

    # ---- report ----
    print(f"\n================ RELIABILITY — {args.layer}  ({n_docs} docs x 3 coders) ================")
    print("Headline (pooled instrument-level Krippendorff alpha):")
    print(f"  ORDINAL 0-5 fields (eth_*, *_strength, *_intensity, alignment): alpha = {a_ord}  [{kripp_band(a_ord)}]  (n={n_ord} judgements)")
    print(f"  NOMINAL fields (value type, actor crosswalks, journal_source_type ...): alpha = {a_nom}  [{kripp_band(a_nom)}]  (n={n_nom})")
    print(f"  BINARY presence/indicator fields (0/1):                                 alpha = {a_bin}  [{kripp_band(a_bin)}]  (n={n_bin})")
    print("  Benchmarks: alpha >= .80 reliable | .667-.80 tentative | < .667 below threshold.")

    print("\nPairwise & coder-excluded sensitivity (pooled alpha) — REPORT ALL, not just the best pair:")
    for g, label in [("ordinal_0_5", "ORDINAL 0-5"), ("nominal", "NOMINAL   "), ("binary", "BINARY    ")]:
        cells = []
        for a, b in PAIRS:
            val = pairwise[g][f"{a}+{b}"]
            cells.append(f"{a}+{b} (excl {EXCL[(a, b)]})={val}")
        print(f"  {label}: " + " | ".join(cells))
    print("  NB: the highest pair is a sensitivity diagnostic, NOT a headline reliability claim.")

    def show(title, kinds):
        sel = [r for r in rows if r["type"] in kinds]
        if not sel:
            return
        print(f"\n  --- per-field ({title}) — small N, read as indicative ---")
        print(f"  {'field':40s} {'n':>2} {'%agr':>5} {'FleissK':>8} {'Kalpha':>7}")
        for r in sorted(sel, key=lambda x: (x['kripp_alpha'] is None, x['kripp_alpha'] if x['kripp_alpha'] is not None else 0)):
            ka = '' if r['kripp_alpha'] is None else f"{r['kripp_alpha']:.3f}"
            fk = '' if r['fleiss_kappa'] is None else f"{r['fleiss_kappa']:.3f}"
            note = '' if r['kripp_alpha'] is not None else '  (no variance / unanimous)'
            print(f"  {r['field']:40s} {r['n_docs']:>2} {str(r['pct_agree'])+'%':>5} {fk:>8} {ka:>7}{note}")

    show("ordinal 0-5", {"ordinal05"})
    show("ordinal (other range)", {"ordinal_other"})
    show("nominal / categorical", {"nominal"})
    show("binary presence/indicators", {"binary"})

    # ---- write outputs ----
    REL.joinpath(args.layer).mkdir(parents=True, exist_ok=True)
    payload = {
        "layer": args.layer, "n_docs": n_docs, "coders": [c.lower() for c in CODERS],
        "missing_convention": "8 and 9 treated as missing",
        "headline_pooled_alpha": {"ordinal_0_5": a_ord, "nominal": a_nom, "binary": a_bin},
        "pairwise_pooled_alpha": pairwise,
        "pairwise_excludes": {f"{a}+{b}": EXCL[(a, b)] for a, b in PAIRS},
        "per_field": rows,
    }
    (REL / args.layer / "reliability_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with open(REL / args.layer / "reliability_per_field.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["field", "type", "n_docs", "pct_agree", "fleiss_kappa", "kripp_alpha"])
        w.writeheader(); w.writerows(rows)
    print(f"\n  wrote -> {REL / args.layer / 'reliability_report.json'}")
    print(f"  wrote -> {REL / args.layer / 'reliability_per_field.csv'}")


if __name__ == "__main__":
    main()
