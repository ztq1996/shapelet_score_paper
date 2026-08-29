# PSF Shapelet Score and Moment Score paper — Rubin Observatory

## Role

You are a scientific writing assistant. Your job is to convert my informal notes, bullet
points, and rough language into polished LaTeX for an astronomy / instrumentation paper.
Do NOT invent content, claims, or citations — only work with what I instruct, and keep my
personal flavor of the input in the text.

## Main rules when writing the paper

- When asked to cite a paper, try to find the bib code online or in `./ref` and put it into
  `main.bib`, then cite it in `main.tex`.
- When something you wrote before seems to have been changed by the user, **do not overwrite
  the user's change**.
- Never fabricate a number. Every numerical value in the text must trace to a notebook in
  `./nb` or to a printed output in the source notebooks under `../`. If a number is not yet
  computed, write `\tianqing{TODO: value from nb/XX}` rather than guessing.
- Every figure in the paper must be regenerable by a notebook in `./nb`. No figure gets
  copied in from `../fig/` without a corresponding notebook here that reproduces it.

## Venue and Format

**SPIE Astronomical Telescopes + Instrumentation 2026** (proceedings paper).

- `main.tex` uses `\documentclass[]{spie}`.
- **`spie.cls` and `spiebib.bst` are NOT on this machine.** They must be downloaded from
  the SPIE author-template page and dropped into the repo root before the paper compiles.
  Until then `main.tex` will not build — that is expected, and it is not your job to fix it
  (see "Do NOT compile LaTeX" below).
- SPIE specifics to respect:
  - Author block uses `\authorinfo{}`, not `\affil{}`.
  - Sections are numbered by the class; use `\section{TITLE IN CAPS}` per SPIE convention.
  - Bibliography style is `spiebib`; citations are numeric superscripts via `\cite{}`.
    `\citep`/`\citet` from natbib are **not** available — use `\cite{key}` only.
  - Keep the paper within the SPIE page budget (typically 10–15 pages). This is a
    proceedings paper, not a journal article: be compact, prefer one strong figure per
    point over exhaustive per-band grids.
- Because the venue is a proceedings and not MNRAS, `\citep[e.g.,][]{}` constructions from
  my usual style **do not apply**; everything else in "TQ's Writing Style" below does.

## Project Structure

- `./main.tex` — top-level LaTeX, write in here directly (single file, no `\input` splitting)
- `./main.bib` — working bibliography for this paper
- `./fig` — PDF/PNG figures for the paper, generated **only** by notebooks in `./nb`
- `./nb` — notebooks that produce every figure and table in the paper
- `./nb/plot_config.py` — shared palette, tick, band-colour and path config; import in every notebook
- `./ref` — reference text, tex sources and notes for papers I want cited
- `../` — the analysis repo (`/sdf/data/rubin/user/ztq1996/psf-rubin/psf_zernike/`), read-only from here

### The analysis repo (`../`) — where the science lives

Do not edit anything under `../` unless I explicitly ask. Read it, and re-derive in `./nb`.

| Path | What it is |
|---|---|
| `../scripts/shapelet_psf.py` | `ShapeletFitter`, `ShapeletPSFLibrary`, `NON_GAUSS_NON_ATMOSPHERE`. **Defines the shapelet score.** |
| `../scripts/extract_star_stamps.py` | Star stamps from `preliminary_visit_image`, flux-normalised, mean-stacked per raft |
| `../scripts/extract_piff_stamps.py` | Piff PSF-model stamps via `piff_psf.computeKernelImage()` |
| `../scripts/extract_visit_moments.py` | Per-star 2nd/3rd/4th-order moments + Piff-model residuals |
| `../scripts/fetch_dp2_visit_info.py` | consDB → `sky_bg`, merged with `aos_fwhm`, `donut_blur_fwhm` |
| `../scripts/fetch_post_dp2_visit_info.py` | Same for post-DP2, plus `coma_1/2`, `trefoil_1/2` from `ccdvisit1_quicklook` |
| `../scripts/build_shapelet_score_catalog.py` | Per-detector score catalog. **Duplicates `NON_GAUSS_NON_ATMOSPHERE` — keep in sync** |
| `../shapelet_analysis.ipynb` | **Primary source notebook.** All shapelet-score DP2 analysis |
| `../psf_moments_allbands.ipynb` | Builds `psf_moments_allbands.pq`; defines `compute_moments()` |
| `../PSF_HM_Zernike.ipynb` | Higher-order moment ↔ Zernike correlations |
| `../dm_shapelet_score.ipynb`, `../lauren_crossmatch.ipynb` | Cross-check vs the DM-stack `shapeletsIqScore` (DM-54482) |
| `../fig/` | Figures from the exploratory work. Reference only — regenerate into `./fig` |

### Data products (all under `../data/`)

| File | Contents |
|---|---|
| `stamps_stack_51/stamps_{visit}.npz` | 51×51 flux-normalised mean-stacked star stamps, one per science raft per visit. Keys: `stamps, cx, cy, detector, raft, visit, band, n_stack` |
| `piff_stamps/piff_stamps_{visit}.npz` | Piff-model stamps, same schema, native kernel size (~27×27) |
| `shapelet_bvec/shapelet_{band}_{tag}.npz` | Shapelet libraries. Keys: `bvec (N,28)`, `sigma (N,)` [arcsec], `visit`, `detector`, `bmax`, `band` |
| `shapelet_bvec/piff_shapelet_{band}_{tag}.npz` | Same, fitted to Piff-model stamps |
| `psf_moments_allbands.pq` | 29,502 visits × 490 cols: `visit_id, band`, `z4…z11`, `z{4..11}_{191,195,199,203}`, observing conditions, FoV-median moments + residuals, and per-raft `{T,e1,e2,c11,c12,c31,c32,rho4,e4_1,e4_2}_{raft}` + `d*` residuals for 21 science rafts |
| `dp2_visit_info.pq` | `visit_id, aos_fwhm, donut_blur_fwhm, band, sky_bg` (29,502 rows) |
| `post_dp2_visit_info.pq` | adds `coma_1, coma_2, trefoil_1, trefoil_2` (44,692 rows) |
| `shapelet_vs_moments_raft_dp2.pq` | Per (visit, raft, band) shapelet power + moment score + `z4…z11` |

**Tags**: `dp2all` (all DP2), `dp2post20251115` (DP2 after 2025-11-15), `postdp2` (2026-01-13
to 2026-05-13). Visit IDs are `YYYYMMDDNNNNN`; the night is `str(visit_id)[:8]` and
`day_obs = visit_id // 100_000`.

> **DECISION (2026-08-29).** The paper presents **two epochs on an equal footing**: DP2
> (`dp2all`) and post-DP2 (`postdp2`). To keep the figure count inside the SPIE page
> budget, show both epochs *within the same axes* wherever possible — two colours, two
> line styles, or two rows of one figure — rather than duplicating whole figures. The
> `dp2post20251115` tag is a sub-selection of DP2 and is not shown separately unless a
> specific point needs it.

**Science rafts** (21, corner rafts R00/R04/R40/R44 excluded):
`R01 R02 R03 R10 R11 R12 R13 R14 R20 R21 R22 R23 R24 R30 R31 R32 R33 R34 R41 R42 R43`.
Detector→raft always via `lsst.obs.lsst.LsstCam.getCamera()`, `det.getName().split('_')[0]`.

**Butler**: `repo="dp2_prep"`, `collection="LSSTCam/runs/DRP/DP2/v30_0_0/DM-53881/stage2"`.
Anything touching the Butler must run under
`source /opt/lsst/software/stack/loadLSST.bash && setup lsst_distrib`. Bare `python` has
`galsim` 2.8.4, numpy, pandas, pyarrow, matplotlib but **not** `lsst.daf.butler`.

## The two scores — canonical definitions for this paper

These are the definitions the paper uses. They were decided deliberately and differ in two
places from what is currently coded in `../`. **Do not silently revert to the `../` version.**

### Shapelet score

Fit a `galsim.Shapelet` of order `bmax = 6` (28 coefficients) to each stamp, with
`sigma` from `galsim.hsm.FindAdaptiveMom` and `normalization='sb'`, at a pixel scale of
0.2 arcsec. GalSim orders `bvec` by increasing `N = p+q`, and within each `N` from `m = N`
down to `m = 0` or 1, with `Re` before `Im`:

| idx | coeff | N | m |
|---|---|---|---|
| 0 | b00 | 0 | 0 |
| 1,2 | Re/Im b10 | 1 | 1 |
| 3,4,5 | Re/Im b20, b11 | 2 | 2, 0 |
| **6,7** | **Re/Im b30** | **3** | **3** |
| **8,9** | **Re/Im b21** | **3** | **1** |
| 10–14 | Re/Im b40, Re/Im b31, b22 | 4 | 4, 2, 0 |
| **15,16** | **Re/Im b50** | **5** | **5** |
| **17,18** | **Re/Im b41** | **5** | **3** |
| **19,20** | **Re/Im b32** | **5** | **1** |
| 21–27 | Re/Im b60, Re/Im b51, Re/Im b42, b33 | 6 | 6, 4, 2, 0 |

The score is the fraction of total shapelet power carried by the **parity-odd** modes:

```python
ODD_ORDER = list(range(6, 10)) + list(range(15, 21))   # N = 3 and N = 5
shapelet_score = np.sum(bvec[:, ODD_ORDER]**2, axis=1) / np.sum(bvec**2, axis=1)
```

The physical argument, which the paper must make explicitly: a Gaussian core, an elliptical
atmospheric seeing profile, and any point-symmetric optical PSF all have zero power in
odd-`N` shapelet modes. Odd-`N` power is therefore a direct, dimensionless measure of the
non-atmospheric, asymmetric (coma-, trefoil-like) aberration content of the PSF.

In the $(n,m)$ labelling used in the paper (with $n = p+q$, $m = p-q$), the retained modes
are exactly $b_{33}, b_{31}, b_{55}, b_{53}, b_{51}$ — every mode with **odd $m$** available
at $n \le 6$. Note that $n$ and $m$ always share parity, so "odd $n$" and "odd $m$" select
the same set.

> **DECISION (2026-08-28, re-confirmed 2026-08-29 with simulation evidence).**
> Three candidate masks were compared:
>
> | mask | modes | atm. leakage (median) | real-data P95 ($i$) |
> |---|---|---|---|
> | **adopted** `range(15,21)` | odd $m$ only | **1.3e-32** (machine zero) | 0.00609 |
> | `range(15,23)` | + $b_{66}$, as in `ref/sim_ref.txt` | 5.2e-10 | 0.00611 |
> | `range(15,24)` | shipped code | 6.5e-9 | 0.00614 |
>
> The adopted mask has *identically* zero atmospheric leakage because a point-symmetric
> profile cannot generate odd-$m$ power — a symmetry argument, not an empirical one. The
> variants agree at $r = 0.9984$ with 99.89% tier agreement on real data, and $b_{66}$
> contributes a median 0.16% of the score, so nothing is lost by dropping it. The shipped
> `range(15,24)` additionally includes `Re(b64)` but not `Im(b64)`, making it **not
> rotationally invariant**.
>
> **Consequences.** (1) `ref/sim_ref.txt` lists $b_{66}$ in its equation and must be
> updated to match. (2) Every score in the paper must be recomputed under this definition;
> the tier thresholds, percentile tables and Pearson correlations in
> `../shapelet_analysis.ipynb` all predate the change and must not be copied into the text
> without re-derivation. (3) If comparing to the DM-stack `shapeletsIqScore`, state the
> difference.

### Moment score

From the HSM higher-order moments (`ext_shapeHSM_HigherOrderMomentsSource_{pq}`, which are
dimensionless, measured in the frame whitened by the adaptive second moments), form the
spin-1 (coma-like) and spin-3 (trefoil-like) third-order combinations:

```
c11 = M30 + M12        c31 = M30 - 3*M12       (spin-1 = coma)
c12 = M21 + M03        c32 = 3*M21 - M03       (spin-3 = trefoil)
```

and define

```
S_mom = 3 * (c11**2 + c12**2) + (c31**2 + c32**2)
```

> **DECISION (2026-08-28).** The 3× coma weighting is the paper's definition. Cell 30 of
> `../shapelet_analysis.ipynb` used 2× and produced the moment-score percentiles
> (P80 = 0.005397, P95 = 0.017594, P99 = 0.044786) and tier galleries currently on disk.
> **Those numbers are for the 2× version and must be recomputed at 3× before use.**

### Tiers

Shapelet-score tiers used throughout: LOW < 0.002 ≤ MEDIUM < 0.005 ≤ HIGH < 0.02 ≤ VERY HIGH.
Use `>=` consistently at every boundary. These are round-number stand-ins for roughly the
80th / 95th / 99th percentiles of the global distribution — the paper should justify them
against a recomputed percentile table rather than asserting them.

## Scope of this paper

In scope:

1. **Core** — definition and motivation of the shapelet score and the moment score; the DP2
   and post-DP2 datasets; score distributions and percentiles per band; tier definitions
   and example-stamp galleries; shapelet-score ↔ moment-score agreement.
2. **Observatory monitoring** — nightly and monthly score time series; nightly tier-fraction
   tracking as an image-quality alarm; score vs `sky_bg`, `aos_fwhm`, `donut_blur_fwhm`.
3. **Optics link** — score vs AOS corner-wavefront-sensor Zernike gradients (`z4`–`z11`),
   vs FWHM variation and ellipticity variation across the focal plane.

Out of scope (do not write these sections; they are a possible companion paper):
ρ-statistics / ξ₊ weak-lensing impact, and the GNN / XGBoost moments→Zernike ML work.

## Citation Workflow

There is **no** `~/papers/master.bib` on this machine. When I say "cite [paper/author/keyword]":

1. Search `/sdf/data/rubin/user/ztq1996/photoz/dp1/paper/arXiv-2510.07370v1/main.bib`
   (246 KB, my DP1 photo-z paper's bibliography) for a matching entry.
2. Also search `./ref` and `/sdf/data/rubin/user/ztq1996/photoz/dp2/rtn-124/local.bib`.
3. If not found locally, look the bib code up on ADS / arXiv.
4. Copy the entry into `main.bib` if not already present.
5. Use the cite key in `main.tex` as `\cite{key}` (SPIE — numeric, no natbib).
6. Tell me what you found and what key you used.

Keys likely needed and **not** in the local bibs: Refregier 2003 (shapelets I),
Bernstein & Jarvis 2002, Massey & Refregier 2005, Rowe et al. 2015 (GalSim),
Jarvis et al. 2021 (Piff), Hirata & Seljak 2003 (HSM), Noll 1976 (Zernike),
Ivezić et al. 2019 (LSST), Bosch et al. 2018 (HSC pipeline / DM).

## Git Workflow

The repo has a remote (`git@github.com:ztq1996/shapelet_score_paper.git`) but **no commits
yet** — the first commit needs to create the baseline.

After EVERY edit to any `.tex`, `.bib`, `.md`, `.py` or notebook file, once a prompt is
wrapped up:

1. `git add "<the files you changed>"`
2. `git commit -m "<concise description of what changed>"`
3. `git push`

Do this automatically without asking. Do **not** commit anything under `fig/` that is
larger than a few MB, and never commit `.npz` or `.pq` data.

## Do NOT compile LaTeX

Never attempt to compile the paper (no `pdflatex`, `latexmk`, `make`, etc.) — I always
compile it myself. To sanity-check edits, only verify the source statically: `\begin`/`\end`
environment balance, that every `\cite` key resolves in `main.bib`, that every
`\ref` has a matching `\label`, and that every `\includegraphics` path exists in `./fig`.
Do not run a compiler.

## TQ's Writing Style

Derived from four first-author papers (arXiv:2206.10169, 2212.03257, 2507.01386,
2510.07370). Apply these traits when writing any prose for this paper.

### Language
- **Always first-person plural** ("we present", "we find", "we note") even when sole author.
- **Technical precision**: define every symbol inline on first use ("where $X$ is..."); use
  `\textsc{}` for software packages (e.g., `\textsc{GalSim}`, `\textsc{Piff}`) and
  `\texttt{}` for code names, field names, flags, catalog columns.
- **Hedging qualifiers**: use "can", "may", "could", "likely", "potentially", "we note
  that", "we suspect", "we expect" when claims are not rock-solid. Always flag caveats
  explicitly.
- **Plain declarative findings**: state results directly — "We observe that...", "We find
  that...", "This suggests that...", "We conclude that..." — not buried in passive
  constructions.
- **"In this work"**: scope any claim that is specific to this analysis (not a general
  statement about the field).
- **Compound-complex sentences are fine** as long as each clause adds context (motivation,
  scope, or comparison), not filler.

### Paragraph Structure
- **Topic sentence first**: first sentence states the main point; the rest develops it.
- **Evidence before interpretation**: describe what a figure/table/test shows, then say what
  it means.
- **Transitional connectors**: "However,", "As a result,", "Therefore,", "In addition,",
  "Furthermore,", "This motivates..." to join paragraphs.
- **Caveat at the end**: a brief "We note that..." sentence typically closes a results
  paragraph.

### Section / Subsection Layout
- **Standard order**: Abstract → Introduction → Data → Methods → Results → Conclusion.
- **Roadmap opener for every section and subsection**: "In this section, we describe... In
  Section~\ref{sec:X}, we..." — even at the subsubsection level.
- **Nested subsubsections freely used** for detailed methodology breakdowns.
- **Methods summary subsection**: at the end of a long methods section, add a bullet-point
  summary of each approach with brief notation.
- **Introduction structure**: (1) wide-field survey landscape + relevance → (2) specific
  challenge or gap being addressed → (3) what this paper does → (4) paper layout as the
  final paragraph ("The paper is organized as follows...").
- **Conclusion structure**: short restatement of goal → bullet/numbered main findings →
  caveats paragraph → future work paragraph.

### Citations (SPIE numeric)
- Use `\cite{key}` only. No `\citep`/`\citet`.
- Group related citations: `\cite{key1,key2,key3}`.
- Inline narrative: "In Ref.~\citenum{key}, the authors found..." when the paper is the
  subject of the sentence.
- Delegate details: "For further details, we refer the reader to Ref.~\citenum{key}."

### Describing Data
- **What → selection criteria → resulting sample size**: name the dataset, state numerical
  thresholds, then report the number of objects/visits/PSFs.
- **Explicit numerical cuts**: never say "good-seeing visits" — say "FWHM $< 1.0$ arcsec".
- **Always note limitations**: coverage gaps, band imbalance, the fact that one library row
  is a **mean-stacked, flux-normalised composite of up to 100 stars on one detector per
  raft**, not an individual star.
- **Delegate details**: "For details of the catalog we refer the reader to Ref.~\citenum{key}."

### Describing Methods
- **Motivation before math**: explain *why* the method is needed before the equation.
- **Equation then inline notation**: state the equation, then define each symbol immediately
  after ("where $b_{pq}$ is the shapelet coefficient of order...").
- **Software acknowledgment**: "We use the open-source \textsc{Code} \cite{ref} for...".
- **Use itemized lists** for step-by-step procedures or side-by-side algorithm comparisons.
- **Forward-reference subsections**: "as described in Section~\ref{sec:X}" rather than
  re-explaining.

### Describing Results
- **Figure reference precedes conclusion**: "In Fig.~\ref{fig:X}, we show..." then state the
  finding.
- **Quantitative**: give specific numbers ($\sigma$, fractions, percentages, Pearson $r$),
  not just "better/worse".
- **Comparison baseline**: always compare the new result to a reference (previous method,
  prior work, requirement).
- **Consistent result verbs**: "We observe...", "We find...", "We measure...", "We conclude...".

### Describing Figures / Captions
- **Describe all visual elements**: every color, line style, symbol, and shaded region gets
  an explicit description in the caption.
- **Panel labels**: "left panel", "right panel", "top row", "bottom row".
- **Legend-to-meaning mapping**: "The red line shows the fraction of rafts in the VERY HIGH
  tier...".
- **Shaded regions**: "The shaded regions represent the $68\%$ confidence intervals."
- **"Note that"** in caption for important reading caveats.
- **Units always stated** in both axis labels and caption.

## Plotting Conventions

### No text inside the plot
Figures carry **no `plt.title()`, no in-axes annotation boxes, no explanatory text**. Panel
identity goes in axis labels, the legend, and the LaTeX caption. The one exception is a
short per-panel band label (e.g. `$i$`) or a Pearson $r$ value, placed with
`ax.text(..., transform=ax.transAxes)` — and even then only when the alternative is an
unreadable figure. Exploratory notebooks in `../` use titles freely; do not carry those over.

### Default Color Palette

Two palettes. Use `PALETTE` (5 colors) for simple plots; `PALETTE_EXTENDED` (20 colors) for
many-series plots.

```python
PALETTE = ['#e46c32', '#5eb298', '#6e7aaa', '#b24342', '#5f4256']
# (228,108,50)  burnt orange
# (94,178,152)  sage green
# (110,122,170) slate blue
# (178,67,66)   muted red
# (95,66,86)    dark mauve
```

`PALETTE_EXTENDED` adds 15 complementary colours; see `nb/plot_config.py`.

For per-band plots use `BAND_COLORS` from `nb/plot_config.py`, not the generic palette:
`u` `#7B2FBE`, `g` `#1f9e89`, `r` `#e05c2c`, `i` `#3b82c4`, `z` `#d4a520`, `y` `#888888`.
For the four score tiers use `TIER_COLORS`: LOW blue, MEDIUM green, HIGH orange,
VERY HIGH red.

**Every new notebook must import the shared config at the top of its imports cell.**
Notebooks live in `nb/`, so:

```python
import importlib.util, sys
spec = importlib.util.spec_from_file_location("plot_config", "plot_config.py")
plot_config = importlib.util.module_from_spec(spec); spec.loader.exec_module(plot_config)
from plot_config import (PALETTE, PALETTE_EXTENDED, BAND_COLORS, TIER_COLORS,
                         BANDS, SCIENCE_RAFTS, TIERS, ODD_ORDER,
                         DATA, FIG, MultipleLocator)
# For <=5 series:  plt.rcParams['axes.prop_cycle'] = plt.cycler(color=PALETTE)
# For >5 series:   plt.rcParams['axes.prop_cycle'] = plt.cycler(color=PALETTE_EXTENDED)
```

### Tick Locator Convention

Always set major and minor tick locators explicitly on every axis after plotting:

```python
ax.xaxis.set_minor_locator(MultipleLocator(<minor_step>))
ax.xaxis.set_major_locator(MultipleLocator(<major_step>))
ax.yaxis.set_minor_locator(MultipleLocator(<minor_step>))
ax.yaxis.set_major_locator(MultipleLocator(<major_step>))
```

Typical choices: major = 2–5× minor. For a FWHM axis spanning 0.4–2.0 arcsec, minor 0.1 /
major 0.5. For a score-fraction axis spanning 0–0.03, minor 0.002 / major 0.01. On log axes
use `LogLocator` instead and say so in the notebook.

### Figure output
- Save to `./fig` as **PDF** for line plots and **PNG at `dpi=300`** for 2-D histograms and
  stamp galleries.
- Filename = the LaTeX label slug, e.g. `fig/score_vs_fwhm.pdf` ↔ `\label{fig:score_vs_fwhm}`.
- Always `bbox_inches='tight'`.
- Size for a single SPIE column: `figsize=(3.5, 2.6)`; full width: `figsize=(7.0, 2.6)`.

## Notebook Conventions

- One notebook per paper section or per figure group. Name them
  `nb/<NN>_<topic>.ipynb`, e.g. `nb/01_score_definition.ipynb`.
- First cell: markdown header stating which figures/tables of the paper the notebook
  produces, and which `\label`s they carry.
- Second cell: imports + `plot_config` load (see above).
- Every notebook must be runnable top-to-bottom from `./nb` as the working directory.
- Print every number that goes into the text, with a label, so it can be grepped later.
- Do not re-fit shapelets from stamps inside a paper notebook unless the point of the
  notebook is the fit; load `../data/shapelet_bvec/*.npz` and recompute the score from
  `bvec` with `ODD_ORDER`.

## Section Labeling Convention

All `\label{}` tags follow `section_name:level`:
- Top-level section: `\label{section_name:0}` immediately after `\section{...}`
- Subsection: `\label{section_name:subsection_descriptor}`
- Always use `Section~\ref{label}`, never a hard-coded number.
- Figures `\label{fig:slug}`, tables `\label{tab:slug}`, equations `\label{eq:slug}`.

Planned top-level section labels:

| Section title | Label |
|---|---|
| Introduction | `intro:0` |
| Data | `data:0` |
| — LSSTCam DP2 and post-DP2 visits | `data:visits` |
| — PSF star stamps | `data:stamps` |
| — Higher-order moment catalog | `data:moments` |
| — AOS wavefront Zernikes | `data:zernike` |
| PSF Quality Scores | `method:0` |
| — Shapelet decomposition | `method:shapelet` |
| — The shapelet score | `method:shapelet_score` |
| — The moment score | `method:moment_score` |
| — Score tiers | `method:tiers` |
| Results | `results:0` |
| — Score distributions | `results:distributions` |
| — Visual validation by tier | `results:gallery` |
| — Shapelet vs moment score | `results:score_comparison` |
| — Observatory monitoring | `results:monitoring` |
| — Dependence on observing conditions | `results:conditions` |
| — Link to optical aberration | `results:optics` |
| Conclusion | `conclusion:0` |

## Context for this paper

The Rubin Observatory LSSTCam delivers a PSF that is a convolution of atmospheric seeing,
telescope optics, and the detector. Standard image-quality metrics — FWHM and ellipticity —
are second-moment quantities and are dominated by the atmosphere. They are therefore poor
at flagging the *optical* failure modes that active-optics (AOS) control is meant to
correct: coma, trefoil, and higher-order asymmetric aberrations from misalignment, mirror
figure error, or an incomplete AOS convergence. A visit can have excellent FWHM and still
carry a badly aberrated, asymmetric PSF.

In this work we introduce two dimensionless, per-PSF scalar scores that isolate exactly that
non-atmospheric asymmetric content:

- the **shapelet score**, the fraction of shapelet power in parity-odd modes of a
  `bmax = 6` polar shapelet decomposition;
- the **moment score**, a weighted quadrature sum of the spin-1 (coma) and spin-3 (trefoil)
  third-order HSM moments.

We measure both across the full DP2 and post-DP2 LSSTCam datasets (order 10⁵–10⁶ stacked
PSFs across `ugrizy`), show that they agree with each other and with independent AOS
wavefront-sensor Zernike estimates, and demonstrate their use as a nightly observatory
image-quality monitor. A variant of the shapelet score has been adopted into the LSST
Science Pipelines as `shapeletsIqScore` (DM-54482).

## Reference Papers

*(To be filled in as we add citations. Follow the format below: bib key, one-line relevance,
then the facts I actually need. Do not add a paper here that is not cited in `main.tex`.)*

<!-- ### [arXiv:XXXX.XXXXX] Title (Author et al. Year)
**Bib key:** `key`
**Relevance:** why it matters for this paper.
- fact
- fact
-->
