"""Expose the To Deck skill's colocated regression suite to root discovery."""

from pathlib import Path
import sys


SKILL_TESTS = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "communication"
    / "to-deck"
    / "tests"
)
sys.path.insert(0, str(SKILL_TESTS))

from test_component_selection import *  # noqa: F401,F403,E402
