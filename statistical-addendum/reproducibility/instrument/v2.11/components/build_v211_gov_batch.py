#!/usr/bin/env python3
r"""Build the v2.11 GOV test batch (SRC_000052-056) intake + ready-to-paste coder packets.

Group 3 of the v2.11 shakedown (governmental/legal/regulatory). Maps 5 government/legal AI
instruments to SRC ids and assembles a READY_TO_PASTE packet per coder = SOURCE GATE +
GOV layer prompt + v2.11 SCORING ANCHORS + v2.11 SCHEMA + coder watchout + SOURCE TEXT.
NOTE: for GOV the gov_* fields ARE coded substantively; journal_* and forum fields = 9.
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\C_Sin\Full Dataset Project")
GR = ROOT / "01_Intake" / "gov_raw" / "06_clean_text"
CB = ROOT / "03_DPPRA_Prompts_and_Codebooks" / "07_codebooks"
QUEUE = ROOT / "20_Coding_Pipeline" / "00_ROUTING" / "00_intake_queue" / "GOV"

MAP = {
    "SRC_000052": "blueprint_ai_bor",
    "SRC_000053": "coe_framework_ai",
    "SRC_000054": "china_genai_measures",
    "SRC_000055": "uk_proinnovation",
    "SRC_000056": "us_eo_14110",
}
CODERS = {"Claude": "claude", "Codex": "codex", "Gemini": "gemini"}

gov_prompt = (ROOT / "03_DPPRA_Prompts_and_Codebooks" / "01_current_prompts" /
              "ACTIVE_GOV_PROMPT_v2.6.txt").read_text(encoding="utf-8", errors="ignore")
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
DPPRA v2.11 CODING TASK — GOVERNMENTAL / LEGAL / REGULATORY (GOV) LAYER — {sid}
======================================================================
You are coding ONE government/legal/regulatory AI instrument (statute, regulation,
executive order, treaty, or official framework) for an inter-coder reliability study.
OUTPUT CONTRACT: your entire reply = ONE fenced JSON object with three flat blocks —
meta, codes, narrative — matching the CANONICAL v2.11 SCHEMA below. Emit EXACTLY the
schema key set: one integer per *_code field; valence_* are proportions (0-1).
LAYER N/A RULE: for a GOV document the gov_* fields ARE coded substantively
(binding status, enforcement density, FRIA, carve-outs, standards displacement,
remedy, sanction, compliance mechanism). Code journal_* = 9 and the forum fields
(learner_posture, assessment_object=99, detection_*, surveillance_*,
external_link_boundary, overall_dominant_valence) = 9; 8 = applicable-but-unclear only.
Set meta.coder = "{coder_lower}", meta.prompt_version = "v2.11",
meta.manifest_match_confirmed = "User-confirmed (final)".

READ IN ORDER, then code: (1) GOV layer prompt [context] -> (2) v2.11 SCORING ANCHORS
[AUTHORITY] -> (3) CANONICAL v2.11 SCHEMA [emit this set] -> (4) your watchout -> (5) source.
======================================================================
"""


def section(title, body):
    return f"\n\n======================================================================\n{title}\n======================================================================\n{body}\n"


def main():
    for sid, key in MAP.items():
        meta_raw = json.loads((GR / f"GOV_{key}__meta.json").read_text(encoding="utf-8"))
        text = (GR / f"GOV_{key}__clean.txt").read_text(encoding="utf-8")
        d = QUEUE / sid
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{sid}__clean.txt").write_text(text, encoding="utf-8")
        meta = {
            "stable_source_id": sid, "document_id": sid,
            "title": meta_raw.get("title", ""), "authoring_body": meta_raw.get("authoring_body", ""),
            "url": meta_raw.get("url", ""), "corpus_batch": "v2.11_test_batch_GOV_2026-06-05",
            "layer": "GOV", "source_candidate_key": key,
        }
        (d / f"{sid}__metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        for Coder, lower in CODERS.items():
            watch = (CB / "coder_watchouts" / f"WATCHOUT_{Coder}.md").read_text(encoding="utf-8")
            packet = (
                header(sid, lower)
                + section("GOV LAYER PROMPT (field meanings — context)", gov_prompt)
                + section("v2.11 SCORING ANCHORS (AUTHORITY — HOW to score)", inject)
                + section("CANONICAL v2.11 SCHEMA (emit EXACTLY this key set)", schema_str)
                + section(f"CODER WATCHOUT — {Coder} (calibration; obey it)", watch)
                + section(f"SOURCE TEXT — {sid} — {meta['title'][:80]}", text)
            )
            (d / f"{sid}__READY_TO_PASTE_GOV_{Coder}.txt").write_text(packet, encoding="utf-8")
        print(f"{sid}  <- {key:22} | {len(text):>7} chars | {meta['authoring_body'][:28]:28} | {meta['title'][:40]}")


if __name__ == "__main__":
    main()
