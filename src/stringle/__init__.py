"""stringle - String wrangling for bulk find-and-replace operations."""

from importlib.metadata import version
from stringle.replacer import Replacer, ReplacementStats, replace_in_files

__version__ = version("stringle")
__all__ = ["Replacer", "ReplacementStats", "replace_in_files"]
