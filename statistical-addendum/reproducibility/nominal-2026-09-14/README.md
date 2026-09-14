# SAMYRAD nominal test sensitivity check

The five published rounded chi-square statistics reproduce from the 195 final RUN 07 JSON files (65 documents, three coders). A within-document coder-label permutation sensitivity check retains all five named findings after Bonferroni correction across the documented 17 fields. No additional field survives correction. The author approved replacing the manuscript’s nominal-test methods and results with this analysis on 14 September 2026.

## What was tested

The 17 fields are taken directly from NOMINAL_EXPLICIT in the existing reliability.py, rather than selected from the observed results. Original comparisons drop codes 8/9 and missing values separately for each coder. Their Pearson statistics and independent-sample chi-square p-values are reconstructed. The paired check uses only documents with three valid ratings for the particular field; Codes 8/9 are missing except assessment_object_code, whose schema defines 88/99 as missing and 8/9 as substantive categories. The historical reconstruction retains the old blanket 8/9 convention solely to reproduce the published statistics. Thus some paired denominators differ from those in the original comparisons. The CSV also gives the independent-sample p-value on the complete-case subset, separating the effect of case selection from permutation calibration.

For each field, the same Pearson category-distribution statistic is calibrated by 199,999 Monte Carlo permutations, independently permuting the three coder labels within each document. Category values remain categorical; no numeric ordering is imposed. Each permutation preserves the document’s three ratings and the overall category totals. Upper-tail p = (exceedances + 1)/(199999 + 1). Seed = 20260914 plus the field’s index in the alphabetically sorted 17-field list. Bonferroni-adjusted p = min(1, 17p).

## Results

Original tests: 5 uncorrected findings; 2 survive Bonferroni. Paired permutation check: 9 uncorrected findings; 5 survive Bonferroni. Consequently, “only five differ before correction” does not describe the paired results. The five corrected findings are exactly responsibility concentration, cost/benefit distribution direction, primary cost bearer, cost/benefit balance, and cost-evidence label.

| Field | Complete documents | Original p | Paired Monte Carlo p | Paired Bonferroni p |
|---|---:|---:|---:|---:|
| assessment_object | 3 | 0.413396 | 1 | 1 |
| cb_balance | 65 | 0.0180394 | 0.000245 | 0.004165 |
| cb_benefit_evidence_label | 65 | 0.0871783 | 0.02449 | 0.41633 |
| cb_cost_evidence_label | 65 | 0.00955189 | 0.000465 | 0.007905 |
| cb_distribution_direction | 65 | 1.73157e-05 | 5e-06 | 8.5e-05 |
| cb_primary_cost_bearer | 62 | 0.0106497 | 1e-05 | 0.00017 |
| cb_primary_material_beneficiary | 65 | 0.37929 | 0.047555 | 0.808435 |
| cb_primary_value_capturer | 61 | 0.397288 | 0.067485 | 1 |
| dominant_value_type | 65 | 0.978561 | 0.55811 | 1 |
| external_link_boundary | 12 | 0.152486 | 0.016315 | 0.277355 |
| journal_level_of_analysis | 14 | 0.301188 | 0.111885 | 1 |
| journal_method_evidence_label | 14 | 0.0683332 | 0.024835 | 0.422195 |
| journal_method_type | 14 | 0.961083 | 1 | 1 |
| journal_source_type | 14 | 0.489551 | 0.222515 | 1 |
| learner_posture | 3 | 0.922001 | 1 | 1 |
| overall_dominant_valence | 12 | 0.35443 | 0.057735 | 0.981495 |
| responsibility_concentration | 65 | 1.75802e-06 | 5e-06 | 8.5e-05 |

## Interpretation and limits

This is a paired sensitivity analysis under within-document coder-label exchangeability: under the null, permuting coder assignments within a document does not change the joint distribution. That is stronger than equal marginal category proportions alone. Coders were not randomly assigned labels, so this is a model-based exchangeability assumption, not a randomized-experiment guarantee. The result supports robustness of the five-field pattern under this check; it is not an assumption-free replacement for a general marginal-homogeneity test. See the paired sample-permutation definition in [SciPy’s documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html).

Documents are treated as independent units; the check does not correct for dependencies between different documents. Complete-case selection conditions the findings on jointly valid ratings and does not test coder differences in missingness/applicability. Learner posture and assessment object each have only three complete documents, so its nonsignificance is particularly uninformative. Other sector-specific fields have 12–14 complete documents. Nonsignificance does not establish equivalence or case-level agreement.

Monte Carlo p-values are estimates. The smallest possible reported value is 0.000005; responsibility concentration and distribution direction had zero exceedances, so that number is the plus-one simulation floor, not an exact tail probability. Primary cost bearer had one exceedance. The corrected decisions are well separated from 0.05 at this simulation size.

Sparse expected counts are recorded in the CSV. Permutation calibration avoids using the asymptotic chi-square reference distribution for the paired check, but does not remove exchangeability or missingness assumptions. No new coder judgments were generated; alpha, ANOVA, ordinal analyses, and the manuscript were not altered.

## Reproduce this release

Install Python and run `python -m pip install -r requirements.txt`, then `python nominal_checks.py`. All files must be in the same directory. The script reads nominal_inputs.csv and writes generated/; it compares all 17 results with nominal_results.json and fails if any differ. The original chi-square values are also checked against the manuscript’s rounding. This is a retrospective sensitivity check, not a preregistered analysis.

The public input contains only document IDs, sectors and the 17 categorical ratings for each coder, including missing markers. No corpus text or narrative coding is included. nominal_results.json provides source hashes with run-relative paths, category counts, simulation seeds and complete-case denominators. Public re-execution verifies the numerical export; it cannot independently authenticate the unpublished source JSON files. SHA256SUMS.json records the released files. The original ordinal and instrument archives remain separate, unchanged releases.

Validation: all 195 raw coding records were read; the five published rounded Pearson statistics reproduced. All 36 permutations of a two-document toy example preserved within-document category values and matched directly computed statistics. Before publication, the portable CSV-based script reproduced all 17 reference results exactly.
