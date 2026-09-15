# Adversarial counter-reading (Instrument E) — judgment-level disposition, RUN_07 v2.14

`E_counterreading_disposition_RUN07.csv` lists every three-way agreement attacked in the
June 30, 2026 counter-reading panel: five documents, one per sector (SRC_000002 GOV,
SRC_000008 JRN, SRC_000010 FRM, SRC_000017 INS, SRC_000025 COR). 67 rows.

Columns: `src`, `field`, `consensus_value` (the value all three production coders emitted),
`strongest_counter` (the counter-reading's best text-bound alternative), `verdict`,
`verdict_note` (e.g. "weakly"), `failure_type` (shared_blind_spot, schema_ambiguity, evidence_gap).

Verdicts: CONSENSUS_HOLDS 25 · CONSENSUS_VULNERABLE 40 · CONSENSUS_WRONG 2.

Procedure: the counter-reading was run by the Claude coder seat, held constant, under a mandate
to build the strongest case that each agreed value is wrong, bound to the document text. The
verdicts are that coder's classification; the researcher reviewed each report. No production
code was overridden and no human adjudication was performed. The exercise is advisory and never
enters a reliability coefficient.

Extracted 2026-09-15 from the five per-document reports; the reports' free-text reasoning is not
released here.
