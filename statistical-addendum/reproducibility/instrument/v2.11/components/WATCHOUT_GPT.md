# Coder Calibration Watchout — GPT

Neutral calibration guidance for this coder. Apply where text-grounded; it does not override the source or the schema.

## Main watchout

GPT is generally schema-aligned and compiler-ready. The main risk is threshold calibration: deciding when a score should be 3, 4, or 5, especially for DPPRA, Justice, Privacy, Integrity, and Non-Maleficence.

## DPPRA 3 vs. 4

Do not assign DPPRA 4 merely because a source is detailed, polished, institutional, or well-written.

DPPRA 4 requires visible operational alignment across most of:

- Discourse
- Policy
- Practice
- Resources
- Accountability

DPPRA 4 is appropriate when several of the following are visible:

- Named governance bodies or responsible teams
- Formal review workflows
- Testing, benchmarking, red teaming, audit trails, or TEVV
- Enforcement signals such as launch blocking, severity scoring, SLAs, sanctions, or policy consequences
- Deployed infrastructure or operational systems
- Training pathways or funded programs
- Stakeholder-facing implementation mechanisms
- External testing, expert review, bug bounty, or third-party evaluation signals

Keep the score at 3 when procedures are strong but resources, enforcement, implementation breadth, or accountability are weak.

Do not assign 5 unless there is independent verification, audit evidence, measured outcomes, or externally validated implementation effects.

## Corporate / platform-builder cap override

For self-authored corporate reports, apply the cap rule carefully.

A self-authored corporate source is normally capped at 3 unless there is enough material implementation evidence to justify an override.

A platform-builder source may receive DPPRA 4 only when the report documents real operational systems, not just principles.

When overriding the corporate cap, explicitly label the decision as a cap override and explain why the source exceeds the usual self-authored-report limit.

## Justice vs. Equity

Do not inflate Justice because the source discusses equity, inclusion, access, accessibility, diversity, or bias mitigation.

Use Equity for access, inclusion, bias mitigation, accessibility, digital divide, equal opportunity, and diverse participation.

Justice may rise above 2 only when the source includes stronger markers such as rights, due process, contestability, appeal, remedy, redress, anti-discrimination enforcement, structural inequality, distribution of burdens and benefits, labor justice, democratic harms, or legal protections.

## Privacy 4 vs. 5

Privacy 5 is reserved for cases where privacy is a dominant organizing logic of the document or system.

Privacy 4 is usually appropriate when privacy is strongly operationalized through data masking, zero retention, access controls, PII/PHI safeguards, privacy-by-design, vendor/data handling rules, or data security requirements.

## Integrity and Non-Maleficence 4 vs. 5

Integrity and Non-Maleficence reach 5 only when they are organizing themes, not merely strong recurring themes.

Integrity 5 is appropriate when the document is organized around testing, verification, auditability, provenance, output reliability, hallucination control, benchmarking, epistemic trust, data assurance, or system assurance.

Non-Maleficence 5 is appropriate when harm prevention structures the source through safety architecture, guardrails, red teaming, misuse prevention, incident response, bias/toxicity controls, security review, launch blocking, or enforcement pathways.

## Assessment Integrity

Do not code general model testing, benchmarking, red teaming, or TEVV as Assessment Integrity.

Model testing belongs under System Integrity / TEVV. Truthfulness and hallucinations belong under Epistemic Integrity. Source grounding and data lineage belong under Data / Provenance Integrity.

