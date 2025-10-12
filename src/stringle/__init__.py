"""stringle - String wrangling for bulk find-and-replace operations."""

from importlib.metadata import version

from stringle.replacer import Replacer, Stats

__version__ = version("stringle")
__all__ = ["Replacer", "Stats"]
