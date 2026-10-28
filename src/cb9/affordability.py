"""Affordability comparisons as defined in the report's AMI chapter."""

from __future__ import annotations


def affordability_gap(ami_limit: float, median_income: float) -> dict[str, float]:
    """Difference between an AMI income limit and a median household income.

    The report's headline gap subtracts the CB9 median from the family-of-three
    100 percent AMI limit and expresses that difference as a percent of the median.
    """
    if median_income == 0:
        raise ZeroDivisionError("median income must be non-zero")
    gap_dollars = ami_limit - median_income
    return {
        "gap_dollars": gap_dollars,
        "gap_percent_of_median": gap_dollars / median_income * 100,
        "ami_as_multiple_of_median": ami_limit / median_income,
    }


def income_ratio(higher: float, lower: float) -> dict[str, float]:
    """Ratio of two income figures, and the percent increase from the lower one."""
    if lower == 0:
        raise ZeroDivisionError("lower income must be non-zero")
    return {
        "ratio": higher / lower,
        "percent_increase": (higher - lower) / lower * 100,
    }


def share_of_threshold(income: float, threshold: float) -> float:
    """Income as a percent of an AMI income limit."""
    if threshold == 0:
        raise ZeroDivisionError("threshold must be non-zero")
    return income / threshold * 100


def times_as_dense(district_rate: float, reference_rate: float) -> float:
    """How many times the reference rate the district rate is."""
    if reference_rate == 0:
        raise ZeroDivisionError("reference rate must be non-zero")
    return district_rate / reference_rate
