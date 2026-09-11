#!/usr/bin/env python3
r"""Build the v2.11 FRM test batch (SRC_000057-061) intake + ready-to-paste coder packets.

Group 4 (forum / discussion). Maps 5 Reddit threads to SRC ids and assembles a
READY_TO_PASTE packet per coder = SOURCE GATE + FRM layer prompt + v2.11 SCORING ANCHORS
+ v2.11 SCHEMA + coder watchout + SOURCE TEXT.
NOTE: for FRM the forum domain fields ARE coded substantively; gov_* and journal_* = 9.
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\C_Sin\Full Dataset Project")
FR = ROOT / "01_Intake" / "forum_raw"
CB = ROOT / "03_DPPRA_Prompts_and_Codebooks" / "07_codebooks"
QUEUE = ROOT / "20_Coding_Pipeline" / "00_ROUTING" / "00_intake_queue" / "FRM"

MAP = {
    "SRC_000057": "FRM_1too065",
    "SRC_000058": "FRM_1toqm76",
    "SRC_000059": "FRM_1tumimt",
    "SRC_000060": "FRM_1tp0zfh",
    "SRC_000061": "FRM_1qax221",
}
CODERS = {"Claude": "claude", "Codex": "codex", "Gemini": "gemini"}

frm_prompt = (ROOT / "03_DPPRA_Prompts_and_Codebooks" / "02_forum_prompts" /
              "Revised_Forum_DPPRA_Coding_Prompt_v2_6_Phase_1_Cleanup.txt").read_text(encoding="utf-8", errors="ignore")
inject = (CB / "DPPRA_v2.11_SCORING_ANCHORS_INJECT.txt").read_text(encoding="utf-8")
schema_obj = json.loads((CB / "DPPRA_v2.11_SCHEMA_template_ALL_CODERS.json").read_text(encoding="utf-8-sig"))
schema_str = json.dumps(schema_obj, indent=2, ensure_ascii=False)


def thread_meta(fid):
    rj = FR / "02_raw_threads" / f"{fid}.json"
    title = sub = author = ""
    if rj.is_file():
        try:
            j = json.loads(rj.read_text(encoding="utf-8"))
            post = j.get("post", {}) if isinstance(j.get("post"), dict) else j
            title = j.get("title") or post.get("title") or ""
            sub = j.get("subreddit") or post.get("subreddit") or ""
            author = j.get("author") or post.get("author") or ""
        except Exception:
            pass
    return title, sub, author


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
DPPRA v2.11 CODING TASK — FORUM / DISCUSSION (FRM) LAYER — {sid}
======================================================================
You are coding ONE online forum thread (a Reddit post + its discussion) for an
inter-coder reliability study. Code the discourse of the thread as a whole.
OUTPUT CONTRACT: your entire reply = ONE fenced JSON object with three flat blocks —
meta, codes, narrative — matching the CANONICAL v2.11 SCHEMA below. Emit EXACTLY the
schema key set: one integer per *_code field; valence_* are proportions (0-1).
LAYER N/A RULE: for a FORUM document the forum domain fields ARE coded substantively
(learner_posture_code, assessment_object_code [uses 88=unclear / 99=N/A], external_link_
boundary_code, detection_verification_presence_binary+strength, surveillance_monitoring_
presence_binary+strength, overall_dominant_valence_code). Code gov_* = 9 and journal_* = 9;
8 = applicable-but-unclear only. Set meta.coder = "{coder_lower}",
meta.prompt_version = "v2.11", meta.manifest_match_confirmed = "User-confirmed (final)".

READ IN ORDER, then code: (1) FRM layer prompt [context] -> (2) v2.11 SCORING ANCHORS
[AUTHORITY] -> (3) CANONICAL v2.11 SCHEMA [emit this set] -> (4) your watchout -> (5) source.
======================================================================
"""


def section(title, body):
    return f"\n\n======================================================================\n{title}\n======================================================================\n{body}\n"


def main():
    for sid, fid in MAP.items():
        text = (FR / "06_clean_text" / f"{fid}__clean.txt").read_text(encoding="utf-8")
        title, sub, author = thread_meta(fid)
        d = QUEUE / sid
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{sid}__clean.txt").write_text(text, encoding="utf-8")
        meta = {
            "stable_source_id": sid, "document_id": sid,
            "title": title, "authoring_body": f"r/{sub} (u/{author})" if sub else "Reddit",
            "subreddit": sub, "corpus_batch": "v2.11_test_batch_FRM_2026-06-05",
            "layer": "FRM", "source_candidate_key": fid,
        }
        (d / f"{sid}__metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        for Coder, lower in CODERS.items():
            watch = (CB / "coder_watchouts" / f"WATCHOUT_{Coder}.md").read_text(encoding="utf-8")
            packet = (
                header(sid, lower)
                + section("FRM LAYER PROMPT (field meanings — context)", frm_prompt)
                + section("v2.11 SCORING ANCHORS (AUTHORITY — HOW to score)", inject)
                + section("CANONICAL v2.11 SCHEMA (emit EXACTLY this key set)", schema_str)
                + section(f"CODER WATCHOUT — {Coder} (calibration; obey it)", watch)
                + section(f"SOURCE TEXT — {sid} — r/{sub} — {title[:70]}", text)
            )
            (d / f"{sid}__READY_TO_PASTE_FRM_{Coder}.txt").write_text(packet, encoding="utf-8")
        print(f"{sid}  <- {fid:14} | {len(text):>6} chars | r/{sub[:16]:16} | {title[:46]}")


if __name__ == "__main__":
    main()
