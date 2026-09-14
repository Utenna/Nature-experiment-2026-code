# Data access

## Participant survey data

The individual-level survey data (`merged_data0925.xlsx` and derived files) are **not
publicly available**. Participants consented to analysis by the research team, not to open
release. Requests for access for the purpose of reproducing or verifying the published
analyses are considered on a case-by-case basis and require a data-sharing agreement and,
where applicable, approval from the University of Hong Kong Human Research Ethics Committee
(Reference No. EA1910004(A3)).

**Contact:** B. Jiang (corresponding author). Requests are normally answered within 4 weeks.

## De-identified data shipped with the capsule

`codeocean_capsule/data/` (`data_balance.csv`, `data_analysis.csv`, `codebook.csv`) is
de-identified data sufficient to reproduce every reported statistic. It is **not published
to this git repository** (git-ignored, see `.gitignore`) because its own
`codeocean_capsule/data/README.md` restricts it to peer-review reproduction — do not
redistribute. It travels with the actual Code Ocean capsule submission, not with this
public git history.

## What you can do without the raw data

The code, comments, and `pipeline.md` fully specify every model, parameter, seed, and
output, and (via the de-identified capsule data, where you have access to it) reproduce
all reported estimates and intervals. Reviewers who need the restricted raw participant
data itself should request it through the contact above.
