"""
Helper functions for determining the scoring
"""

import numpy as np


def geometric_mean(scores):
    adjusted_scores = [
        max(score, 1e-10) for score in scores
    ]  # Replace zero scores with a small positive value
    return np.prod(adjusted_scores) ** (1.0 / len(adjusted_scores))
