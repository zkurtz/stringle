"""Core search and replace functionality."""

import logging
import os
import re
from functools import cached_property
from pathlib import Path

import attrs
from tqdm import tqdm

logger = logging.getLogger(__name__)


@attrs.frozen(kw_only=True)
class Directory:
    """A class for discovering and filtering files in a directory.

    Args:
        path: Root directory to search in
        ignore_dirs: List of directory names to ignore (default: common VCS dirs)
        ignore_files: List of full file paths to ignore
        ignore_extensions: List of file extensions to ignore (e.g., ['.pyc', '.exe'])
        include_extensions: If provided, only process files with these extensions

    Example:
        >>> dir_spec = Directory(path='/path/to/directory')
        >>> files = dir_spec.selected_files
    """

    path: Path = attrs.field(converter=lambda x: Path(x).resolve())
    ignore_dirs: tuple[str, ...] = attrs.field(
        default=(
            ".git",
            ".svn",
            ".hg",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            "build",
            "dist",
            ".eggs",
        ),
        converter=tuple,
    )
    ignore_files: tuple[Path, ...] = attrs.field(default=())
    ignore_extensions: tuple[str, ...] = attrs.field(default=(), converter=tuple)
    include_extensions: tuple[str, ...] | None = attrs.field(
        default=None,
        converter=lambda x: tuple(x) if x is not None else None,
    )

    def _should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed based on filters.

        Args:
            file_path: Path to the file

        Returns:
            True if the file should be processed, False otherwise
        """
        # Check if file is in ignored files list (using full paths)
        if file_path in self.ignore_files:
            return False

        # Check file extension
        if self.ignore_extensions and file_path.suffix in self.ignore_extensions:
            return False

        if self.include_extensions and file_path.suffix not in self.include_extensions:
            return False

        return True

    @cached_property
    def selected_files(self) -> list[Path]:
        """Get list of files to process based on filters.

        Returns:
            List of full paths to files that should be processed
        """
        selected = []
        for root, dirs, files in os.walk(self.path):
            # Filter directories in-place to prevent descending into ignored dirs
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]

            for filename in files:
                file_path = (Path(root) / filename).resolve()
                if self._should_process_file(file_path):
                    selected.append(file_path)

        return selected

    @cached_property
    def other_files(self) -> list[Path]:
        """Get list of files that are filtered out.

        Returns:
            List of full paths to files that are not selected for processing
        """
        all_files = []
        for root, dirs, files in os.walk(self.path):
            # Don't filter directories here - we want to see all files
            for filename in files:
                file_path = (Path(root) / filename).resolve()
                all_files.append(file_path)

        selected_set = set(self.selected_files)
        return [f for f in all_files if f not in selected_set]


@attrs.define(kw_only=True)
class Replacer:
    """A class for performing bulk search and replace operations across files.

    Args:
        files: List of file paths to process
        case_sensitive: Whether to perform case-sensitive matching (default: True)
        use_regex: Whether to treat search patterns as regular expressions (default: False)

    Example:
        >>> directory = Directory(path='/path/to/directory')
        >>> replacer = Replacer(files=directory.selected_files)
        >>> replacer([('old_text', 'new_text'), ('another_old', 'another_new')])
    """

    files: list[Path]
    case_sensitive: bool = True
    use_regex: bool = False

    def _replace_in_content(
        self,
        content: str,
        *,
        replacements: list[tuple[str, str]],
        compiled_patterns: list[tuple[re.Pattern, str]],
    ) -> str:
        """Perform replacements in content string.

        Args:
            content: The content to perform replacements in
            replacements: List of (search, replace) tuples
            compiled_patterns: Compiled regex patterns (if use_regex is True)

        Returns:
            Modified content string
        """
        modified = content

        if self.use_regex:
            for pattern, replacement in compiled_patterns:
                modified = pattern.sub(replacement, modified)
        else:
            for search, replace in replacements:
                if self.case_sensitive:
                    modified = modified.replace(search, replace)
                else:
                    # Case-insensitive replacement
                    pattern = re.compile(re.escape(search), re.IGNORECASE)
                    modified = pattern.sub(replace, modified)

        return modified

    def _process_file(
        self,
        file_path: Path,
        *,
        replacements: list[tuple[str, str]],
        compiled_patterns: list[tuple[re.Pattern, str]],
    ) -> int:
        """Process a single file.

        Args:
            file_path: Path to the file to process
            replacements: List of (search, replace) tuples
            compiled_patterns: Compiled regex patterns (if use_regex is True)

        Returns:
            1 if file was modified, 0 otherwise
        """
        content = file_path.read_text(encoding="utf-8")

        modified_content = self._replace_in_content(
            content,
            replacements=replacements,
            compiled_patterns=compiled_patterns,
        )

        if modified_content != content:
            file_path.write_text(modified_content, encoding="utf-8")
            return 1

        return 0

    def __call__(self, replacements: list[tuple[str, str]]) -> None:
        """Execute the search and replace operation.

        Args:
            replacements: List of (search, replace) tuples
        """
        # Compile regex patterns if needed
        compiled_patterns = []
        if self.use_regex:
            flags = 0 if self.case_sensitive else re.IGNORECASE
            for search, replace in replacements:
                compiled_patterns.append((re.compile(search, flags), replace))

        logger.info(f"Processing {len(self.files)} files with {len(replacements)} replacement(s)")

        files_modified = 0

        iterator = tqdm(self.files, desc="Processing files")

        for file_path in iterator:
            files_modified += self._process_file(
                file_path,
                replacements=replacements,
                compiled_patterns=compiled_patterns,
            )

        logger.info(f"Modified {files_modified} file(s)")
