#!/usr/bin/env python3
"""Validation script to demonstrate stringle functionality."""

import sys
import os

# Add src to path for development install
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from stringle import Replacer, replace_in_files


def main():
    """Run validation checks."""
    print("=" * 60)
    print("Stringle Package Validation")
    print("=" * 60)
    
    # Check imports
    print("\n✓ Package imports successfully")
    print(f"  - Replacer class: {Replacer}")
    print(f"  - replace_in_files function: {replace_in_files}")
    
    # Check basic functionality
    import tempfile
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create test files
        (tmp_path / "test.txt").write_text("foo bar baz")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.txt").write_text("foo bar")
        
        # Test 1: Basic replacement
        print("\n✓ Testing basic replacement...")
        stats = replace_in_files(
            tmp_path,
            [("foo", "FOO"), ("bar", "BAR")]
        )
        assert stats['files_modified'] == 2
        assert stats['total_replacements'] == 4
        print(f"  - Modified {stats['files_modified']} files")
        print(f"  - Made {stats['total_replacements']} replacements")
        
        # Reset files
        (tmp_path / "test.txt").write_text("Hello World")
        
        # Test 2: Case-insensitive
        print("\n✓ Testing case-insensitive mode...")
        stats = replace_in_files(
            tmp_path,
            [("hello", "hi"), ("world", "universe")],
            case_sensitive=False
        )
        assert stats['files_modified'] == 1
        print(f"  - Modified {stats['files_modified']} files")
        
        # Test 3: Regex
        (tmp_path / "regex_test.txt").write_text("Test123 Test456")
        print("\n✓ Testing regex support...")
        stats = replace_in_files(
            tmp_path,
            [(r"Test\d+", "Result")],
            use_regex=True,
            include_extensions=[".txt"]
        )
        assert stats['total_replacements'] >= 2
        print(f"  - Made {stats['total_replacements']} regex replacements")
        
        # Test 4: Dry run
        print("\n✓ Testing dry run mode...")
        (tmp_path / "dryrun.txt").write_text("original")
        stats = replace_in_files(
            tmp_path,
            [("original", "modified")],
            dry_run=True
        )
        content = (tmp_path / "dryrun.txt").read_text()
        assert content == "original", "Dry run should not modify files"
        print(f"  - Dry run correctly preserved original content")
        
        # Test 5: Filtering
        print("\n✓ Testing file filtering...")
        (tmp_path / "include.py").write_text("test")
        (tmp_path / "exclude.txt").write_text("test")
        stats = replace_in_files(
            tmp_path,
            [("test", "replaced")],
            include_extensions=[".py"]
        )
        py_content = (tmp_path / "include.py").read_text()
        txt_content = (tmp_path / "exclude.txt").read_text()
        assert py_content == "replaced"
        assert txt_content == "test"
        print(f"  - Extension filtering works correctly")
    
    print("\n" + "=" * 60)
    print("✅ All validation checks passed!")
    print("=" * 60)
    print("\nThe stringle package is working correctly.")
    print("\nUsage examples:")
    print("  >>> from stringle import replace_in_files")
    print("  >>> stats = replace_in_files('path/to/dir', [('old', 'new')])")
    print("\nFor more details, see README.md")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
