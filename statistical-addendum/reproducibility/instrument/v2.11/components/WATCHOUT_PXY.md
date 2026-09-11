# Coder Calibration Watchout — PXY (v2.11)

Neutral calibration guidance for this coder. Apply where text-grounded; it does not override the source or the schema.

## Mirror calibration — YOUR POLE: MIXED (under-commit on strength, over-commit on the CAP)

The Run-2 data shows two opposite tendencies in you:

1. **Under-conservatism on DPPRA strength for self-authored sources** — you cap material that is actually operationalized. (Your standing watchout; kept below.)
2. **Over-use of the 5 / CAP** — you assigned FOUR co-equal spine-5s on some documents (e.g. SRC_000020, SRC_000031). The CAP rule allows at most ONE dimension at 5 unless two are *genuinely co-equal on section share*. Four 5s is almost never defensible.

Medication: apply the v2.11 PROPORTION GATE to every candidate 5 (leading theme in a plurality of major sections + removal test). If two dimensions tie on section share, you may name two co-equal 5s in `cap_rule_notes` — but never three or four.

## eth_integrity (v2.11 — REDEFINED)

Integrity is **principled consistency + follow-through** — alignment of professed values with actual/required conduct (epistemic honesty AND follow-through). int_* and decoupling are evidence streams feeding/undercutting the headline. A doc that merely STATES values = low (1-2); a doc that BINDS values to conduct or EXPOSES the say-do breach = high. Keep it text-grounded; do not auto-cap eth_integrity just because the source is self-authored.

## DPPRA cap / override (your standing main watchout)

Do not reduce a score solely because the source is self-authored. For self-authored corporate/nonprofit/institutional sources, do not automatically cap DPPRA at 2-3. A self-authored source may reach DPPRA strength 4 with strong evidence: named governance offices, formal review workflows, testing/benchmarking/red-teaming, audit trails, enforcement signals, deployed infrastructure, training pathways, stakeholder-facing mechanisms, external/expert/third-party evaluation. Remain at 2-3 for aspirational principles, voluntary frameworks, case studies without adoption evidence, self-reported impact, soft-governance without enforcement. Reserve 5 for independent verification, audit evidence, measured outcomes, or externally validated implementation.

## Justice vs. Equity

Keep Justice conservative but do not under-code it when a source goes beyond general equity language. Equity = access/inclusion/bias-mitigation/accessibility/digital-divide. Justice rises above 2 for rights, due process, contestability, appeal, remedy, redress, anti-discrimination enforcement, structural inequality, burden/benefit distribution, labor justice, democratic harms, legal protections.

## Assessment Integrity

Keep it narrow. Not for general model testing/benchmarking/red-teaming/TEVV (that is System/TEVV). Truthfulness/hallucinations/citations = Epistemic; source grounding/data lineage = Data/Provenance.

## OUTPUT HYGIENE — HARD REQUIREMENTS (these are your recurring filing failures)

These are not style preferences; outputs that violate them get rejected by the compiler and have to be re-run.

1. **PRESERVE UNDERSCORES in every key.** Emit `eth_equity_code`, NOT `ethequitycode`. Do not strip, camelCase, or collapse separators. Every key must match the canonical schema string exactly.
2. **EMIT EVERY KEY in the injected v2.11 schema** — including N/A fields. Cross-layer fields that don't apply get `9` (or `99` for `assessment_object_code`); do not silently omit them.
3. **Use the v2.11 schema ONLY.** Do not fall back to an older key set (no `cb_cost_labor_time_code`, `cb_benefit_integrity_detection_code`, `cb_cost_legitimacy_trust_code`, etc. — those were cut). Do not emit the dropped `*_presence` binaries (Part F); emit the `*_strength` fields.
4. **Valid JSON.** Escape any double-quote inside a string value (`\"`). Do not put raw unescaped quotes inside array-of-string elements (e.g. evidence excerpts) — that breaks the whole record.
5. **Do NOT return a metadata-only exclusion** when a full source text is attached. If the document is present, code it; reserve exclusion for genuinely empty/unreadable input.
6. Emit flat `meta` / `codes` / `narrative` blocks, one integer per `*_code` field, `meta.coder = "perplexity"`, `meta.prompt_version = "v2.11"`.

## Manifest confirmation — NO HALT (hard rule; this is your single biggest failure mode)

Every source handed to you has ALREADY passed the project's confirmation process BEFORE it reaches you. **User delivery = manifest confirmed.** You do not re-verify source identity and you NEVER halt on manifest grounds.

- Always set `manifest_match_confirmed = "User-confirmed (final)"`.
- **NEVER** emit `SOURCE MISMATCH`, `CODING PAUSED`, `Mismatch / uncertain`, `attached-file confirmed but no external manifest`, or any status/preamble that withholds or defers coding. There is no "stop and ask" branch — it has been removed.
- A missing date/version, ISSN, or any single absent metadata field is NOT a stop condition. Code the document, leave that one field blank or `8`, and note it in `narrative.methodological_caution`.
- "Attached-file confirmed" is NOT a lesser status that lets you pause — for this workflow it IS full confirmation. Do not treat the absence of a separate external manifest as a reason to halt; the user's delivery is the manifest.
- If you genuinely feel uncertain about identity, you STILL code, and record the uncertainty in `narrative.methodological_caution`. Coding is mandatory; pausing is not an option the workflow offers you.

Why this rule exists: in the v2.11 batch you halted on SRC_000042 with "SOURCE MISMATCH — CODING PAUSED" while Claude and Codex coded it without issue. The article was never the problem — you stalled in the verification branch before reaching the coding task. That branch is now closed.

## Compiler extraction

Use clean field labels; every required quantitative field must be easy for the compiler to locate. Narrative explanation is fine, but never at the cost of the points above.
