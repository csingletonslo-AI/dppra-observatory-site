#!/usr/bin/env python3
r"""Build the v2.11 COR test batch (SRC_000062-066) intake + ready-to-paste coder packets.

Group 5 (corporate). Maps 5 corporate AI-governance documents to SRC ids and assembles a
READY_TO_PASTE packet per coder = SOURCE GATE + ICST (institutional/corporate) layer prompt
+ v2.11 SCORING ANCHORS + v2.11 SCHEMA + coder watchout + SOURCE TEXT.
NOTE: for COR, gov_*, journal_*, and the forum fields = 9 (corporate self-published doc).
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\C_Sin\Full Dataset Project")
CR = ROOT / "01_Intake" / "corporate_raw" / "06_clean_text"
CB = ROOT / "03_DPPRA_Prompts_and_Codebooks" / "07_codebooks"
QUEUE = ROOT / "20_Coding_Pipeline" / "00_ROUTING" / "00_intake_queue" / "COR"

MAP = {
    "SRC_000062": "anthropic_core_views",
    "SRC_000063": "openai_preparedness",
    "SRC_000064": "salesforce_trusted_ai",
    "SRC_000065": "aws_responsible_ai",
    "SRC_000066": "ibm_ai_ethics",
}
CODERS = {"Claude": "claude", "Codex": "codex", "Gemini": "gemini"}

cor_prompt = (ROOT / "03_DPPRA_Prompts_and_Codebooks" / "05_institutional_corporate_prompts" /
              "Institutional_Corporate_ICST_v2.6_CANONICAL.txt").read_text(encoding="utf-8", errors="ignore")
inject = (CB / "DPPRA_v2.11_SCORING_ANCHORS_INJECT.txt").read_text(encoding="utf-8")
schema_obj = json.loads((CB / "DPPRA_v2.11_SCHEMA_template_ALL_CODERS.json").read_text(encoding="utf-8-sig"))
schema_str = json.dumps(schema_obj, indent=2, ensure_ascii=False)


def header(sid, coder_lower):
    return f"""======================================================================
SOURCE GATE — READ FIRST (OVERRIDES ANY SOURCE-LOCK / MANIFEST LANGUAGE BELOW)
======================================================================
The source in this packet was confirmed by the user BEFORE it reached you. USER
DELIVERY IS THE MANIFEST VERIFICATION. Treat {sid} as FINAL and fully manifest-
confirmed. Do NOT re-litigate identity, do NOT halt/pause/emit "SOURCE MISMATCH" or
any non-coding status. A missing single metadata field is not a stop condition.
Your ONLY valid output is the completed coding JSON. Set
meta.manifest_match_confirmed = "User-confirmed (final)".

======================================================================
DPPRA v2.11 CODING TASK — CORPORATE (COR) LAYER — {sid}
======================================================================
You are coding ONE corporate, self-published AI-governance document (a company's own
AI principles / safety framework / responsible-AI policy) for an inter-coder reliability
study. Read for the document's own discourse and commitments — and watch the say-do /
decoupling dimension (espoused values vs operationalized practice), which matters for
self-authored corporate sources.
OUTPUT CONTRACT: your entire reply = ONE fenced JSON object with three flat blocks —
meta, codes, narrative — matching the CANONICAL v2.11 SCHEMA below. Emit EXACTLY the
schema key set: one integer per *_code field; valence_* are proportions (0-1).
LAYER N/A RULE: for a CORPORATE document, code gov_* = 9, journal_* = 9, and the forum
fields (learner_posture, assessment_object=99, detection_*, surveillance_*,
external_link_boundary, overall_dominant_valence) = 9; 8 = applicable-but-unclear only.
Set meta.coder = "{coder_lower}", meta.prompt_version = "v2.11",
meta.manifest_match_confirmed = "User-confirmed (final)".

READ IN ORDER, then code: (1) ICST layer prompt [context] -> (2) v2.11 SCORING ANCHORS
[AUTHORITY] -> (3) CANONICAL v2.11 SCHEMA [emit this set] -> (4) your watchout -> (5) source.
======================================================================
"""


def section(title, body):
    return f"\n\n======================================================================\n{title}\n======================================================================\n{body}\n"


def main():
    for sid, key in MAP.items():
        meta_raw = json.loads((CR / f"COR_{key}__meta.json").read_text(encoding="utf-8"))
        text = (CR / f"COR_{key}__clean.txt").read_text(encoding="utf-8")
        d = QUEUE / sid
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{sid}__clean.txt").write_text(text, encoding="utf-8")
        meta = {
            "stable_source_id": sid, "document_id": sid,
            "title": meta_raw.get("title", ""), "authoring_body": meta_raw.get("authoring_body", ""),
            "url": meta_raw.get("url", ""), "corpus_batch": "v2.11_test_batch_COR_2026-06-05",
            "layer": "COR", "source_candidate_key": key,
        }
        (d / f"{sid}__metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        for Coder, lower in CODERS.items():
            watch = (CB / "coder_watchouts" / f"WATCHOUT_{Coder}.md").read_text(encoding="utf-8")
            packet = (
                header(sid, lower)
                + section("ICST (INSTITUTIONAL/CORPORATE) LAYER PROMPT (field meanings — context)", cor_prompt)
                + section("v2.11 SCORING ANCHORS (AUTHORITY — HOW to score)", inject)
                + section("CANONICAL v2.11 SCHEMA (emit EXACTLY this key set)", schema_str)
                + section(f"CODER WATCHOUT — {Coder} (calibration; obey it)", watch)
                + section(f"SOURCE TEXT — {sid} — {meta['authoring_body']} — {meta['title'][:60]}", text)
            )
            (d / f"{sid}__READY_TO_PASTE_COR_{Coder}.txt").write_text(packet, encoding="utf-8")
        print(f"{sid}  <- {key:24} | {len(text):>6} chars | {meta['authoring_body'][:20]:20} | {meta['title'][:42]}")


if __name__ == "__main__":
    main()
