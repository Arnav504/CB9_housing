"""Service Saturation Index formulas printed in the CB9 housing report.

The body formula is on printed pages 36–37. The appendix formula is on printed
page 54. The appendix names a CB9 average without writing that average out;
``appendix_ssi`` uses the same three-term expression, evaluated at the printed
district-average rates, as the denominator.
"""

from __future__ import annotations

MAIN_WEIGHTS = {"mh": 0.4, "sh": 0.4, "fp": 0.2}


def main_ssi(
    mh: float,
    sh: float,
    fp: float,
    mh_bar: float,
    sh_bar: float,
    fp_bar: float,
) -> float:
    """Weighted index. A result of 100 matches the CB9 average rates."""
    _require_positive_bars(mh_bar, sh_bar, fp_bar)
    score = (
        MAIN_WEIGHTS["mh"] * (mh / mh_bar)
        + MAIN_WEIGHTS["sh"] * (sh / sh_bar)
        + MAIN_WEIGHTS["fp"] * (fp / fp_bar)
    )
    return score * 100


def weighted_terms(
    mh: float,
    sh: float,
    fp: float,
    mh_bar: float,
    sh_bar: float,
    fp_bar: float,
) -> dict[str, float]:
    """Each weight times the tract-to-district ratio, already scaled by 100."""
    _require_positive_bars(mh_bar, sh_bar, fp_bar)
    return {
        "mh_ratio": mh / mh_bar,
        "sh_ratio": sh / sh_bar,
        "fp_ratio": fp / fp_bar,
        "mh_points": MAIN_WEIGHTS["mh"] * (mh / mh_bar) * 100,
        "sh_points": MAIN_WEIGHTS["sh"] * (sh / sh_bar) * 100,
        "fp_points": MAIN_WEIGHTS["fp"] * (fp / fp_bar) * 100,
    }


def appendix_ssi(
    mh: float,
    sh: float,
    fp: float,
    mh_bar: float,
    sh_bar: float,
    fp_bar: float,
) -> float:
    """(MH + 2×SH + FP) divided by the same expression at the CB9 average rates."""
    numer = mh + (2 * sh) + fp
    denom = mh_bar + (2 * sh_bar) + fp_bar
    if denom == 0:
        raise ZeroDivisionError("CB9 counterpart must be non-zero")
    return numer / denom * 100


def band_for(score: float) -> str:
    """Map a score onto the printed threshold table.

    The printed bands share the endpoints 100, 120, and 150. Scores on a shared
    endpoint use the lower band.
    """
    if score < 50:
        return "Critically under-served"
    if score < 100:
        return "Under-served"
    if score <= 120:
        return "Balanced"
    if score <= 150:
        return "Approaching saturation"
    return "Over-saturated"


def _require_positive_bars(mh_bar: float, sh_bar: float, fp_bar: float) -> None:
    if mh_bar == 0 or sh_bar == 0 or fp_bar == 0:
        raise ZeroDivisionError("CB9 average rates must be non-zero")
