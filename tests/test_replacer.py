"""Tests for the stringle package."""

from pathlib import Path

from stringle import Directory, Replacer


def test_simple_replacement(tmp_path: Path) -> None:
    """Test basic search and replace."""
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello world, world is great!")

    # Perform replacement
    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files)
    replacer([("world", "universe")])

    # Verify
    assert test_file.read_text() == "Hello universe, universe is great!"


def test_multiple_replacements(tmp_path: Path) -> None:
    """Test multiple search and replace patterns."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("foo bar baz")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files)
    replacer([("foo", "FOO"), ("bar", "BAR"), ("baz", "BAZ")])

    assert test_file.read_text() == "FOO BAR BAZ"


def test_case_insensitive(tmp_path: Path) -> None:
    """Test case-insensitive replacement."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello HELLO hello HeLLo")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files, case_sensitive=False)
    replacer([("hello", "hi")])

    assert test_file.read_text() == "hi hi hi hi"


def test_case_sensitive(tmp_path: Path) -> None:
    """Test case-sensitive replacement."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello hello HELLO")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files, case_sensitive=True)
    replacer([("hello", "hi")])

    assert test_file.read_text() == "Hello hi HELLO"


def test_regex_replacement(tmp_path: Path) -> None:
    """Test regex-based replacement."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test123 Test456 Test789")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files, use_regex=True)
    replacer([(r"Test\d+", "Result")])

    assert test_file.read_text() == "Result Result Result"


def test_regex_with_groups(tmp_path: Path) -> None:
    """Test regex replacement with capture groups."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Price: $10.50 and $20.75")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files, use_regex=True)
    replacer([(r"\$(\d+\.\d+)", r"£\1")])

    assert test_file.read_text() == "Price: £10.50 and £20.75"


def test_ignore_dirs(tmp_path: Path) -> None:
    """Test ignoring specific directories."""
    # Create directory structure
    (tmp_path / "include").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / "include" / "test.txt").write_text("foo")
    (tmp_path / ".git" / "test.txt").write_text("foo")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files)
    replacer([("foo", "bar")])

    # Should process file in include but not in .git
    assert (tmp_path / "include" / "test.txt").read_text() == "bar"
    assert (tmp_path / ".git" / "test.txt").read_text() == "foo"


def test_ignore_files(tmp_path: Path) -> None:
    """Test ignoring specific files."""
    (tmp_path / "process.txt").write_text("foo")
    (tmp_path / "ignore.txt").write_text("foo")

    directory = Directory(path=tmp_path, ignore_files=(tmp_path / "ignore.txt",))
    replacer = Replacer(files=directory.selected_files)
    replacer([("foo", "bar")])

    assert (tmp_path / "process.txt").read_text() == "bar"
    assert (tmp_path / "ignore.txt").read_text() == "foo"


def test_ignore_extensions(tmp_path: Path) -> None:
    """Test ignoring files by extension."""
    (tmp_path / "test.txt").write_text("foo")
    (tmp_path / "test.log").write_text("foo")

    directory = Directory(path=tmp_path, ignore_extensions=[".log"])
    replacer = Replacer(files=directory.selected_files)
    replacer([("foo", "bar")])

    assert (tmp_path / "test.txt").read_text() == "bar"
    assert (tmp_path / "test.log").read_text() == "foo"


def test_include_extensions(tmp_path: Path) -> None:
    """Test processing only specific extensions."""
    (tmp_path / "test.py").write_text("foo")
    (tmp_path / "test.txt").write_text("foo")

    directory = Directory(path=tmp_path, include_extensions=[".py"])
    replacer = Replacer(files=directory.selected_files)
    replacer([("foo", "bar")])

    assert (tmp_path / "test.py").read_text() == "bar"
    assert (tmp_path / "test.txt").read_text() == "foo"


def test_recursive_processing(tmp_path: Path) -> None:
    """Test recursive directory processing."""
    # Create nested structure
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "dir2").mkdir()
    (tmp_path / "file1.txt").write_text("foo")
    (tmp_path / "dir1" / "file2.txt").write_text("foo")
    (tmp_path / "dir1" / "dir2" / "file3.txt").write_text("foo")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files)
    replacer([("foo", "bar")])

    assert (tmp_path / "file1.txt").read_text() == "bar"
    assert (tmp_path / "dir1" / "file2.txt").read_text() == "bar"
    assert (tmp_path / "dir1" / "dir2" / "file3.txt").read_text() == "bar"


def test_no_replacements(tmp_path: Path) -> None:
    """Test when no replacements are found."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files)
    replacer([("notfound", "replacement")])

    assert test_file.read_text() == "hello world"


def test_with_include_extensions(tmp_path: Path) -> None:
    """Test with extension filter."""
    (tmp_path / "test.py").write_text("old_name")
    (tmp_path / "test.txt").write_text("old_name")

    directory = Directory(path=tmp_path, include_extensions=[".py"])
    replacer = Replacer(files=directory.selected_files)
    replacer([("old_name", "new_name")])

    assert (tmp_path / "test.py").read_text() == "new_name"
    assert (tmp_path / "test.txt").read_text() == "old_name"


def test_directory_selected_files(tmp_path: Path) -> None:
    """Test Directory.selected_files property."""
    (tmp_path / "file1.txt").write_text("test")
    (tmp_path / "file2.py").write_text("test")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("test")

    directory = Directory(path=tmp_path)
    selected = directory.selected_files

    assert len(selected) == 2
    assert tmp_path / "file1.txt" in selected
    assert tmp_path / "file2.py" in selected
    assert tmp_path / ".git" / "config" not in selected


def test_directory_other_files(tmp_path: Path) -> None:
    """Test Directory.other_files property."""
    (tmp_path / "file1.txt").write_text("test")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("test")

    directory = Directory(path=tmp_path)
    other = directory.other_files

    assert len(other) == 1
    assert tmp_path / ".git" / "config" in other


def test_duplicate_search_terms_different_replacements(tmp_path: Path) -> None:
    """Test that duplicate search terms with different replacements raise ValueError."""
    import pytest

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files)

    # Should raise ValueError for duplicate search terms with different replacements
    with pytest.raises(ValueError, match="Duplicate search term.*hello"):
        replacer([("hello", "hi"), ("hello", "goodbye")])


def test_duplicate_search_terms_same_replacement(tmp_path: Path) -> None:
    """Test that duplicate search terms even with same replacement raise ValueError."""
    import pytest

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files)

    # Should raise ValueError even if the replacement is the same (redundant)
    with pytest.raises(ValueError, match="Duplicate search term.*hello"):
        replacer([("hello", "hi"), ("hello", "hi")])


def test_different_search_terms_same_replacement(tmp_path: Path) -> None:
    """Test that different search terms with same replacement work fine."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files)

    # Should NOT raise ValueError for different search terms with same replacement
    replacer([("hello", "greeting"), ("world", "greeting")])

    assert test_file.read_text() == "greeting greeting"


def test_multiple_duplicate_search_terms(tmp_path: Path) -> None:
    """Test error message with multiple duplicate search terms."""
    import pytest

    test_file = tmp_path / "test.txt"
    test_file.write_text("foo bar baz")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files)

    # Should raise ValueError listing all duplicates
    with pytest.raises(ValueError, match="Duplicate search term.*bar.*foo"):
        replacer([("foo", "a"), ("bar", "b"), ("foo", "c"), ("bar", "d")])
