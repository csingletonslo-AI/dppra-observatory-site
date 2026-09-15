#!/usr/bin/env python3
"""Reproduce the 15 September 2026 inventory and missingness documentation.

Uses only the Python standard library and the six unchanged public source files
listed below. This is an inventory audit, not a reliability-analysis program.
"""

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

RELEASE = Path(__file__).resolve().parent
ROOT = RELEASE.parents[2]
REPRO = "statistical-addendum/reproducibility/"
SOURCE_COMMIT = "f23bfa2ad63ee4700852e8fc6f31edc3cac83051"
SOURCES = {
    REPRO + "instrument/v2.14/GOV__Claude.txt": "26187e6bd0f982e2e649829f1aaaf5f903d873f4",
    REPRO + "ordinal_ratings.csv": "cab54e2eb000503e626ad049e2f855becb6a17ac",
    REPRO + "field_inventory.csv": "ce6ff4ac0d2d09b5c309e375eba357e6ca0b1c49",
    REPRO + "nominal-2026-09-14/nominal_inputs.csv": "c7d47ed77a60d5febe5e50df7c3c32c41215897d",
    REPRO + "nominal-2026-09-14/nominal_results.json": "063eed1047c0a33df7f6d8d36547e22f8de2e686",
    "observatory_site_data.json": "aa828b77dcaeae34408f16059c255240d70a7bff",
}
CODERS = ("Claude", "Codex", "Gemini")
DOMAIN = {
    "detection_verification_presence_strength_code": "FRM",
    "surveillance_monitoring_presence_strength_code": "FRM",
    "journal_evidence_quality_strength_code": "JRN",
}


def csv_rows(relative_path):
    with (ROOT / relative_path).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def csv_bytes(rows, columns):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def field_group(field, block):
    # Readable organization of the schema; not the production alpha classifier.
    if block == "narrative":
        return "narrative"
    if field in {"coding_confidence_code", "final_confidence_code", "human_review_flag_code"}:
        return "process/confidence"
    for prefix, group in [
        ("eth_", "ethical principles"), ("dppra_", "DPPRA"),
        ("int_", "integrity mechanisms"), ("cb_", "cost/benefit"),
        ("gov_", "government-specific"), ("journal_", "journal-specific"),
        ("valence_", "valence proportions"),
    ]:
        if field.startswith(prefix):
            return group
    if field in {
        "decoupling_signal_code", "market_capture_signal_code",
        "dominant_value_type_code", "responsibility_concentration_code",
    }:
        return "structural interpretation"
    return "forum-specific"


def build():
    source_hashes = {}
    for path, expected in SOURCES.items():
        payload = (ROOT / path).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
        if blob != expected:
            raise ValueError(f"Source bytes differ from the dated release: {path}")
        source_hashes[path] = {"git_blob_sha1": blob, "sha256": hashlib.sha256(payload).hexdigest()}

    packet = (ROOT / (REPRO + "instrument/v2.14/GOV__Claude.txt")).read_text(encoding="utf-8")
    tail = packet.split("CANONICAL OUTPUT SCHEMA — emit", 1)[1]
    schema, _ = json.JSONDecoder().raw_decode(tail[tail.index("{"):])
    codes = {key: value for key, value in schema["codes"].items() if not key.startswith("_")}
    narrative = schema["narrative"]
    assert len(codes) == 91 and len(narrative) == 16

    ordinal = csv_rows(REPRO + "ordinal_ratings.csv")
    inventory = {row["field"]: int(row["n_common_documents"])
                 for row in csv_rows(REPRO + "field_inventory.csv")}
    by_unit = defaultdict(dict)
    by_field_coder = defaultdict(list)
    docs = {}
    for row in ordinal:
        source, sector, field, coder = (row[key] for key in ("source_id", "sector", "field", "coder"))
        assert field in inventory and coder in CODERS
        if source in docs:
            assert docs[source] == sector
        docs[source] = sector
        unit = by_unit[(source, field)]
        assert coder not in unit
        rating = None if row["rating"] == "" else int(row["rating"])
        assert rating is None or 0 <= rating <= 5
        unit[coder] = rating
        by_field_coder[(field, coder)].append((source, sector, rating))
    assert len(docs) == 65 and len(inventory) == 29 and len(ordinal) == 5655
    assert len(by_unit) == 65 * 29
    assert all(set(unit) == set(CODERS) for unit in by_unit.values())
    common = Counter(field for (_, field), unit in by_unit.items()
                     if all(rating is not None for rating in unit.values()))
    assert dict(common) == inventory

    missing = []
    for field in sorted(inventory):
        for coder in CODERS:
            rows = by_field_coder[(field, coder)]
            assert len(rows) == 65
            outside = [row for row in rows if field in DOMAIN and row[1] != DOMAIN[field]]
            inside = [row for row in rows if field not in DOMAIN or row[1] == DOMAIN[field]]
            # Domain assignments are specified in the published instrument.
            assert all(row[2] is None for row in outside)
            missing.append({
                "field": field, "coder": coder, "applicable_sector": DOMAIN.get(field, "ALL"),
                "total_slots": len(rows), "valid_ratings": sum(row[2] is not None for row in rows),
                "blank_ratings": sum(row[2] is None for row in rows),
                "out_of_domain_blank_ratings": len(outside),
                "within_domain_blank_ratings": sum(row[2] is None for row in inside),
                "within_domain_blank_source_ids": ";".join(sorted(row[0] for row in inside if row[2] is None)),
            })

    nominal = csv_rows(REPRO + "nominal-2026-09-14/nominal_inputs.csv")
    nominal_common = Counter()
    nominal_fields = set()
    seen_nominal = set()
    for row in nominal:
        field = row["field"]
        key = (row["source_id"], field)
        assert key not in seen_nominal and docs[row["source_id"]] == row["sector"]
        seen_nominal.add(key)
        nominal_fields.add(field)
        excluded = {88, 99} if field == "assessment_object_code" else {8, 9}
        values = [int(row[coder]) if row[coder] else None for coder in CODERS]
        if all(value is not None and value not in excluded for value in values):
            nominal_common[field] += 1
    assert len(nominal_fields) == 17 and len(nominal) == 65 * 17
    assert set(inventory) <= set(codes) and nominal_fields <= set(codes)
    nominal_reference = json.loads((ROOT / (REPRO + "nominal-2026-09-14/nominal_results.json")).read_text(encoding="utf-8"))
    assert dict(nominal_common) == {row["field"]: row["complete_documents"] for row in nominal_reference["results"]}

    crosswalk = []
    for block, fields in [("codes", codes), ("narrative", narrative)]:
        for field, declaration in fields.items():
            crosswalk.append({
                "block": block, "field": field, "field_group": field_group(field, block),
                "archived_schema_declaration": declaration,
                "ordinal_battery": "yes" if field in inventory else "no",
                "ordinal_complete_documents": inventory.get(field, ""),
                "paired_nominal_battery": "yes" if field in nominal_fields else "no",
                "paired_nominal_complete_documents": nominal_common[field] if field in nominal_fields else "",
            })

    site = json.loads((ROOT / "observatory_site_data.json").read_text(encoding="utf-8"))
    manifest = [{"source_id": item["src_id"], "sector": item["sector_code"],
                 "title": item["title"], "author": item["author"], "year": item["year"]}
                for item in sorted(site["corpus_items"], key=lambda item: item["src_id"])]
    assert len(manifest) == 65 and len({item["source_id"] for item in manifest}) == 65
    assert {item["source_id"]: item["sector"] for item in manifest} == docs
    blank = sum(row["blank_ratings"] for row in missing)
    outside_blank = sum(row["out_of_domain_blank_ratings"] for row in missing)
    valid = len(ordinal) - blank
    complete = sum(common.values())
    summary = {
        "release": "2026-09-15", "source_commit": SOURCE_COMMIT,
        "scope": "Inventory and missingness documentation; no new statistical tests or pooled nominal/binary alpha reproduction.",
        "source_files": source_hashes,
        "coded_fields": len(codes), "narrative_fields": len(narrative),
        "ordinal_fields": len(inventory), "paired_nominal_fields": len(nominal_fields),
        "documents": len(docs), "sector_counts": dict(sorted(Counter(docs.values()).items())),
        "ordinal_slots": len(ordinal), "ordinal_blank_ratings": blank,
        "ordinal_out_of_domain_blanks": outside_blank,
        "ordinal_within_domain_blanks": blank - outside_blank,
        "ordinal_valid_ratings_before_matching": valid,
        "ordinal_common_document_field_units": complete,
        "ordinal_common_valid_ratings": complete * 3,
        "valid_ratings_excluded_by_common_matching": valid - complete * 3,
        "ordinal_blanks_by_coder": {coder: sum(row["blank_ratings"] for row in missing if row["coder"] == coder) for coder in CODERS},
        "paired_nominal_complete_documents": dict(sorted(nominal_common.items())),
    }
    assert (blank, outside_blank, valid, complete) == (472, 471, 5183, 1727)
    return {
        "field_crosswalk.csv": csv_bytes(crosswalk, list(crosswalk[0])),
        "ordinal_missingness.csv": csv_bytes(missing, list(missing[0])),
        "corpus_manifest.csv": csv_bytes(manifest, list(manifest[0])),
        "scope_audit.json": (json.dumps(summary, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=RELEASE / "generated")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    outputs = build()
    differences = []
    for name, content in outputs.items():
        reference = RELEASE / name
        if args.out_dir.resolve() != RELEASE.resolve() and (not reference.exists() or reference.read_bytes() != content):
            differences.append(name)
        (args.out_dir / name).write_bytes(content)
    if differences:
        raise SystemExit("Reference mismatch: " + ", ".join(differences))
    print(f"Verified six source files; wrote {len(outputs)} inventories to {args.out_dir}")
    print("91 coded + 16 narrative fields; 65 documents; 472 blanks = 471 out of domain + 1 within domain.")


if __name__ == "__main__":
    main()
