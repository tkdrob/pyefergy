"""Tests for PyEfergy."""
import pathlib

API_KEY = "ur1234567-0abc12de3f456gh7ij89k012"


def load_fixture(filename):
    """Load a fixture."""
    return (
        pathlib.Path(__file__)
        .parent.joinpath("fixtures", filename)
        .read_text(encoding="utf8")
    )
