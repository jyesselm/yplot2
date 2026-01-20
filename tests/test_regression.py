"""Tests for regression plot functionality."""

import numpy as np
import pytest
import matplotlib.pyplot as plt

from yplot2.plots.regression import regplot, regplot_density, _compute_linear_regression


class TestComputeLinearRegression:
    """Tests for _compute_linear_regression helper."""

    def test_perfect_positive_correlation(self):
        """Test with perfectly correlated data."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])  # y = 2x
        slope, intercept, r_squared = _compute_linear_regression(x, y)
        assert np.isclose(slope, 2.0)
        assert np.isclose(intercept, 0.0)
        assert np.isclose(r_squared, 1.0)

    def test_perfect_negative_correlation(self):
        """Test with perfectly negative correlated data."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([10, 8, 6, 4, 2])  # y = -2x + 12
        slope, intercept, r_squared = _compute_linear_regression(x, y)
        assert np.isclose(slope, -2.0)
        assert np.isclose(intercept, 12.0)
        assert np.isclose(r_squared, 1.0)

    def test_with_intercept(self):
        """Test with non-zero intercept."""
        x = np.array([0, 1, 2, 3, 4])
        y = np.array([5, 7, 9, 11, 13])  # y = 2x + 5
        slope, intercept, r_squared = _compute_linear_regression(x, y)
        assert np.isclose(slope, 2.0)
        assert np.isclose(intercept, 5.0)
        assert np.isclose(r_squared, 1.0)


class TestRegplot:
    """Tests for regplot function."""

    def test_basic_usage(self):
        """Test basic regplot creates expected output."""
        fig, ax = plt.subplots()
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2.1, 3.9, 6.2, 7.8, 10.1])

        result = regplot(ax, x, y)

        assert "slope" in result
        assert "intercept" in result
        assert "r_squared" in result
        assert "line" in result
        assert "scatter" in result
        assert "text" in result
        assert result["scatter"] is not None
        assert result["text"] is not None
        plt.close(fig)

    def test_hide_scatter(self):
        """Test regplot with scatter hidden."""
        fig, ax = plt.subplots()
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        result = regplot(ax, x, y, show_scatter=False)

        assert result["scatter"] is None
        plt.close(fig)

    def test_hide_r2(self):
        """Test regplot with R-squared hidden."""
        fig, ax = plt.subplots()
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        result = regplot(ax, x, y, show_r2=False)

        assert result["text"] is None
        plt.close(fig)

    def test_custom_r2_position(self):
        """Test regplot with custom R-squared position via r2_args."""
        fig, ax = plt.subplots()
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        result = regplot(ax, x, y, r2_args={"pos": "top right"})

        assert result["text"] is not None
        plt.close(fig)

    def test_custom_r2_precision(self):
        """Test regplot with custom R-squared precision via r2_args."""
        fig, ax = plt.subplots()
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        result = regplot(ax, x, y, r2_args={"precision": 2})

        text_str = result["text"].get_text()
        assert "R²" in text_str
        plt.close(fig)

    def test_error_fewer_than_2_points(self):
        """Test that regplot raises error with fewer than 2 points."""
        fig, ax = plt.subplots()
        x = np.array([1])
        y = np.array([2])

        with pytest.raises(ValueError, match="at least 2 data points"):
            regplot(ax, x, y)
        plt.close(fig)

    def test_error_unsupported_method(self):
        """Test that regplot raises error for unsupported method."""
        fig, ax = plt.subplots()
        x = np.array([1, 2, 3])
        y = np.array([2, 4, 6])

        with pytest.raises(ValueError, match="Unknown method"):
            regplot(ax, x, y, method="polynomial")
        plt.close(fig)

    def test_r2_with_box(self):
        """Test regplot with boxed R-squared text via r2_args."""
        fig, ax = plt.subplots()
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        result = regplot(ax, x, y, r2_args={"box": True})

        assert result["text"] is not None
        plt.close(fig)

    def test_custom_line_args(self):
        """Test regplot with custom line styling via line_args."""
        fig, ax = plt.subplots()
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        result = regplot(
            ax, x, y,
            line_args={"color": "red", "linestyle": "--", "linewidth": 2.0},
        )

        assert result["line"] is not None
        plt.close(fig)

    def test_custom_scatter_args(self):
        """Test regplot with custom scatter styling via scatter_args."""
        fig, ax = plt.subplots()
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        result = regplot(
            ax, x, y,
            scatter_args={"c": "blue", "s": 100, "alpha": 0.5},
        )

        assert result["scatter"] is not None
        plt.close(fig)

    def test_combined_args(self):
        """Test regplot with all *_args specified."""
        fig, ax = plt.subplots()
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        result = regplot(
            ax, x, y,
            line_args={"color": "red"},
            scatter_args={"c": "blue"},
            r2_args={"pos": "top left", "precision": 4},
        )

        assert result["line"] is not None
        assert result["scatter"] is not None
        assert result["text"] is not None
        plt.close(fig)


class TestRegplotDensity:
    """Tests for regplot_density function."""

    def test_basic_usage(self):
        """Test basic regplot_density with density-colored scatter."""
        fig, ax = plt.subplots()
        np.random.seed(42)
        x = np.random.randn(100)
        y = x + np.random.randn(100) * 0.5

        result = regplot_density(ax, x, y)

        assert "slope" in result
        assert "intercept" in result
        assert "r_squared" in result
        assert "scatter" in result
        assert "line" in result
        assert "cbar" in result
        assert result["scatter"] is not None
        assert result["cbar"] is not None
        plt.close(fig)

    def test_custom_bins(self):
        """Test regplot_density with custom bins."""
        fig, ax = plt.subplots()
        np.random.seed(42)
        x = np.random.randn(100)
        y = x + np.random.randn(100) * 0.5

        result = regplot_density(ax, x, y, bins=200)

        assert result["scatter"] is not None
        plt.close(fig)

    def test_hide_r2(self):
        """Test regplot_density with R-squared hidden."""
        fig, ax = plt.subplots()
        np.random.seed(42)
        x = np.random.randn(100)
        y = x + np.random.randn(100) * 0.5

        result = regplot_density(ax, x, y, show_r2=False)

        assert result["text"] is None
        plt.close(fig)

    def test_hide_cbar(self):
        """Test regplot_density with colorbar hidden."""
        fig, ax = plt.subplots()
        np.random.seed(42)
        x = np.random.randn(100)
        y = x + np.random.randn(100) * 0.5

        result = regplot_density(ax, x, y, show_cbar=False)

        assert result["cbar"] is None
        plt.close(fig)

    def test_custom_scatter_args(self):
        """Test regplot_density with custom scatter styling."""
        fig, ax = plt.subplots()
        np.random.seed(42)
        x = np.random.randn(100)
        y = x + np.random.randn(100) * 0.5

        result = regplot_density(
            ax, x, y,
            scatter_args={"cmap": "viridis", "s": 5, "cmap_min": 0.3},
        )

        assert result["scatter"] is not None
        plt.close(fig)

    def test_custom_line_args(self):
        """Test regplot_density with custom line styling."""
        fig, ax = plt.subplots()
        np.random.seed(42)
        x = np.random.randn(100)
        y = x + np.random.randn(100) * 0.5

        result = regplot_density(
            ax, x, y,
            line_args={"color": "red", "linestyle": "-"},
        )

        assert result["line"] is not None
        plt.close(fig)

    def test_custom_cbar_args(self):
        """Test regplot_density with custom colorbar options."""
        fig, ax = plt.subplots()
        np.random.seed(42)
        x = np.random.randn(100)
        y = x + np.random.randn(100) * 0.5

        result = regplot_density(
            ax, x, y,
            cbar_args={"label": "Points"},
        )

        assert result["cbar"] is not None
        plt.close(fig)

    def test_error_fewer_than_2_points(self):
        """Test that regplot_density raises error with fewer than 2 points."""
        fig, ax = plt.subplots()
        x = np.array([1])
        y = np.array([2])

        with pytest.raises(ValueError, match="at least 2 data points"):
            regplot_density(ax, x, y)
        plt.close(fig)
