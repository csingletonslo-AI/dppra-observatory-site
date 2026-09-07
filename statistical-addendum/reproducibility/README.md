# RUN 07 statistical reproduction

Post-review analysis, 7 September 2026. Python 3.12.14; exact package versions in requirements.txt. No API keys, model calls, or raw corpus text are needed. This package contains the ordinal numerical subset needed for these tests, not the full coded corpus. Source IDs identify documents, not people.

## Reproduce all calculations

In an isolated environment, from this directory:

```sh
python -m pip install -r requirements.txt
python checks.py
python ordinal_checks.py
python verify.py
```

The scripts overwrite calculated outputs in this directory. Keep a fresh download for comparison. Floating point results can vary slightly by platform. Bootstrap seed is 20260907 with 30,000 whole-document samples. The original analysis plan is retained as a historical record; its no-manuscript-edit restriction applied before author review, which is now complete.

ordinal_ratings.csv contains 5,655 document/coder/field slots (65 × 3 × 29), including blank values for missing/inapplicable outcomes. Codes 8 and 9 were converted to missing. common_valid_ratings.csv contains the 5,181 ratings shared across all three coders. The production classification selects 29 ordinal fields and excludes process/confidence and deprecated fields. field_inventory.csv provides exact field names and denominators. Three fields are domain-specific. The original alpha and pooled t-tests use pair-available ratings; all replacement comparisons use three-coder common-valid matching.

source_manifest.json records SHA-256 hashes and relative paths for the 195 frozen source outputs. Those originals were independently checked unchanged at analysis completion; they are not included. The public reproduction begins from exported numerical ratings and cannot itself attest to the original JSON files. data_audit.json preserves original environment/provenance metadata. verification.json is the original verification record; verify.py writes reproduced_verification.json without claiming to re-check unavailable originals.

Model summaries report raw statsmodels inference. The article and ordinal_contrasts.csv use document-adjusted robust covariance multiplied by G/(G−1), t(G−1) reference, and Holm p adjustment within each fit. Their confidence intervals are pointwise. Expanded cumulative threshold rows in ordinal summaries are internal computation, not independent observations. All 12 fits converge. Low-threshold nuisance covariance can be rank-deficient, and printed nuisance standard errors can be NaN; coder contrasts retain full-rank covariance. No full-parameter Wald inference is claimed. Threshold comparisons are diagnostics, not a formal proportional-odds test.

This release covers every test in this reviewer-requested ordinal sensitivity battery. It does not reproduce all historical protocol experiments, nominal-field tests, or qualitative adversarial exercises. Those can be added as separately dated studies.
