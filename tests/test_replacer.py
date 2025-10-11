"""Tests for the stringle package."""

from pathlib import Path

from stringle import Replacer


def test_simple_replacement(tmp_path: Path) -> None:
    """Test basic search and replace."""
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello world, world is great!")

    # Perform replacement
    replacer = Replacer(directory=tmp_path)
    stats = replacer([("world", "universe")])

    # Verify
    assert stats.files_processed == 1
    assert stats.files_modified == 1
    assert stats.total_replacements == 2
    assert test_file.read_text() == "Hello universe, universe is great!"


def test_multiple_replacements(tmp_path: Path) -> None:
    """Test multiple search and replace patterns."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("foo bar baz")

    replacer = Replacer(directory=tmp_path)
    stats = replacer([("foo", "FOO"), ("bar", "BAR"), ("baz", "BAZ")])

    assert stats.total_replacements == 3
    assert test_file.read_text() == "FOO BAR BAZ"


def test_case_insensitive(tmp_path: Path) -> None:
    """Test case-insensitive replacement."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello HELLO hello HeLLo")

    replacer = Replacer(directory=tmp_path, case_sensitive=False)
    stats = replacer([("hello", "hi")])

    assert stats.total_replacements == 4
    assert test_file.read_text() == "hi hi hi hi"


def test_case_sensitive(tmp_path: Path) -> None:
    """Test case-sensitive replacement."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello hello HELLO")

    replacer = Replacer(directory=tmp_path, case_sensitive=True)
    stats = replacer([("hello", "hi")])

    assert stats.total_replacements == 1
    assert test_file.read_text() == "Hello hi HELLO"


def test_regex_replacement(tmp_path: Path) -> None:
    """Test regex-based replacement."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test123 Test456 Test789")

    replacer = Replacer(directory=tmp_path, use_regex=True)
    stats = replacer([(r"Test\d+", "Result")])

    assert stats.total_replacements == 3
    assert test_file.read_text() == "Result Result Result"


def test_regex_with_groups(tmp_path: Path) -> None:
    """Test regex replacement with capture groups."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Price: $10.50 and $20.75")

    replacer = Replacer(directory=tmp_path, use_regex=True)
    stats = replacer([(r"\$(\d+\.\d+)", r"£\1")])

    assert stats.total_replacements == 2
    assert test_file.read_text() == "Price: £10.50 and £20.75"


def test_ignore_dirs(tmp_path: Path) -> None:
    """Test ignoring specific directories."""
    # Create directory structure
    (tmp_path / "include").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / "include" / "test.txt").write_text("foo")
    (tmp_path / ".git" / "test.txt").write_text("foo")

    replacer = Replacer(directory=tmp_path)
    stats = replacer([("foo", "bar")])

    # Should process file in include but not in .git
    assert stats.files_processed == 1
    assert (tmp_path / "include" / "test.txt").read_text() == "bar"
    assert (tmp_path / ".git" / "test.txt").read_text() == "foo"


def test_ignore_files(tmp_path: Path) -> None:
    """Test ignoring specific files."""
    (tmp_path / "process.txt").write_text("foo")
    (tmp_path / "ignore.txt").write_text("foo")

    replacer = Replacer(directory=tmp_path, ignore_files=["ignore.txt"])
    stats = replacer([("foo", "bar")])

    assert stats.files_processed == 1
    assert (tmp_path / "process.txt").read_text() == "bar"
    assert (tmp_path / "ignore.txt").read_text() == "foo"


def test_ignore_extensions(tmp_path: Path) -> None:
    """Test ignoring files by extension."""
    (tmp_path / "test.txt").write_text("foo")
    (tmp_path / "test.log").write_text("foo")

    replacer = Replacer(directory=tmp_path, ignore_extensions=[".log"])
    stats = replacer([("foo", "bar")])

    assert stats.files_processed == 1
    assert (tmp_path / "test.txt").read_text() == "bar"
    assert (tmp_path / "test.log").read_text() == "foo"


def test_include_extensions(tmp_path: Path) -> None:
    """Test processing only specific extensions."""
    (tmp_path / "test.py").write_text("foo")
    (tmp_path / "test.txt").write_text("foo")

    replacer = Replacer(directory=tmp_path, include_extensions=[".py"])
    stats = replacer([("foo", "bar")])

    assert stats.files_processed == 1
    assert (tmp_path / "test.py").read_text() == "bar"
    assert (tmp_path / "test.txt").read_text() == "foo"


def test_dry_run(tmp_path: Path) -> None:
    """Test dry run mode."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("foo bar")

    replacer = Replacer(directory=tmp_path, dry_run=True)
    stats = replacer([("foo", "baz"), ("bar", "qux")])

    # Stats should show what would be changed
    assert stats.files_modified == 1
    assert stats.total_replacements == 2
    # But file should be unchanged
    assert test_file.read_text() == "foo bar"


def test_recursive_processing(tmp_path: Path) -> None:
    """Test recursive directory processing."""
    # Create nested structure
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "dir2").mkdir()
    (tmp_path / "file1.txt").write_text("foo")
    (tmp_path / "dir1" / "file2.txt").write_text("foo")
    (tmp_path / "dir1" / "dir2" / "file3.txt").write_text("foo")

    replacer = Replacer(directory=tmp_path)
    stats = replacer([("foo", "bar")])

    assert stats.files_processed == 3
    assert stats.files_modified == 3
    assert (tmp_path / "file1.txt").read_text() == "bar"
    assert (tmp_path / "dir1" / "file2.txt").read_text() == "bar"
    assert (tmp_path / "dir1" / "dir2" / "file3.txt").read_text() == "bar"


def test_no_replacements(tmp_path: Path) -> None:
    """Test when no replacements are found."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    replacer = Replacer(directory=tmp_path)
    stats = replacer([("notfound", "replacement")])

    assert stats.files_processed == 1
    assert stats.files_modified == 0
    assert stats.total_replacements == 0
    assert test_file.read_text() == "hello world"


def test_with_include_extensions(tmp_path: Path) -> None:
    """Test with extension filter."""
    (tmp_path / "test.py").write_text("old_name")
    (tmp_path / "test.txt").write_text("old_name")

    replacer = Replacer(directory=tmp_path, include_extensions=[".py"])
    stats = replacer([("old_name", "new_name")])

    assert stats.files_processed == 1
    assert (tmp_path / "test.py").read_text() == "new_name"
    assert (tmp_path / "test.txt").read_text() == "old_name"
