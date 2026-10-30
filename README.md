# Housing and timing gaps in construction

Versioned computational data and code associated with *Housing and the Timing Gaps in Construction: Private Property, Access and Collective Robotics* by Gonçalo Melo de Magalhães.

## Scope

This repository contains synthetic reference data and executable analysis. It includes a conserved 854-module construction inventory, geometric face-contact checks, an elastic connection study, a support-release diagnostic benchmark, a communication-topology experiment, a five-year delivery model, and a timed-claim valuation illustration.

The architectural proposal, physical assembly, contact strength, complete building safety, and territorial effects require further validation. These files report the declared computational cases; they do not report constructed or occupied robotic houses. No university affiliation is claimed for this deposit. The creator's research affiliation is Planta Smart Homes.

## Reproduce

Reference analysis used Python 3.14.7; a separate execution check used Python 3.12.14. Install the drawing dependencies with `python3 -m pip install -r requirements.txt`, then run:

```sh
python3 scripts/swarm_topology.py
python3 scripts/interface_analysis.py
python3 scripts/territory_model.py
python3 scripts/valuation_timing.py
python3 scripts/complete_sequence.py
python3 scripts/check_construction_contacts.py
python3 scripts/release_benchmark.py
```

The selected numerical outputs reproduce within 1e-8 absolute tolerance across the checked Python versions; discrete inventory, contacts and decision counts require exact equality. Reference output hashes are in `manifest.sha256.json`. Geometry and state assignments are prescribed reference cases, rather than solved autonomous motion trajectories. Diagnostic noise and loading inputs are selected assumptions.

## Timing correction in version 1.0.1

Admissions, need arrivals and qualified completions occur at month end. Dwelling-months and unmet-household-months integrate beginning-of-month stocks. This corrects the one-month overcount in dwelling service and aligns backlog exposure with the same convention. Completion totals and allocation results are unchanged. Corrected dwelling-years are 968.0, 1143.5 and 1241.67.

Independent verification is available through `python3 scripts/final_independent_checks.py` (NumPy required). It checks elastic cases using finite elements, valuation using a geometric series, connectivity using union-find, and delivery using cohorts.

## Citation and version

Please use `CITATION.cff`. Version 1.0.1 identifies this computational deposit. A GitHub release is a public versioned repository record; no DOI is claimed. The article's citation points to this record and its exact commit.

## Funding and tools

The author states that this study received no external funding. OpenAI Codex supported analytical-code development and research preparation. The deposited numerical outputs derive from the executable scripts. Explanatory architectural concept images and the manuscript itself are outside this data/code deposit.

## Licence and contact

No additional reuse licence has been selected for this release. Contact the author for reuse permission where needed: hi@planta.design. Creator ORCID: https://orcid.org/0009-0008-6255-7724.
