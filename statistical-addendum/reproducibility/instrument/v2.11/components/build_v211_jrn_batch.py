#!/usr/bin/env python3
r"""Build the v2.11 JRN test batch (SRC_000042-046) intake + ready-to-paste coder packets.

Maps 5 new journal clean texts -> SRC ids, writes intake (clean text + metadata), and assembles
a READY_TO_PASTE packet per coder = TASK/OUTPUT-CONTRACT + JRN layer prompt + v2.11 SCORING
ANCHORS + v2.11 CANONICAL SCHEMA + coder watchout + SOURCE TEXT.
"""
import json, shutil
from pathlib import Path

ROOT = Path(r"C:\Users\C_Sin\Full Dataset Project")
JR = ROOT / "01_Intake" / "journals_raw" / "Journal_Articles"
CB = ROOT / "03_DPPRA_Prompts_and_Codebooks" / "07_codebooks"
QUEUE = ROOT / "20_Coding_Pipeline" / "00_ROUTING" / "00_intake_queue" / "JRN"

MAP = {  # SRC id -> source candidate id
    "SRC_000042": "JRN_2026_0001", "SRC_000043": "JRN_2026_0002",
    "SRC_000044": "JRN_2026_0004", "SRC_000045": "JRN_2026_0005",
    "SRC_000046": "JRN_2026_0013",
}
CODERS = {"Claude": "claude", "Codex": "codex", "Gemini": "gemini"}  # PXY swapped out for v2.11

jrn_prompt = (ROOT / "03_DPPRA_Prompts_and_Codebooks" / "03_journal_prompts" /
              "Revised_Journal_DPPRA_Coding_Prompt_v2_6_SPSS_Ready.txt").read_text(encoding="utf-8", errors="ignore")
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
DPPRA v2.11 CODING TASK — JOURNAL (JRN) LAYER — {sid}
======================================================================
You are coding ONE journal article for an inter-coder reliability study.
OUTPUT CONTRACT: your entire reply = ONE fenced JSON object with exactly three
flat blocks — meta, codes, narrative — matching the CANONICAL v2.11 SCHEMA below.
Emit EXACTLY the schema key set: one integer per *_code field; valence_* are
proportions (0-1). Use 9 for definitionally-N/A fields (gov_* and forum fields on a
journal article), 8 only for applicable-but-unclear. Set meta.coder = "{coder_lower}",
meta.prompt_version = "v2.11", and meta.manifest_match_confirmed = "User-confirmed (final)".

READ IN THIS ORDER, then code:
  1. JRN LAYER PROMPT (field meanings)         — context
  2. v2.11 SCORING ANCHORS (HOW to score)      — AUTHORITY; supersedes any 0-5 text above
  3. CANONICAL v2.11 SCHEMA (the exact keys)   — emit this set
  4. YOUR CODER WATCHOUT                        — calibration; obey it
  5. SOURCE TEXT                                — the article to code
======================================================================
"""


def section(title, body):
    return f"\n\n======================================================================\n{title}\n======================================================================\n{body}\n"


def main():
    for sid, jid in MAP.items():
        meta_raw = json.loads((JR / "02_raw_metadata" / f"{jid}__metadata.json").read_text(encoding="utf-8"))
        text = (JR / "06_clean_text" / f"{jid}__clean.txt").read_text(encoding="utf-8")
        d = QUEUE / sid
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{sid}__clean.txt").write_text(text, encoding="utf-8")
        meta = {
            "stable_source_id": sid, "document_id": sid,
            "title": meta_raw.get("title", ""), "doi": meta_raw.get("doi", ""),
            "authoring_body": str(meta_raw.get("authorships") or meta_raw.get("authors") or meta_raw.get("author") or ""),
            "date": str(meta_raw.get("publication_year", meta_raw.get("year", ""))),
            "corpus_batch": "v2.11_test_batch_2026-06-04", "layer": "JRN",
            "source_candidate_id": jid,
        }
        (d / f"{sid}__metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        for Coder, lower in CODERS.items():
            watch = (CB / "coder_watchouts" / f"WATCHOUT_{Coder}.md").read_text(encoding="utf-8")
            packet = (
                (pxy_banner(sid) if Coder == "PXY" else "")
                + header(sid, lower)
                + section("JRN LAYER PROMPT (field meanings — context)", jrn_prompt)
                + section("v2.11 SCORING ANCHORS (AUTHORITY — HOW to score)", inject)
                + section("CANONICAL v2.11 SCHEMA (emit EXACTLY this key set)", schema_str)
                + section(f"CODER WATCHOUT — {Coder} (calibration; obey it)", watch)
                + section(f"SOURCE TEXT — {sid} — {meta['title'][:80]}", text)
            )
            (d / f"{sid}__READY_TO_PASTE_JRN_{Coder}.txt").write_text(packet, encoding="utf-8")
        print(f"{sid}  <- {jid}  | {len(text)} chars | packets: Claude/Codex/PXY | {meta['title'][:55]}")


if __name__ == "__main__":
    main()
