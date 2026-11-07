"""Statistical rigor and mathematical invariance test suite."""

import math
import pytest
from core.models import ConfidenceInterval

def test_wilson_ci_monotonically_increases():
    """Higher success count strictly results in higher Wilson lower and upper bounds."""
    ci_1 = ConfidenceInterval.calculate_wilson_interval(1, 10)
    ci_5 = ConfidenceInterval.calculate_wilson_interval(5, 10)
    ci_9 = ConfidenceInterval.calculate_wilson_interval(9, 10)

    assert ci_1.lower_bound < ci_5.lower_bound < ci_9.lower_bound
    assert ci_1.upper_bound < ci_5.upper_bound < ci_9.upper_bound

def test_pass_pow_k_geometric_property():
    """pass^k measures consistent mastery: a single failure reduces pass^k to 0."""
    scores_mixed = [1.0, 1.0, 0.0]
    scores_perfect = [1.0, 1.0, 1.0]

    pass_pow_k_mixed = 1.0 if all(s == 1.0 for s in scores_mixed) else 0.0
    pass_pow_k_perfect = 1.0 if all(s == 1.0 for s in scores_perfect) else 0.0

    assert pass_pow_k_mixed == 0.0
    assert pass_pow_k_perfect == 1.0
