# Instrument, development and interpretation clarifications

Release: **15 September 2026**. Companion to *Coders as Standpoint Instruments: Reading Cross-Family LLM Disagreement as Diagnostic in AI-Ethics Content Analysis*.

This release adds documentation to the [statistical addendum](../../index.html#instrument-scope). It records the complete schema inventory, the two statistical battery memberships, the public corpus manifest, and ordinal missingness. The addendum also supplies a development ledger, precise labels for the selected eight-document alignment result, a comparison of the different disagreement diagnostics, and a practical interpretation of the triage proposal.

No production output, historical prompt, statistical result, or earlier release archive is changed. The 7, 11 and 14 September releases retain their separate dates and scopes.

## Files

| File | Contents |
| --- | --- |
| `field_crosswalk.csv` | 107 rows: 91 coded fields and 16 narrative fields. Archived schema declarations; descriptive family groups; membership and complete-document denominators for the 29 ordinal and 17 paired nominal test fields. |
| `corpus_manifest.csv` | 65 public source IDs, sectors, titles, authors and years, copied from `observatory_site_data.json` and reconciled to the ordinal export. No source-document text. |
| `ordinal_missingness.csv` | 87 field/coder rows. Counts of slots, valid ratings and blanks, with out-of-domain and within-domain blanks distinguished. The exceptional within-domain source is identified. |
| `scope_audit.json` | Aggregate counts, sector counts, nominal complete-case denominators and SHA-256/Git blob hashes for the six unchanged public inputs. |
| `scope_audit.py` | Standard-library Python program that checks exact input bytes, regenerates the four inventory files and compares them byte-for-byte with the released references. |

## Reproduce

Use Python 3.9 or later from a checkout of this repository. No third-party Python packages are required. From the repository root:

```sh
python3 statistical-addendum/reproducibility/clarifications-2026-09-15/scope_audit.py
```

The program creates a local `generated/` directory in this release folder. It exits with an error if an input differs from its recorded Git blob hash, an inventory fails an internal reconciliation, or a regenerated file differs from the released reference. Do not commit the generated copies.

For creation of a new reference set only, `--out-dir` can be set to the release directory. Normal reproduction should use the default, which compares against the existing reference files.

The exact source snapshot is [commit f23bfa2ad63ee4700852e8fc6f31edc3cac83051](https://github.com/csingletonslo-AI/dppra-observatory-site/commit/f23bfa2ad63ee4700852e8fc6f31edc3cac83051). The program pins these six files:

- `instrument/v2.14/GOV__Claude.txt`, relative to the parent reproducibility directory.
- `ordinal_ratings.csv`.
- `field_inventory.csv`.
- `nominal-2026-09-14/nominal_inputs.csv`.
- `nominal-2026-09-14/nominal_results.json`.
- `observatory_site_data.json`, at the repository root.

Their Git blob hashes are embedded in the script; their SHA-256 values are in `scope_audit.json`. If a later live-data update changes an input, reproduce from the dated repository revision rather than weakening the source check. This release is an inventory audit, not a new alpha, permutation or GEE analysis.

## Counting and interpretation rules

The canonical schema is extracted from the archived v2.14 government/Claude packet. Keys beginning with `_` in `codes` are instruction helpers and are excluded; this removes `_principle_intensity_range`, leaving 91 coded fields. The 16 narrative fields are inventoried separately. Family group labels organize the schema for reading; they do not reconstruct the production measurement-type classifier.

Schema declarations are copied verbatim, including historical version labels. Part J of the v2.14 packet explicitly supersedes Part A for the families it revises. The CSV is therefore an index into the instrument, not a replacement for the operative instructions. A `no` battery flag means outside that particular test set; it does not mean an unused field or establish exclusion from every production reliability calculation. Process/confidence and valence-proportion fields remain visible in the full schema inventory.

Ordinal membership and common-case denominators come from the existing `field_inventory.csv` and are independently reconciled to the 5,655 exported slots. The two forum-only strength fields each have 159 out-of-domain blanks; journal evidence quality has 153. Together these account for 471 of 472 blanks. The one within-domain blank is Claude's alignment rating. The export does not preserve every original missing-value reason. There are 5,183 available ratings before common matching; dropping the incomplete triple also excludes the other two available ratings for that unit, leaving 1,727 complete units and 5,181 ratings. No imputation is performed.

Nominal membership comes from the released 17-field input. Complete-case counts use the paired release's field-specific rule: assessment object excludes 88/99 while preserving valid 8/9 categories; other fields exclude 8/9. Counts are checked against all 17 entries in `nominal_results.json`. The statistical procedure and its limits remain documented in the [14 September README](../nominal-2026-09-14/README.md).

## Historical and qualitative sources

The development coefficients, selected eight-document alignment trajectory and June probe descriptions are transcribed or summarized from the companion manuscript reviewed for this update. They are labeled as historical reported findings in the addendum, not newly reproduced from public numerical data. The run/version mapping is cross-referenced to the [instrument README](../instrument/README.md) and [configuration record](../provenance_configuration.json).

The concrete earlier counter-reading examples come from `adversarial_layer.passes` in the public Observatory data, specifically RUN 03 dated 5 June 2026. These are historical audit summaries and recorded recommendations. They do not supply source passages or substitute for the June panel's 67-judgment disposition log. The new operational triage procedure is an explanation of how to use the proposed framework; it is not represented as a previously collected adjudication protocol.

## Remaining reproduction boundaries

The 17-field paired nominal battery is not a reproduction of pooled nominal alpha 0.706 or binary alpha 0.567. Full production measurement-type classification, pooling and missing-code implementation, with suitable numerical inputs, are needed to audit those coefficients. The public field crosswalk must not be used to invent that classifier, and a coefficient recomputed from a different subset is not a replacement production estimate.

The June qualitative record does not publicly supply the judgment-level outcomes, an explicit rule and classifier for the 25 judgments described as holding, or the disposition of the remaining 42. It also does not supply the exact lens/challenge instruction blocks or full sequential conversation histories. The remaining judgments are not automatically verified errors. These records can be added in a subsequent supplement if available; their contents are not reconstructed here.

Listed hashes for the 195 original coding JSON files remain evidence of the recorded provenance, not public access to those originals. Reproduction from numerical exports should be distinguished from authentication against unpublished coding records and full source texts.
