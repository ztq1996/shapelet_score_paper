"""Shared plotting and analysis configuration for the shapelet-score paper.

Import this at the top of every notebook in ``nb/``::

    import importlib.util
    spec = importlib.util.spec_from_file_location("plot_config", "plot_config.py")
    plot_config = importlib.util.module_from_spec(spec); spec.loader.exec_module(plot_config)
    from plot_config import *

See ../CLAUDE.md for the conventions this file encodes.
"""

from pathlib import Path

import numpy as np
from matplotlib.ticker import MultipleLocator, LogLocator  # noqa: F401  (re-exported)

# ── Paths ────────────────────────────────────────────────────────────────────
# Notebooks run with nb/ as the working directory; the analysis repo is two up.
PAPER = Path(__file__).resolve().parent.parent
ANALYSIS = PAPER.parent
DATA = ANALYSIS / 'data'
FIG = PAPER / 'fig'

BVEC_DIR = DATA / 'shapelet_bvec'
STAMPS_DIR = DATA / 'stamps_stack_51'
PIFF_STAMPS_DIR = DATA / 'piff_stamps'

MOMENTS_PQ = DATA / 'psf_moments_allbands.pq'
DP2_VISIT_INFO_PQ = DATA / 'dp2_visit_info.pq'
POSTDP2_VISIT_INFO_PQ = DATA / 'post_dp2_visit_info.pq'

# ── Colour ───────────────────────────────────────────────────────────────────
PALETTE = ['#e46c32', '#5eb298', '#6e7aaa', '#b24342', '#5f4256']
# (228,108,50)  burnt orange
# (94,178,152)  sage green
# (110,122,170) slate blue
# (178,67,66)   muted red
# (95,66,86)    dark mauve

PALETTE_EXTENDED = PALETTE + [
    '#c99a2e',  #  5  amber gold
    '#d4bc72',  #  6  light wheat
    '#9baa3c',  #  7  yellow olive
    '#5a9c50',  #  8  grass green
    '#3d8c72',  #  9  dark teal green
    '#4ab0a8',  # 10  cyan teal
    '#3c84b0',  # 11  cornflower blue
    '#4a5c9c',  # 12  blue indigo
    '#7968b8',  # 13  periwinkle
    '#9856b2',  # 14  medium purple
    '#b44c8c',  # 15  magenta purple
    '#c46078',  # 16  dusty rose
    '#8c4c2c',  # 17  dark sienna
    '#8c7c5c',  # 18  warm khaki
    '#6c7c6c',  # 19  slate gray-green
]

BANDS = list('ugrizy')
BAND_COLORS = {'u': '#7B2FBE', 'g': '#1f9e89', 'r': '#e05c2c',
               'i': '#3b82c4', 'z': '#d4a520', 'y': '#888888'}

# ── Instrument ───────────────────────────────────────────────────────────────
PIXEL_SCALE = 0.2          # arcsec / pixel
FWHM_PER_SIGMA = 2.3548    # Gaussian FWHM = 2.3548 * sigma

# 21 science rafts; the four corner rafts (R00, R04, R40, R44) carry the
# wavefront sensors and are excluded from all star-based measurements.
SCIENCE_RAFTS = [
    'R01', 'R02', 'R03',
    'R10', 'R11', 'R12', 'R13', 'R14',
    'R20', 'R21', 'R22', 'R23', 'R24',
    'R30', 'R31', 'R32', 'R33', 'R34',
    'R41', 'R42', 'R43',
]

# AOS corner wavefront-sensor detectors, and the Zernike modes they report.
AOS_DETECTORS = [191, 195, 199, 203]
ZERNIKE_MODES = [f'z{i}' for i in range(4, 12)]   # Noll z4 (defocus) .. z11 (spherical)

# ── Dataset tags ─────────────────────────────────────────────────────────────
TAGS = ['dp2all', 'dp2post20251115', 'postdp2']
TAG_LABELS = {
    'dp2all':          'DP2',
    'dp2post20251115': 'DP2, after 2025-11-15',
    'postdp2':         'Post-DP2, 2026-01-13 to 2026-05-13',
}
TAG_VISIT_INFO = {
    'dp2all':          DP2_VISIT_INFO_PQ,
    'dp2post20251115': DP2_VISIT_INFO_PQ,
    'postdp2':         POSTDP2_VISIT_INFO_PQ,
}


def bvec_path(band, tag, piff=False):
    """Path to a compiled shapelet library for *band* and *tag*."""
    prefix = 'piff_shapelet' if piff else 'shapelet'
    return BVEC_DIR / f'{prefix}_{band}_{tag}.npz'


# ── Score definitions (see CLAUDE.md; these are the paper's definitions) ──────
#
# GalSim orders bvec by increasing N = p + q, and within each N from m = N down
# to m = 0 or 1, Re before Im.  At bmax = 6 there are 28 coefficients:
#
#   idx  0      b00                       N=0  m=0
#   idx  1,2    Re/Im b10                 N=1  m=1
#   idx  3-5    Re/Im b20, b11            N=2  m=2,0
#   idx  6,7    Re/Im b30                 N=3  m=3   <- trefoil-like
#   idx  8,9    Re/Im b21                 N=3  m=1   <- coma-like
#   idx 10-14   Re/Im b40, Re/Im b31, b22 N=4  m=4,2,0
#   idx 15,16   Re/Im b50                 N=5  m=5
#   idx 17,18   Re/Im b41                 N=5  m=3
#   idx 19,20   Re/Im b32                 N=5  m=1
#   idx 21-27   Re/Im b60, Re/Im b51,     N=6  m=6,4,2,0
#               Re/Im b42, b33
#
# The paper's shapelet score is the fraction of power in the odd-m modes with
# n >= 3.  A Gaussian core, an elliptical atmospheric profile, and any
# point-symmetric optical PSF all have identically zero odd-m power.
#
# n=1 (m=1, idx 1-2) is odd-m but is EXCLUDED: those two coefficients encode the
# residual centroid offset of the stamp relative to the adaptive-moment centroid,
# i.e. a registration artifact, not a PSF asymmetry.  On real i-band data they
# carry a median fractional power of ~1e-4, roughly 20% of the score, so the
# exclusion is numerically significant and not merely cosmetic.
#
# NOTE: this deliberately differs from NON_GAUSS_NON_ATMOSPHERE in
# ../scripts/shapelet_psf.py, which uses range(15, 24) and so picks up a
# rotationally incomplete slice of n=6 (Re/Im b_66 and Re b_64 only).
BMAX = 6

def _odd_m_indices(bmax=BMAX, n_min=3):
    """Indices of coefficients with odd m and n >= n_min, in GalSim bvec order."""
    out = []
    for n in range(bmax + 1):
        for q in range(n // 2 + 1):
            p = n - q
            m = p - q
            idx = n * (n + 1) // 2 + 2 * q
            if m % 2 == 1 and n >= n_min:
                out.extend([idx, idx + 1])       # Re and Im
    return sorted(out)


ODD_ORDER = _odd_m_indices()
assert ODD_ORDER == list(range(6, 10)) + list(range(15, 21)), ODD_ORDER

# The n=1 dipole (centroid) modes, excluded from the score but tracked as a
# diagnostic of stamp registration.
CENTROID_MODES = [1, 2]

# The order-3-only subset, for an apples-to-apples comparison against the
# third-order moment score.
THIRD_ORDER = list(range(6, 10))


def shapelet_score(bvec, indices=None):
    """Fractional shapelet power in *indices* (default: parity-odd modes).

    Parameters
    ----------
    bvec : ndarray, shape (N, n_coeff)
        Shapelet coefficient vectors from a compiled library.
    indices : list[int], optional
        Coefficient indices to sum over. Defaults to ``ODD_ORDER``.

    Returns
    -------
    ndarray, shape (N,)
        Score in [0, 1]; zero where the total power vanishes.
    """
    if indices is None:
        indices = ODD_ORDER
    bvec = np.atleast_2d(np.asarray(bvec, dtype=np.float64))
    total = np.sum(bvec ** 2, axis=1)
    part = np.sum(bvec[:, indices] ** 2, axis=1)
    return np.where(total > 0, part / total, 0.0)


COMA_WEIGHT = 3.0


def moment_score(c11, c12, c31, c32, coma_weight=COMA_WEIGHT):
    """Weighted third-order moment score: w*|coma|^2 + |trefoil|^2.

    ``c11 = M30 + M12`` and ``c12 = M21 + M03`` are the spin-1 (coma-like)
    combinations; ``c31 = M30 - 3*M12`` and ``c32 = 3*M21 - M03`` are the
    spin-3 (trefoil-like) combinations of the dimensionless HSM third-order
    moments. The paper uses ``coma_weight = 3``.
    """
    coma_sq = np.asarray(c11, dtype=np.float64) ** 2 + np.asarray(c12, dtype=np.float64) ** 2
    trefoil_sq = np.asarray(c31, dtype=np.float64) ** 2 + np.asarray(c32, dtype=np.float64) ** 2
    return coma_weight * coma_sq + trefoil_sq


# ── Score tiers ──────────────────────────────────────────────────────────────
# (name, lower bound inclusive, upper bound exclusive, colour)
TIERS = [
    ('LOW',       None,  0.002, '#3c84b0'),
    ('MEDIUM',    0.002, 0.005, '#5a9c50'),
    ('HIGH',      0.005, 0.02,  '#e46c32'),
    ('VERY HIGH', 0.02,  None,  '#b24342'),
]
TIER_NAMES = [t[0] for t in TIERS]
TIER_COLORS = {t[0]: t[3] for t in TIERS}
TIER_EDGES = [0.002, 0.005, 0.02]


def classify_tier(score):
    """Assign scores to tier names using >= at every boundary."""
    score = np.asarray(score, dtype=np.float64)
    out = np.full(score.shape, 'LOW', dtype=object)
    out[score >= 0.002] = 'MEDIUM'
    out[score >= 0.005] = 'HIGH'
    out[score >= 0.02] = 'VERY HIGH'
    return out


# ── Visit-ID helpers ─────────────────────────────────────────────────────────
def day_obs(visit_id):
    """Night of observation as an integer YYYYMMDD."""
    return np.asarray(visit_id, dtype=np.int64) // 100_000


def detector_to_raft():
    """Map detector id -> raft name for the 189 science CCDs (e.g. 42 -> 'R12').

    LSSTCam numbers the science detectors 0-188, nine per raft, in the raft
    order of ``SCIENCE_RAFTS``, so ``raft = SCIENCE_RAFTS[det // 9]``. This has
    been verified against the ``detector``/``raft`` pairs stored in the stamp
    files; it avoids depending on the LSST stack, which is not importable in the
    bare environment these notebooks run in.
    """
    return {det: SCIENCE_RAFTS[det // 9] for det in range(9 * len(SCIENCE_RAFTS))}


def detector_to_raft_from_stamps(n_files=6):
    """Independent check: derive the mapping from the stamp files themselves."""
    import numpy as _np
    out = {}
    for f in sorted(STAMPS_DIR.glob('stamps_*.npz'))[:n_files]:
        d = _np.load(f, allow_pickle=True)
        for det, raft in zip(d['detector'], d['raft']):
            out[int(det)] = str(raft)
    return out


# ── Matplotlib defaults ──────────────────────────────────────────────────────
def apply_style():
    """Apply the paper's matplotlib defaults. Call once per notebook."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'figure.dpi': 110,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'font.size': 9,
        'axes.labelsize': 9,
        'axes.titlesize': 9,
        'legend.fontsize': 8,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.top': True,
        'ytick.right': True,
        'xtick.minor.visible': True,
        'ytick.minor.visible': True,
        'axes.prop_cycle': plt.cycler(color=PALETTE),
        'figure.autolayout': False,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
    })


# Single-column and full-width figure sizes for the SPIE two-column layout.
FIG_COL = (3.5, 2.6)
FIG_WIDE = (7.0, 2.6)
