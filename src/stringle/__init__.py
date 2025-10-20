"""stringle - String wrangling for bulk find-and-replace operations."""

from importlib.metadata import version

from stringle.replacer import Directory, Replacer

__version__ = version("stringle")
__all__ = ["Directory", "Replacer"]
