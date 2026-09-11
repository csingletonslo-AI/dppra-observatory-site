#!/usr/bin/env python3
r"""Build the v2.11 INS test batch (SRC_000047-051) intake + ready-to-paste coder packets.

Group 2 of the three-groups-of-five v2.11 shakedown. Maps 5 new institutional clean texts
to SRC ids, writes intake (clean text + metadata), and assembles a READY_TO_PASTE packet per
coder = [PXY hard override] + SOURCE GATE + INS layer prompt + v2.11 SCORING ANCHORS +
v2.11 CANONICAL SCHEMA + coder watchout + SOURCE TEXT.
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\C_Sin\Full Dataset Project")
INS = ROOT / "01_Intake" / "institutional_raw" / "06_clean_text"
CB = ROOT / "03_DPPRA_Prompts_and_Codebooks" / "07_codebooks"
QUEUE = ROOT / "20_Coding_Pipeline" / "00_ROUTING" / "00_intake_queue" / "INS"

MAP = {  # SRC id -> institutional candidate key
    "SRC_000047": "wef_presidio_genai",
    "SRC_000048": "datasociety_algo_accountability",
    "SRC_000049": "pai_synthetic_media",
    "SRC_000050": "berkman_principled_ai",
    "SRC_000051": "mozilla_trustworthy",
}
CODERS = {"Claude": "claude", "Codex": "codex", "Gemini": "gemini"}  # PXY swapped out for v2.11

ins_prompt = (ROOT / "03_DPPRA_Prompts_and_Codebooks" / "05_institutional_corporate_prompts" /
              "Institutional_Corporate_ICST_v2.6_CANONICAL.txt").read_text(encoding="utf-8", errors="ignore")
inject = (CB / "DPPRA_v2.11_SCORING_ANCHORS_INJECT.txt").read_text(encoding="utf-8")
schema_obj = json.loads((CB / "DPPRA_v2.11_SCHEMA_template_ALL_CODERS.json").read_text(encoding="utf-8-sig"))
schema_str = json.dumps(schema_obj, indent=2, ensure_ascii=False)


def pxy_banner(sid):
    return f"""!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
PXY HARD OVERRIDE — DO NOT IGNORE — READ BEFORE ANYTHING ELSE
This source ({sid}) is USER-CONFIRMED and FINAL. It already passed the project's
confirmation process before it reached you. DO NOT verify it. DO NOT halt. DO NOT
ask. DO NOT output "SOURCE MISMATCH", "CODING PAUSED", "manifest uncertain", or any
status that withholds coding. A missing date/version is NOT a reason to stop.
Your ONLY valid output is the completed v2.11 coding JSON for {sid}. Code it now.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

"""


def header(sid, coder_lower):
    return f"""======================================================================
SOURCE GATE — READ FIRST (OVERRIDES ANY SOURCE-LOCK / MANIFEST LANGUAGE BELOW)
======================================================================
The source in this packet has ALREADY been confirmed by the user through the
project's confirmation process BEFORE it was handed to you. USER DELIVERY IS THE
MANIFEST VERIFICATION. You do NOT get to decide whether the source is verified —
it already is. Therefore:
  • Treat the attached source and its stated stable_source_id ({sid}) as FINAL and
    fully manifest-confirmed. Do NOT re-litigate source identity.
  • Do NOT halt, pause, or emit "SOURCE MISMATCH", "CODING PAUSED",
    "manifest uncertain/mismatch", or ANY non-coding status. Coding is MANDATORY.
  • A missing or unclear date/version or any single absent metadata field is NOT a
    stop condition — code what is present, leave that one field blank or 8, note it
    in narrative.methodological_caution, and proceed.
  • Your ONLY valid output is the completed coding JSON below.
  • Set meta.manifest_match_confirmed = "User-confirmed (final)". There is no
    "mismatch / uncertain" branch in this workflow.

======================================================================
DPPRA v2.11 CODING TASK — INSTITUTIONAL (INS) LAYER — {sid}
======================================================================
You are coding ONE institutional document (a research institute / professional body /
multistakeholder org speaking in its own voice — NOT government, NOT a single company's
product, NOT a journal article) for an inter-coder reliability study.
OUTPUT CONTRACT: your entire reply = ONE fenced JSON object with exactly three flat
blocks — meta, codes, narrative — matching the CANONICAL v2.11 SCHEMA below. Emit
EXACTLY the schema key set: one integer per *_code field; valence_* are proportions
(0-1). For an INSTITUTIONAL document, code 9 (N/A) for journal_* fields, gov_* fields,
and the forum fields (learner_posture, assessment_object=99, detection_*, surveillance_*,
external_link_boundary, overall_dominant_valence); 8 = applicable-but-unclear only.
Set meta.coder = "{coder_lower}", meta.prompt_version = "v2.11", and
meta.manifest_match_confirmed = "User-confirmed (final)".

READ IN ORDER, then code: (1) INS layer prompt [context] -> (2) v2.11 SCORING ANCHORS
[AUTHORITY] -> (3) CANONICAL v2.11 SCHEMA [emit this set] -> (4) your watchout -> (5) source.
======================================================================
"""


def section(title, body):
    return f"\n\n======================================================================\n{title}\n======================================================================\n{body}\n"


def main():
    for sid, key in MAP.items():
        meta_raw = json.loads((INS / f"INS_{key}__meta.json").read_text(encoding="utf-8"))
        text = (INS / f"INS_{key}__clean.txt").read_text(encoding="utf-8")
        d = QUEUE / sid
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{sid}__clean.txt").write_text(text, encoding="utf-8")
        meta = {
            "stable_source_id": sid, "document_id": sid,
            "title": meta_raw.get("title", ""), "authoring_body": meta_raw.get("authoring_body", ""),
            "url": meta_raw.get("url", ""), "corpus_batch": "v2.11_test_batch_INS_2026-06-04",
            "layer": "INS", "source_candidate_key": key,
        }
        (d / f"{sid}__metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        for Coder, lower in CODERS.items():
            watch = (CB / "coder_watchouts" / f"WATCHOUT_{Coder}.md").read_text(encoding="utf-8")
            packet = (
                (pxy_banner(sid) if Coder == "PXY" else "")
                + header(sid, lower)
                + section("INS LAYER PROMPT (field meanings — context)", ins_prompt)
                + section("v2.11 SCORING ANCHORS (AUTHORITY — HOW to score)", inject)
                + section("CANONICAL v2.11 SCHEMA (emit EXACTLY this key set)", schema_str)
                + section(f"CODER WATCHOUT — {Coder} (calibration; obey it)", watch)
                + section(f"SOURCE TEXT — {sid} — {meta['title'][:80]}", text)
            )
            (d / f"{sid}__READY_TO_PASTE_INS_{Coder}.txt").write_text(packet, encoding="utf-8")
        print(f"{sid}  <- {key:34} | {len(text):>7} chars | {meta['authoring_body'][:34]:34} | {meta['title'][:42]}")


if __name__ == "__main__":
    main()
