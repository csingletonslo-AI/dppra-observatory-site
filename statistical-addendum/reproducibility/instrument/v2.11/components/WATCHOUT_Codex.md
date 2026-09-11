# Coder Watch-out — Codex (v2.13)

Neutral, shared guidance. It does not override the source or the schema. v2.13 uses
ONE discipline for all three coders — there is no per-coder "temperature."

## v2.13 — per-coder calibration RETIRED (reliability through clarity, not conformity)

The v2.12 hot/cold "pole" framing and the heating/cooling addenda are GONE. RUN_04
proved they did not calibrate — they pushed coders to recite the instructions instead
of read the document (identical generic narratives across all 65 docs, flat ethical
rows, all-1 cost rows). v2.13 replaces per-coder nudging with the EVIDENCE-FIRST rule
that governs everyone equally (inject PART I). There is no pole to correct toward and
no target agreement to reach for — read each document on its own terms and earn every
score from a passage you can point to. Where coders still diverge on a STANDPOINT field
(the actor crosswalk, `decoupling_signal`), that divergence is DATA — do not normalize
it away to match the other coders or the document's self-framing.

## The shared discipline (it all lives in the inject — this is the spine)

- **Earn each value from field-specific evidence, not the document's tone** (PART I0):
  locate the passage that bears on the field, classify its strength (0 none · 1 incidental ·
  2 named-no-mechanism · 3 concrete-local · 4 recurring-most-sections · 5 spine), score
  from that. For your 5(s) and any cost/benefit you fire, name the locating passage in
  the narrative. Repeated values are fine — a true all-4 document is fine — but each must
  be earned field-specifically, never asserted from the topic ("this is about responsible AI").
- **Cost/benefit trigger test** (PART I1): code a `cb_*` indicator 1 ONLY if THIS specific
  cost/benefit is named or clearly implied; 0 if the document is merely about AI risk/benefit
  in general. A passing or diffuse mention is not presence.
- `eth_beneficence_mech` (operational good the system does) and `eth_beneficence_eth`
  (appeal to dignity/wellbeing as a value) are INDEPENDENT — score each on its own evidence
  (PART I2). `int_*` and `surveillance_monitoring` fire on a described operational MECHANISM,
  not metaphor (PART C). Categorical fields name a TYPE, not a magnitude (PART H). Score the
  document's OWN mechanism, not the mechanisms it analyzes (PART I4).
- `eth_integrity` = principled consistency + follow-through; saying-one-thing/doing-another
  is the inverse (PART B). Equity = access/inclusion; justice = rights/remedy/distribution
  (PART B2). Integrity sub-dimensions are the canonical six; cheating/plagiarism =
  `int_academic`, general model testing = `int_system_tevv` (PART C).

## Operational compliance

- Use the official schema key set exactly — flat `meta` / `codes` / `narrative` blocks,
  no grouped sub-objects, no invented fields, exactly one integer per `*_code` field.
  EMIT EVERY key including N/A fields (9, or 99 for `assessment_object_code`); never silently
  omit a key. Emit the `*_strength` fields; the `*_presence` binaries are dropped.
- Set `meta.coder = "codex"`, `meta.prompt_version = "v2.13"`. valence_* are 0–1 proportions.
- The user's delivery of the source IS the manifest confirmation. Set
  `manifest_match_confirmed = "User-confirmed (final)"` and code directly. Never halt, pause,
  or emit a mismatch/uncertain status; a missing single metadata field is not a stop condition
  (leave it blank or 8 and note it in `methodological_caution`).
