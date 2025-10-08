"""Core search and replace functionality."""

import os
import re
from pathlib import Path
from typing import List, Tuple, Optional, Union, Callable


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
    
    def __init__(
        self,
        root_dir: Union[str, Path],
        replacements: List[Tuple[str, str]],
        case_sensitive: bool = True,
        use_regex: bool = False,
        ignore_dirs: Optional[List[str]] = None,
        ignore_files: Optional[List[str]] = None,
        ignore_extensions: Optional[List[str]] = None,
        include_extensions: Optional[List[str]] = None,
        dry_run: bool = False,
    ):
        self.root_dir = Path(root_dir).resolve()
        self.replacements = replacements
        self.case_sensitive = case_sensitive
        self.use_regex = use_regex
        self.dry_run = dry_run
        
        # Default to ignoring common VCS and build directories
        self.ignore_dirs = ignore_dirs if ignore_dirs is not None else [
            '.git', '.svn', '.hg', '__pycache__', '.pytest_cache',
            'node_modules', '.venv', 'venv', 'build', 'dist', '.eggs'
        ]
        self.ignore_files = ignore_files or []
        self.ignore_extensions = ignore_extensions or []
        self.include_extensions = include_extensions
        
        # Compile regex patterns if needed
        self._compiled_patterns = []
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            for search, replace in replacements:
                self._compiled_patterns.append((re.compile(search, flags), replace))
    
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
    
    def replace_in_content(self, content: str) -> Tuple[str, int]:
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
    
    def process_file(self, file_path: Path) -> Tuple[int, Optional[str]]:
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
    
    def run(self) -> dict:
        """Execute the search and replace operation.
        
        Returns:
            Dictionary with statistics about the operation:
            - files_processed: Number of files processed
            - files_modified: Number of files that had replacements
            - total_replacements: Total number of replacements made
            - errors: List of (file_path, error_message) tuples
        """
        stats = {
            'files_processed': 0,
            'files_modified': 0,
            'total_replacements': 0,
            'errors': [],
            'modified_files': []
        }
        
        for root, dirs, files in os.walk(self.root_dir):
            # Filter directories in-place to prevent descending into ignored dirs
            dirs[:] = [d for d in dirs if self.should_process_dir(Path(root) / d)]
            
            for filename in files:
                file_path = Path(root) / filename
                
                if not self.should_process_file(file_path):
                    continue
                
                stats['files_processed'] += 1
                num_replacements, error = self.process_file(file_path)
                
                if error:
                    stats['errors'].append((str(file_path), error))
                elif num_replacements > 0:
                    stats['files_modified'] += 1
                    stats['total_replacements'] += num_replacements
                    stats['modified_files'].append(str(file_path))
        
        return stats


def replace_in_files(
    root_dir: Union[str, Path],
    replacements: List[Tuple[str, str]],
    **kwargs
) -> dict:
    """Convenience function to perform search and replace operations.
    
    Args:
        root_dir: Root directory to search in
        replacements: List of (search, replace) tuples
        **kwargs: Additional arguments passed to Replacer constructor
        
    Returns:
        Dictionary with operation statistics
        
    Example:
        >>> stats = replace_in_files(
        ...     '/path/to/dir',
        ...     [('old_name', 'new_name'), ('foo', 'bar')],
        ...     case_sensitive=False,
        ...     include_extensions=['.py', '.txt']
        ... )
        >>> print(f"Modified {stats['files_modified']} files")
    """
    replacer = Replacer(root_dir, replacements, **kwargs)
    return replacer.run()
