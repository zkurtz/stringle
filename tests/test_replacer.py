"""Tests for the stringle package."""

import os
import tempfile
from pathlib import Path
import pytest

from stringle import Replacer, replace_in_files


class TestReplacer:
    """Test the Replacer class."""
    
    def test_simple_replacement(self, tmp_path):
        """Test basic search and replace."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello world, world is great!")
        
        # Perform replacement
        replacer = Replacer(
            tmp_path,
            [("world", "universe")]
        )
        stats = replacer.run()
        
        # Verify
        assert stats['files_processed'] == 1
        assert stats['files_modified'] == 1
        assert stats['total_replacements'] == 2
        assert test_file.read_text() == "Hello universe, universe is great!"
    
    def test_multiple_replacements(self, tmp_path):
        """Test multiple search and replace patterns."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("foo bar baz")
        
        replacer = Replacer(
            tmp_path,
            [("foo", "FOO"), ("bar", "BAR"), ("baz", "BAZ")]
        )
        stats = replacer.run()
        
        assert stats['total_replacements'] == 3
        assert test_file.read_text() == "FOO BAR BAZ"
    
    def test_case_insensitive(self, tmp_path):
        """Test case-insensitive replacement."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello HELLO hello HeLLo")
        
        replacer = Replacer(
            tmp_path,
            [("hello", "hi")],
            case_sensitive=False
        )
        stats = replacer.run()
        
        assert stats['total_replacements'] == 4
        assert test_file.read_text() == "hi hi hi hi"
    
    def test_case_sensitive(self, tmp_path):
        """Test case-sensitive replacement."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello hello HELLO")
        
        replacer = Replacer(
            tmp_path,
            [("hello", "hi")],
            case_sensitive=True
        )
        stats = replacer.run()
        
        assert stats['total_replacements'] == 1
        assert test_file.read_text() == "Hello hi HELLO"
    
    def test_regex_replacement(self, tmp_path):
        """Test regex-based replacement."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test123 Test456 Test789")
        
        replacer = Replacer(
            tmp_path,
            [(r"Test\d+", "Result")],
            use_regex=True
        )
        stats = replacer.run()
        
        assert stats['total_replacements'] == 3
        assert test_file.read_text() == "Result Result Result"
    
    def test_regex_with_groups(self, tmp_path):
        """Test regex replacement with capture groups."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Price: $10.50 and $20.75")
        
        replacer = Replacer(
            tmp_path,
            [(r"\$(\d+\.\d+)", r"£\1")],
            use_regex=True
        )
        stats = replacer.run()
        
        assert stats['total_replacements'] == 2
        assert test_file.read_text() == "Price: £10.50 and £20.75"
    
    def test_ignore_dirs(self, tmp_path):
        """Test ignoring specific directories."""
        # Create directory structure
        (tmp_path / "include").mkdir()
        (tmp_path / ".git").mkdir()
        (tmp_path / "include" / "test.txt").write_text("foo")
        (tmp_path / ".git" / "test.txt").write_text("foo")
        
        replacer = Replacer(
            tmp_path,
            [("foo", "bar")]
        )
        stats = replacer.run()
        
        # Should process file in include but not in .git
        assert stats['files_processed'] == 1
        assert (tmp_path / "include" / "test.txt").read_text() == "bar"
        assert (tmp_path / ".git" / "test.txt").read_text() == "foo"
    
    def test_ignore_files(self, tmp_path):
        """Test ignoring specific files."""
        (tmp_path / "process.txt").write_text("foo")
        (tmp_path / "ignore.txt").write_text("foo")
        
        replacer = Replacer(
            tmp_path,
            [("foo", "bar")],
            ignore_files=["ignore.txt"]
        )
        stats = replacer.run()
        
        assert stats['files_processed'] == 1
        assert (tmp_path / "process.txt").read_text() == "bar"
        assert (tmp_path / "ignore.txt").read_text() == "foo"
    
    def test_ignore_extensions(self, tmp_path):
        """Test ignoring files by extension."""
        (tmp_path / "test.txt").write_text("foo")
        (tmp_path / "test.log").write_text("foo")
        
        replacer = Replacer(
            tmp_path,
            [("foo", "bar")],
            ignore_extensions=[".log"]
        )
        stats = replacer.run()
        
        assert stats['files_processed'] == 1
        assert (tmp_path / "test.txt").read_text() == "bar"
        assert (tmp_path / "test.log").read_text() == "foo"
    
    def test_include_extensions(self, tmp_path):
        """Test processing only specific extensions."""
        (tmp_path / "test.py").write_text("foo")
        (tmp_path / "test.txt").write_text("foo")
        
        replacer = Replacer(
            tmp_path,
            [("foo", "bar")],
            include_extensions=[".py"]
        )
        stats = replacer.run()
        
        assert stats['files_processed'] == 1
        assert (tmp_path / "test.py").read_text() == "bar"
        assert (tmp_path / "test.txt").read_text() == "foo"
    
    def test_dry_run(self, tmp_path):
        """Test dry run mode."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("foo bar")
        
        replacer = Replacer(
            tmp_path,
            [("foo", "baz"), ("bar", "qux")],
            dry_run=True
        )
        stats = replacer.run()
        
        # Stats should show what would be changed
        assert stats['files_modified'] == 1
        assert stats['total_replacements'] == 2
        # But file should be unchanged
        assert test_file.read_text() == "foo bar"
    
    def test_recursive_processing(self, tmp_path):
        """Test recursive directory processing."""
        # Create nested structure
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir1" / "dir2").mkdir()
        (tmp_path / "file1.txt").write_text("foo")
        (tmp_path / "dir1" / "file2.txt").write_text("foo")
        (tmp_path / "dir1" / "dir2" / "file3.txt").write_text("foo")
        
        replacer = Replacer(
            tmp_path,
            [("foo", "bar")]
        )
        stats = replacer.run()
        
        assert stats['files_processed'] == 3
        assert stats['files_modified'] == 3
        assert (tmp_path / "file1.txt").read_text() == "bar"
        assert (tmp_path / "dir1" / "file2.txt").read_text() == "bar"
        assert (tmp_path / "dir1" / "dir2" / "file3.txt").read_text() == "bar"
    
    def test_no_replacements(self, tmp_path):
        """Test when no replacements are found."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        
        replacer = Replacer(
            tmp_path,
            [("notfound", "replacement")]
        )
        stats = replacer.run()
        
        assert stats['files_processed'] == 1
        assert stats['files_modified'] == 0
        assert stats['total_replacements'] == 0
        assert test_file.read_text() == "hello world"


class TestConvenienceFunction:
    """Test the replace_in_files convenience function."""
    
    def test_replace_in_files(self, tmp_path):
        """Test the convenience function."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("foo bar baz")
        
        stats = replace_in_files(
            tmp_path,
            [("foo", "FOO"), ("bar", "BAR")],
            case_sensitive=True
        )
        
        assert stats['files_modified'] == 1
        assert stats['total_replacements'] == 2
        assert test_file.read_text() == "FOO BAR baz"
    
    def test_with_include_extensions(self, tmp_path):
        """Test convenience function with extension filter."""
        (tmp_path / "test.py").write_text("old_name")
        (tmp_path / "test.txt").write_text("old_name")
        
        stats = replace_in_files(
            tmp_path,
            [("old_name", "new_name")],
            include_extensions=[".py"]
        )
        
        assert stats['files_processed'] == 1
        assert (tmp_path / "test.py").read_text() == "new_name"
        assert (tmp_path / "test.txt").read_text() == "old_name"
