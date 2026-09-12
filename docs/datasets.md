# Data Innovation Challenge — sanctioned datasets and tools

Source: <https://itcodefair.cdu.edu.au/datasciencechalllenge_datasets/>
Transcribed 11 September 2026. The organiser's page lists the names only, with no URLs. The
"what it is" and "why it matters" columns below are added context, not organiser text, and
should be verified before being cited in the report.

> Participants may utilise the following resources, split into datasets and development tools.

## Datasets (organiser's list, verbatim names)

| # | Dataset | What it is | Why it matters here |
|---|---|---|---|
| 1 | NT Remote Areas Mobile Coverage | NT Government view of mobile coverage in remote areas | The most locally specific source; the natural spine of the analysis |
| 2 | ADII (Australian Digital Inclusion Index) Dashboard | Access, affordability and digital ability scores by region and demographic | Turns "no signal" into "no inclusion"; brings affordability and skills into a coverage story |
| 3 | National Broadband Network (NBN) dataset | Fixed-line, fixed-wireless and satellite service availability | Fixed access, complementing the mobile picture; Sky Muster satellite is the remote reality |
| 4 | ACCC Mobile Infrastructure Report — data release | Regulator's audit of mobile infrastructure, including tower and carrier data | Independent of the carriers' own marketing maps; good for cross-checking claims |
| 5 | Tropical cyclone reports | Bureau of Meteorology cyclone tracks and impact reports | Connectivity in the NT is seasonal; resilience during cyclone season is the sharper question |
| 6 | First Nations Connectivity Mapping Tool | Community-level connectivity mapping for First Nations communities | Community-level granularity, and the source that carries data sovereignty considerations |
| 7 | ACMA Site Location Map | Radiocommunications site and licence locations from the media authority | Ground truth on where transmitters physically are, versus where coverage is claimed |
| 8 | ABS TableBuilder | Australian Bureau of Statistics custom census table builder | Population, remoteness, language and socioeconomic denominators for any per-capita claim |

Other public datasets relevant to connectivity, geography, or community demographics are
explicitly allowed.

## Tools (organiser's list, verbatim)

- Python and related data analysis libraries
- AI / Machine Learning libraries
- Public data APIs
- Other development, visualisation and mapping tools

## Practical notes

- **Predicted coverage is not measured coverage.** Carrier and government coverage layers are
  usually propagation model output. Where a source is modelled rather than measured, say so in
  the Methodology section. Judges from the NT Government department will know the difference.
- **Geographic joins need a stated spatial unit.** ABS boundaries (SA1/SA2, remoteness areas),
  community locality boundaries and coverage rasters do not share a geometry. Pick the unit,
  justify it, and be explicit about what is lost in the conversion.
- **Sparse population breaks per-capita statistics.** A remoteness area with a few hundred
  people produces unstable rates and identifiable individuals. Both are reasons to aggregate
  carefully, and both are worth a paragraph in the Discussion.
- **Licensing belongs in the References section.** The requirement page asks for "official
  articles, data, resources, peer-reviewed publications, and tools with links", so every
  dataset used needs a link and, where it exists, its licence.
