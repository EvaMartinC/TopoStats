"""Testing of grainstats class."""

import logging
from pathlib import Path

import numpy as np
import pytest

from topostats.grainstats import GrainStats
from topostats.logs.logs import LOGGER_NAME

# pylint: disable=protected-access

POINT1 = (0, 0)
POINT2 = (1, 0)
POINT3 = (1, 1)
POINT4 = (0, 1)
EDGES = np.array([POINT1, POINT2, POINT3, POINT4])


def test_get_angle(dummy_grainstats: GrainStats) -> None:
    """Test calculation of angle."""
    angle = dummy_grainstats.get_angle(POINT1, POINT3)
    target = np.arctan2(POINT1[1] - POINT3[1], POINT1[0] - POINT3[0])

    assert isinstance(angle, float)
    assert angle == target


def test_is_clockwise_clockwise(dummy_grainstats: GrainStats) -> None:
    """Test calculation of whether three points make a clockwise turn."""
    clockwise = dummy_grainstats.is_clockwise(POINT3, POINT2, POINT1)

    assert isinstance(clockwise, bool)
    assert clockwise


def test_is_clockwise_anti_clockwise(dummy_grainstats: GrainStats) -> None:
    """Test calculation of whether three points make a clockwise turn."""
    clockwise = dummy_grainstats.is_clockwise(POINT1, POINT2, POINT3)

    assert isinstance(clockwise, bool)
    assert not clockwise


@pytest.mark.parametrize(
    ("method", "grain_mask", "expected_coords"),
    [
        (
            "binary_erosion",
            [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
            ],
            [
                [1, 1],
                [1, 2],
                [1, 3],
                [1, 4],
                [1, 5],
                [1, 6],
                [2, 1],
                [2, 6],
                [3, 1],
                [3, 6],
                [4, 1],
                [4, 6],
                [5, 1],
                [5, 6],
                [6, 1],
                [6, 2],
                [6, 3],
                [6, 4],
                [6, 5],
                [6, 6],
            ],
        ),
        (
            "binary_erosion",
            [
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0],
            ],
            [
                [1, 1],
            ],
        ),
        (
            "binary_erosion",
            [
                [0, 1, 0],
                [1, 0, 1],
                [0, 1, 0],
            ],
            [
                [0, 1],
                [1, 0],
                [1, 2],
                [2, 1],
            ],
        ),
        (
            "binary_erosion",
            [
                [0, 1, 0],
                [1, 1, 1],
                [1, 1, 1],
            ],
            [
                [0, 1],
                [1, 0],
                [1, 2],
                [2, 0],
                [2, 1],
                [2, 2],
            ],
        ),
        (
            "canny",
            [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
            ],
            [
                [1, 1],
                [1, 2],
                [1, 3],
                [1, 4],
                [1, 5],
                [1, 6],
                [2, 1],
                [2, 6],
                [3, 1],
                [3, 6],
                [4, 1],
                [4, 6],
                [5, 1],
                [5, 6],
                [6, 1],
                [6, 2],
                [6, 3],
                [6, 4],
                [6, 5],
                [6, 6],
            ],
        ),
        (
            "canny",
            [
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0],
            ],
            [],
        ),
        (
            "canny",
            [
                [0, 1, 0],
                [1, 0, 1],
                [0, 1, 0],
            ],
            [],
        ),
        (
            "canny",
            [
                [0, 1, 0],
                [1, 1, 1],
                [1, 1, 1],
            ],
            [],
        ),
    ],
)
def test_calculate_edges(dummy_grainstats: GrainStats, method, grain_mask, expected_coords) -> None:
    """Test calculation of edges."""
    edges = dummy_grainstats.calculate_edges(grain_mask, edge_detection_method=method)

    assert isinstance(edges, list)
    np.testing.assert_array_equal(edges, expected_coords)


def test_calculate_centroid(dummy_grainstats: GrainStats) -> None:
    """Test calculation of centroid."""
    centroid = dummy_grainstats._calculate_centroid(EDGES)
    target = (0.5, 0.5)

    assert isinstance(centroid, tuple)
    assert centroid == target


def test_calculate_displacement(dummy_grainstats: GrainStats) -> None:
    """Test calculation of displacement of points from centroid."""
    centroid = dummy_grainstats._calculate_centroid(EDGES)
    displacement = dummy_grainstats._calculate_displacement(EDGES, centroid)

    target = np.array([[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]])

    assert isinstance(displacement, np.ndarray)
    np.testing.assert_array_equal(displacement, target)


def test_calculate_radius(dummy_grainstats: GrainStats) -> None:
    """Calculate the radius of each point from the centroid."""
    centroid = dummy_grainstats._calculate_centroid(EDGES)
    displacement = dummy_grainstats._calculate_displacement(EDGES, centroid)
    radii = dummy_grainstats._calculate_radius(displacement)

    target = np.array([0.7071067811865476, 0.7071067811865476, 0.7071067811865476, 0.7071067811865476])

    assert isinstance(radii, np.ndarray)
    np.testing.assert_array_equal(radii, target)


def test_calculate_squared_distance(dummy_grainstats: GrainStats) -> None:
    """Test the calculation of displacement between two points."""
    displacement_1_2 = dummy_grainstats.calculate_squared_distance(POINT2, POINT1)
    displacement_1_3 = dummy_grainstats.calculate_squared_distance(POINT3, POINT1)
    displacement_2_3 = dummy_grainstats.calculate_squared_distance(POINT3, POINT2)

    target_1_2 = (POINT2[0] - POINT1[0]) ** 2 + (POINT2[1] - POINT1[1]) ** 2
    target_1_3 = (POINT3[0] - POINT1[0]) ** 2 + (POINT3[1] - POINT1[1]) ** 2
    target_2_3 = (POINT2[0] - POINT3[0]) ** 2 + (POINT2[1] - POINT3[1]) ** 2

    assert isinstance(displacement_1_2, float)
    assert displacement_1_2 == target_1_2
    assert isinstance(displacement_1_3, float)
    assert displacement_1_3 == target_1_3
    assert isinstance(displacement_2_3, float)
    assert displacement_2_3 == target_2_3


def test_no_grains(caplog, tmp_path: Path) -> None:
    """Test GrainStats raises error when passed zero grains."""
    caplog.set_level(logging.DEBUG, logger=LOGGER_NAME)
    grainstats = GrainStats(
        grain_crops={},
        image_name="random",
        direction="above",
        base_output_dir=tmp_path,
    )
    grainstats.calculate_stats()

    assert "No grain crops for this image, grain statistics can not be calculated." in caplog.text


@pytest.mark.parametrize(
    ("coords", "shape", "expected"),
    [(np.asarray([5, 5]), 10, 0), (np.asarray([-3, 12]), 10, 3), (np.asarray([-3, 14]), 10, -4)],
)
def test_get_shift(coords, shape, expected):
    """Tests the Grainstats.get_shift function against known expected outcomes."""
    assert GrainStats.get_shift(coords, shape) == expected


@pytest.mark.parametrize(
    ("length", "centre", "img_len", "expected"),
    [
        (5, np.asarray([10, 10]), 21, [5, 5]),
        (3, np.asarray([1, 20]), 21, [1, 6]),
        (8, np.asarray([18, 6]), 21, [14, 6]),
    ],
)
def test_get_cropped_region(dummy_grainstats: GrainStats, length, centre, img_len, expected):
    """Tests the Grainstats.get_cropped_region function's shape and center position are correct."""
    rng = np.random.default_rng()
    image = rng.random((img_len, img_len))
    image[centre[0], centre[1]] = 5
    output = dummy_grainstats.get_cropped_region(image, length, centre)
    assert output.shape == (2 * length + 1, 2 * length + 1)
    assert output[expected[0], expected[1]] == 5
