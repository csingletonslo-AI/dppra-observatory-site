# DPPRA/ICST coding instrument — the protocol ladder, v2.11 to v2.14

Published 11 September 2026 as part of the SAMYRAD statistical addendum, in answer to the reviewers' request for the complete coding instrument and coder prompts. These are the exact instruction blocks that preceded the source document in every coder packet of the four version-locked runs reported in Table I of the paper. **No corpus text is included**: each file stops where the packet turned to the document.

## What a packet is

A packet is one text file pasted (or piped) to one coder for one document. It is assembled in layers, and the layer labels inside the text carry the version at which each layer was last changed — that is why a v2.14 packet still opens with the "v2.10 operational profile". Reading order in the packet:

1. **Operational profile** — output contract (one fenced JSON object; flat `meta` / `codes` / `narrative`), key-name lock, no-preamble rules.
2. **Layer prompt** — the sector-specific field definitions (GOV, JRN, FRM, INS/COR). INS and COR share one prompt, so their blocks are byte-identical; the other sectors differ substantially. Collapsing the layer prompts into one instrument was planned for v2.15 and is not part of the reported runs.
3. **Scoring anchors inject** — the authority on *how* to score: the 0–5 intensity ladder, presence gates, and from v2.14 the evidence-grade families (Part J: stated goal ceilings at 2, verifiable action floors at 3).
4. **Canonical schema** — the exact key set to emit.
5. **Coder watch-out** — the per-coder block. This is where the natural experiment lives: v2.12 carried different heating/cooling addenda per coder; v2.13 and v2.14 replaced them with one shared evidence-first discipline, identical for all three coders except the `meta.coder` line.
6. *Source document* — omitted here.

## Files

`{version}/{SECTOR}__{Coder}.txt`, one per sector per coder per version. Each file opens with a provenance header: run, number of packets the block was verified byte-identical in, SHA-256 of the block, and the local path pattern of the packets it was cut from. `instrument_manifest.json` lists every file with the same fields.

| version | run | coders | notes |
|---|---|---|---|
| v2.14 | RUN_07 (65 docs, 30 June 2026) | Claude, Codex, Gemini | the paper's reported run. Codex packet text is identical to Claude's; coder identity was set by the Codex run sheet. |
| v2.13 | RUN_06 (55 docs) + RUN_05 test-10 | Claude, Codex, Gemini | per-coder calibration retired. Gemini blocks come from the Drive layer prompts used in the consumer app. |
| v2.12 | RUN_04 (65 docs, 24–27 June) | Claude, Codex, Gemini | the conformity intervention: per-coder watch-outs (cooling for the hot coder, warming for the cold, none for the newly seated third). |
| v2.12_ablation_no_codex_watchout | RUN_04 ablation | Codex | the cooling addendum retracted; Table I row "v2.12 − watchout". |
| v2.11 | RUN_03 | PXY (surviving packets) + components | see below. |

## v2.11 — what survives and what is reconstructable

The v2.11 packets for Claude, Codex and Gemini were overwritten in the working queue by later versions; they were not archived as a run-versioned batch. What survives as files is ten packets built for the Perplexity seat on 4 June 2026, the day Perplexity was retired and Gemini seated (INS ×5, JRN ×5). Their instrument blocks are published as the artifact record of v2.11, with the per-document id normalised to `SRC_XXXXXX`. Two JRN variants are genuine: three of the five carry a "PXY hard override" header, the workaround added after Perplexity repeatedly halted at the source-manifest gate.

`v2.11/components/` holds the parts every v2.11 packet was built from — the v2.11 scoring-anchors inject, the v2.11 schema template, the per-coder watch-out files, and the five `build_v211_*_batch.py` scripts that assembled them with the layer prompts. A v2.11 packet for any coder and sector can be regenerated from these; the regenerated text is a reconstruction, not a hashed artifact, and is labelled as such.

## What is not here

Corpus text; the sector layer prompts as standalone files (they are embedded in every block above); the coding outputs (their SHA-256 hashes are in `source_manifest.json`); and any claim about model-side system prompts or sampling parameters, which were not settable through the interfaces used (see the configuration section of the addendum).
