"""Whale Optimization Algorithm for CNN hyperparameter tuning."""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class WOAResult:
    """Result of a WOA optimization run."""

    best_position: np.ndarray
    best_fitness: float
    best_config: Dict[str, Any]
    convergence_curve: List[float] = field(default_factory=list)
    iteration_times: List[float] = field(default_factory=list)
    all_evaluations: List[Dict[str, Any]] = field(default_factory=list)


class WhaleOptimizationAlgorithm:
    """
    Whale Optimization Algorithm (Mirjalili & Lewis, 2016).

    Optimizes CNN hyperparameters by minimizing validation loss while
    maximizing validation accuracy (combined fitness).
    """

    def __init__(
        self,
        dim: int,
        bounds: List[Tuple[float, float]],
        population_size: int = 5,
        max_iterations: int = 10,
        seed: Optional[int] = 42,
    ) -> None:
        if len(bounds) != dim:
            raise ValueError("bounds length must match dim")
        self.dim = dim
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.rng = random.Random(seed)
        np.random.seed(seed)

        self.positions = self._init_population()
        self.fitness = np.full(population_size, np.inf)
        self.best_position: Optional[np.ndarray] = None
        self.best_fitness: float = np.inf

    def _init_population(self) -> np.ndarray:
        population = np.zeros((self.population_size, self.dim))
        for i in range(self.population_size):
            for j, (low, high) in enumerate(self.bounds):
                population[i, j] = self.rng.uniform(low, high)
        return population

    @staticmethod
    def _clip(position: np.ndarray, bounds: List[Tuple[float, float]]) -> np.ndarray:
        clipped = position.copy()
        for j, (low, high) in enumerate(bounds):
            clipped[j] = np.clip(clipped[j], low, high)
        return clipped

    def optimize(self, fitness_fn: Callable[[np.ndarray], float]) -> WOAResult:
        """
        Run WOA search.

        fitness_fn: lower is better (we use negative val_accuracy + val_loss weight).
        """
        convergence: List[float] = []
        iteration_times: List[float] = []
        evaluations: List[Dict[str, Any]] = []

        for i in range(self.population_size):
            self.fitness[i] = fitness_fn(self.positions[i])
            evaluations.append({"position": self.positions[i].tolist(), "fitness": float(self.fitness[i])})

        best_idx = int(np.argmin(self.fitness))
        self.best_position = self.positions[best_idx].copy()
        self.best_fitness = float(self.fitness[best_idx])

        for t in range(self.max_iterations):
            iter_start = time.time()
            a = 2 - t * (2 / self.max_iterations)

            for i in range(self.population_size):
                r1 = np.random.random(self.dim)
                r2 = np.random.random(self.dim)
                A = 2 * a * r1 - a
                C = 2 * r2
                p = np.random.random()
                l = np.random.uniform(-1, 1)
                b = 1.0

                if p < 0.5:
                    if np.all(np.abs(A) < 1):
                        D = np.abs(C * self.best_position - self.positions[i])
                        new_pos = self.best_position - A * D
                    else:
                        rand_idx = self.rng.randint(0, self.population_size - 1)
                        X_rand = self.positions[rand_idx]
                        D = np.abs(C * X_rand - self.positions[i])
                        new_pos = X_rand - A * D
                else:
                    D = np.abs(self.best_position - self.positions[i])
                    new_pos = D * np.exp(b * l) * np.cos(2 * np.pi * l) + self.best_position

                new_pos = self._clip(new_pos, self.bounds)
                new_fitness = fitness_fn(new_pos)
                evaluations.append({"position": new_pos.tolist(), "fitness": float(new_fitness), "iteration": t})

                if new_fitness < self.fitness[i]:
                    self.positions[i] = new_pos
                    self.fitness[i] = new_fitness

                if new_fitness < self.best_fitness:
                    self.best_fitness = float(new_fitness)
                    self.best_position = new_pos.copy()

            convergence.append(self.best_fitness)
            iteration_times.append(time.time() - iter_start)
            logger.info("WOA iteration %d/%d best fitness=%.4f", t + 1, self.max_iterations, self.best_fitness)

        from app.models.cnn_model import hyperparameter_vector_to_config

        return WOAResult(
            best_position=self.best_position,
            best_fitness=self.best_fitness,
            best_config=hyperparameter_vector_to_config(self.best_position.tolist()),
            convergence_curve=convergence,
            iteration_times=iteration_times,
            all_evaluations=evaluations,
        )


def default_woa_bounds() -> List[Tuple[float, float]]:
    """Search space for CNN hyperparameters."""
    return [
        (1e-4, 0.01),    # learning rate
        (8, 64),         # batch size
        (16, 128),       # filters
        (3, 7),          # kernel size
        (0.1, 0.6),      # dropout
        (32, 512),       # dense units
        (5, 30),         # epochs (for WOA inner training)
        (0, 3.99),       # optimizer index
        (0, 2.99),       # activation index
    ]
