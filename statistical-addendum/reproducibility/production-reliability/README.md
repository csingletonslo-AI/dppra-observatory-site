# Production reliability script and report (RUN_07, v2.14)

`reliability.py` is the script that produced the manuscript's headline pooled coefficients
(ordinal 0-5 alpha .725, nominal alpha .706, binary alpha .567) and the per-field table.
`reliability_report_ALL.json` and `reliability_per_field_ALL.csv` are its outputs for the
pooled layer (65 documents, three coders, codes 8 and 9 treated as missing).

What this folder does and does not do:
- It documents the pooling rule. The nominal headline pools 26 categorical fields (listed in
  the report's `per_field` entries with `type: nominal`), remapping each field's value set to a
  shared index before computing Krippendorff's nominal alpha over all three coders on units
  where all three are present.
- It does not reproduce the number from public inputs. The script reads the unpublished
  per-document coding JSON under a local path (`ROOT` at the top of the file). The published
  `ordinal_ratings.csv` reproduces the ordinal headline; the nominal headline has no public
  ratings export yet.
- The 17-field nominal permutation release elsewhere in this addendum tests distributions; it is
  not this coefficient and should not be read as a competing estimate.

Staged 2026-09-15 in response to a review question about the pooled nominal alpha.
