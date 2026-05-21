"""Tests for hotspot clustering sizing rules."""

from app.ml.hotspot_cluster import _k_for_sample_size


def test_k_requires_at_least_three_samples():
    assert _k_for_sample_size(0) == 0
    assert _k_for_sample_size(2) == 0
    assert _k_for_sample_size(3) == 3


def test_k_caps_at_five():
    assert _k_for_sample_size(32) == 3
    assert _k_for_sample_size(50) == 5
    assert _k_for_sample_size(120) == 5
