"""Unit tests for recommendation engine and WOA."""

import numpy as np
import pytest

from app.recommendation.engine import build_diagnosis_payload, compute_severity, DISEASE_CLASSES
from woa.whale_optimization import WhaleOptimizationAlgorithm, default_woa_bounds


def test_all_diseases_have_diagnosis():
    for disease in DISEASE_CLASSES:
        payload = build_diagnosis_payload(disease, 0.8)
        assert payload["disease_name"] == disease
        assert "recommendations" in payload
        assert payload["recommendations"]["fertilizer"]


def test_severity_levels():
    assert compute_severity(0.9, "Anthracnose") == "Severe"
    assert compute_severity(0.7, "Anthracnose") == "Moderate"
    assert compute_severity(0.5, "Anthracnose") == "Mild"
    assert compute_severity(0.9, "Healthy") == "None"


def test_woa_runs_short_optimization():
    bounds = default_woa_bounds()

    def dummy_fitness(x: np.ndarray) -> float:
        return float(np.sum(x ** 2))

    woa = WhaleOptimizationAlgorithm(dim=len(bounds), bounds=bounds, population_size=3, max_iterations=2, seed=1)
    result = woa.optimize(dummy_fitness)
    assert result.best_fitness <= dummy_fitness(woa.positions[0])
    assert len(result.convergence_curve) == 2
