"""
Helper functions for determining the scoring
"""


def geometric_mean(scores):
    adjusted_scores = [
        max(score, 1e-10) for score in scores
    ]  # Replace zero scores with a small positive value
    product = 1
    for score in adjusted_scores:
        product *= score
    return product ** (1.0 / len(adjusted_scores))
