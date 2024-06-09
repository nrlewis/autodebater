"""
Test the math functions
"""

from autodebater.scoring import geometric_mean


def test_geometric_means():
    scores = [70, 50]
    assert 60 > geometric_mean(scores) > 59
