"""Core search and replace functionality."""

import os
import re
from pathlib import Path

import attrs


@attrs.frozen
class ReplacementStats:
    """Statistics about a replacement operation.
    
    Attributes:
        files_processed: Number of files processed
        files_modified: Number of files that had replacements
        total_replacements: Total number of replacements made
        errors: List of (file_path, error_message) tuples
        modified_files: List of file paths that were modified
    """
    files_processed: int
    files_modified: int
    total_replacements: int
    errors: list[tuple[str, str]]
    modified_files: list[str]


@attrs.frozen
class Replacer:
    """A class for performing bulk search and replace operations across files.
    
    Args:
        root_dir: Root directory to search in
        replacements: List of (search, replace) tuples
        case_sensitive: Whether to perform case-sensitive matching (default: True)
        use_regex: Whether to treat search patterns as regular expressions (default: False)
        ignore_dirs: List of directory names to ignore (default: common VCS dirs)
        ignore_files: List of file names to ignore
        ignore_extensions: List of file extensions to ignore (e.g., ['.pyc', '.exe'])
        include_extensions: If provided, only process files with these extensions
        dry_run: If True, report what would be changed without making changes (default: False)
    """
    
    root_dir: Path = attrs.field(converter=lambda x: Path(x).resolve())
    replacements: list[tuple[str, str]]
    case_sensitive: bool = True
    use_regex: bool = False
    ignore_dirs: list[str] = attrs.field(factory=lambda: [
        '.git', '.svn', '.hg', '__pycache__', '.pytest_cache',
        'node_modules', '.venv', 'venv', 'build', 'dist', '.eggs'
    ])
    ignore_files: list[str] = attrs.field(factory=list)
    ignore_extensions: list[str] = attrs.field(factory=list)
    include_extensions: list[str] | None = None
    dry_run: bool = False
    _compiled_patterns: list[tuple[re.Pattern, str]] = attrs.field(init=False, repr=False)
    
    def __attrs_post_init__(self):
        """Compile regex patterns if needed."""
        compiled = []
        if self.use_regex:
            flags = 0 if self.case_sensitive else re.IGNORECASE
            for search, replace in self.replacements:
                compiled.append((re.compile(search, flags), replace))
        object.__setattr__(self, '_compiled_patterns', compiled)
    
    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed based on filters.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be processed, False otherwise
        """
        # Check if file is in ignored files list
        if file_path.name in self.ignore_files:
            return False
        
        # Check file extension
        if self.ignore_extensions and file_path.suffix in self.ignore_extensions:
            return False
        
        if self.include_extensions and file_path.suffix not in self.include_extensions:
            return False
        
        return True
    
    def should_process_dir(self, dir_path: Path) -> bool:
        """Determine if a directory should be processed.
        
        Args:
            dir_path: Path to the directory
            
        Returns:
            True if the directory should be processed, False otherwise
        """
        return dir_path.name not in self.ignore_dirs
    
    def replace_in_content(self, content: str) -> tuple[str, int]:
        """Perform replacements in content string.
        
        Args:
            content: The content to perform replacements in
            
        Returns:
            Tuple of (modified content, number of replacements made)
        """
        modified = content
        total_replacements = 0
        
        if self.use_regex:
            for pattern, replacement in self._compiled_patterns:
                modified, count = pattern.subn(replacement, modified)
                total_replacements += count
        else:
            for search, replace in self.replacements:
                if self.case_sensitive:
                    count = modified.count(search)
                    modified = modified.replace(search, replace)
                else:
                    # Case-insensitive replacement
                    pattern = re.compile(re.escape(search), re.IGNORECASE)
                    modified, count = pattern.subn(replace, modified)
                total_replacements += count
        
        return modified, total_replacements
    
    def process_file(self, file_path: Path) -> tuple[int, str | None]:
        """Process a single file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Tuple of (number of replacements, error message if any)
        """
        try:
            # Try to read as text file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError) as e:
            return 0, f"Skipped (cannot read): {e}"
        
        modified_content, num_replacements = self.replace_in_content(content)
        
        if num_replacements > 0 and not self.dry_run:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            except Exception as e:
                return 0, f"Error writing file: {e}"
        
        return num_replacements, None
    
    def run(self) -> ReplacementStats:
        """Execute the search and replace operation.
        
        Returns:
            ReplacementStats object with statistics about the operation
        """
        files_processed = 0
        files_modified = 0
        total_replacements = 0
        errors = []
        modified_files = []
        
        for root, dirs, files in os.walk(self.root_dir):
            # Filter directories in-place to prevent descending into ignored dirs
            dirs[:] = [d for d in dirs if self.should_process_dir(Path(root) / d)]
            
            for filename in files:
                file_path = Path(root) / filename
                
                if not self.should_process_file(file_path):
                    continue
                
                files_processed += 1
                num_replacements, error = self.process_file(file_path)
                
                if error:
                    errors.append((str(file_path), error))
                elif num_replacements > 0:
                    files_modified += 1
                    total_replacements += num_replacements
                    modified_files.append(str(file_path))
        
        return ReplacementStats(
            files_processed=files_processed,
            files_modified=files_modified,
            total_replacements=total_replacements,
            errors=errors,
            modified_files=modified_files,
        )


def replace_in_files(
    root_dir: str | Path,
    replacements: list[tuple[str, str]],
    **kwargs
) -> ReplacementStats:
    """Convenience function to perform search and replace operations.
    
    Args:
        root_dir: Root directory to search in
        replacements: List of (search, replace) tuples
        **kwargs: Additional arguments passed to Replacer constructor
        
    Returns:
        ReplacementStats object with operation statistics
        
    Example:
        >>> stats = replace_in_files(
        ...     '/path/to/dir',
        ...     [('old_name', 'new_name'), ('foo', 'bar')],
        ...     case_sensitive=False,
        ...     include_extensions=['.py', '.txt']
        ... )
        >>> print(f"Modified {stats.files_modified} files")
    """
    replacer = Replacer(root_dir, replacements, **kwargs)
    return replacer.run()
