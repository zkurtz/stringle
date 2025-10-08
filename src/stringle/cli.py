"""Command-line interface for stringle."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple

from stringle import replace_in_files


def parse_replacements(replacement_args: List[str]) -> List[Tuple[str, str]]:
    """Parse replacement arguments in the format 'search:replace'.
    
    Args:
        replacement_args: List of strings in format 'search:replace'
        
    Returns:
        List of (search, replace) tuples
    """
    replacements = []
    for arg in replacement_args:
        if ':' not in arg:
            raise ValueError(f"Invalid replacement format: {arg}. Expected 'search:replace'")
        search, replace = arg.split(':', 1)
        replacements.append((search, replace))
    return replacements


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Stringle - Bulk find and replace in files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic replacement
  stringle /path/to/dir 'old:new'
  
  # Multiple replacements
  stringle /path/to/dir 'foo:bar' 'old:new'
  
  # Case-insensitive with specific extensions
  stringle /path/to/dir 'hello:hi' -i -e .py -e .txt
  
  # Regex replacement with dry run
  stringle /path/to/dir 'Test\\d+:Result' -r --dry-run
  
  # Ignore specific directories
  stringle /path/to/dir 'old:new' --ignore-dir .git --ignore-dir build
"""
    )
    
    parser.add_argument(
        'directory',
        type=Path,
        help='Root directory to search in'
    )
    
    parser.add_argument(
        'replacements',
        nargs='+',
        help='Replacements in format "search:replace"'
    )
    
    parser.add_argument(
        '-i', '--ignore-case',
        action='store_true',
        help='Case-insensitive matching'
    )
    
    parser.add_argument(
        '-r', '--regex',
        action='store_true',
        help='Treat search patterns as regular expressions'
    )
    
    parser.add_argument(
        '-e', '--extension',
        action='append',
        dest='extensions',
        help='Only process files with this extension (can be specified multiple times)'
    )
    
    parser.add_argument(
        '--ignore-dir',
        action='append',
        dest='ignore_dirs',
        help='Ignore this directory (can be specified multiple times)'
    )
    
    parser.add_argument(
        '--ignore-file',
        action='append',
        dest='ignore_files',
        help='Ignore this file (can be specified multiple times)'
    )
    
    parser.add_argument(
        '--ignore-ext',
        action='append',
        dest='ignore_extensions',
        help='Ignore files with this extension (can be specified multiple times)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    
    args = parser.parse_args()
    
    # Validate directory
    if not args.directory.exists():
        print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
        return 1
    
    if not args.directory.is_dir():
        print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
        return 1
    
    # Parse replacements
    try:
        replacements = parse_replacements(args.replacements)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Build kwargs
    kwargs = {
        'case_sensitive': not args.ignore_case,
        'use_regex': args.regex,
        'dry_run': args.dry_run,
    }
    
    if args.extensions:
        kwargs['include_extensions'] = args.extensions
    
    if args.ignore_dirs:
        kwargs['ignore_dirs'] = args.ignore_dirs
    
    if args.ignore_files:
        kwargs['ignore_files'] = args.ignore_files
    
    if args.ignore_extensions:
        kwargs['ignore_extensions'] = args.ignore_extensions
    
    # Run replacement
    try:
        stats = replace_in_files(args.directory, replacements, **kwargs)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    # Output results
    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        mode = "Would process" if args.dry_run else "Processed"
        print(f"{mode} {stats['files_processed']} files")
        print(f"{mode.split()[0]} modified" if args.dry_run else "Modified", 
              f"{stats['files_modified']} files")
        print(f"{mode.split()[0]} make" if args.dry_run else "Made", 
              f"{stats['total_replacements']} replacements")
        
        if args.verbose and stats['modified_files']:
            print("\nModified files:")
            for file_path in stats['modified_files']:
                print(f"  - {file_path}")
        
        if stats['errors']:
            print("\nErrors:")
            for file_path, error in stats['errors']:
                print(f"  - {file_path}: {error}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
