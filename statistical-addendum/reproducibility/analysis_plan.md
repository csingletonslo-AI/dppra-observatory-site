# Reviewer-requested sensitivity checks

Scope: frozen RUN_07_v2.14_FULL only. No recoding, no source edits, no manuscript edits before discussion.

1. Inventory and hash all 195 source files; validate 65 complete triples and protocol versions. Use the production reliability.py field classification and exclusions. Codes 8/9 are missing for the selected 0–5 fields.
2. Reproduce published document-level repeated-measures ANOVA and pooled paired tests before running replacements. Reproduce ordinal alpha. Report any discrepancy before interpreting sensitivity results.
3. For each document retain only fields valid for all three coders. Compare coder means across 65 paired documents, with 95% t confidence intervals and Holm adjustment across three pairwise tests. Check the ten ethical-principle fields separately; treat this as a sensitivity analysis, not a newly selected primary outcome.
4. Rank-only check: within each matched document-field pair compute sign(A−B), then average within each document. Bootstrap whole documents for confidence intervals. Report higher/tied/lower document counts and exact sign tests with Holm adjustment. This tests directional predominance without assigning category distances. Interpret across this fixed field set, not as generalization to a random population of fields.
5. Fit a cumulative-logit ordinal GEE to common-valid ratings, with coder indicators, fixed field effects, document clusters, working independence and robust covariance. This is a marginal clustered ordinal model, not a mixed-effects model. It addresses repeated ratings while allowing ordered categories without equal spacing. Use document-cluster degrees of freedom and a finite-cluster covariance adjustment for contrasts. Check convergence, covariance rank, and sensitivity to threshold-specific binary GEE fits (proportional-odds assumption). Also fit the ten-principle subset and leave-one-sector-out models to assess pooling sensitivity.
6. Report model assumptions and limits: 65 documents, fixed instrument fields, selected corpus, heterogeneous constructs, possible proportional-odds departures, and unisolated model/interface effects. Do not claim the original 76% total-variance or causal interpretation is validated.

Software documentation: https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_estimating_equations.OrdinalGEE.html

This is a post-review sensitivity plan, not a preregistration. No results are assumed in advance.
