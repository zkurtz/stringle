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
    replacer = Replacer(files=directory.selected_files, replacements=[("world", "universe")])
    replacer()

    # Verify
    assert test_file.read_text() == "Hello universe, universe is great!"


def test_multiple_replacements(tmp_path: Path) -> None:
    """Test multiple search and replace patterns."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("foo bar baz")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files, replacements=[("foo", "FOO"), ("bar", "BAR"), ("baz", "BAZ")])
    replacer()

    assert test_file.read_text() == "FOO BAR BAZ"


def test_case_insensitive(tmp_path: Path) -> None:
    """Test case-insensitive replacement."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello HELLO hello HeLLo")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files, case_sensitive=False, replacements=[("hello", "hi")])
    replacer()

    assert test_file.read_text() == "hi hi hi hi"


def test_case_sensitive(tmp_path: Path) -> None:
    """Test case-sensitive replacement."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello hello HELLO")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files, case_sensitive=True, replacements=[("hello", "hi")])
    replacer()

    assert test_file.read_text() == "Hello hi HELLO"


def test_regex_replacement(tmp_path: Path) -> None:
    """Test regex-based replacement."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test123 Test456 Test789")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files, use_regex=True, replacements=[(r"Test\d+", "Result")])
    replacer()

    assert test_file.read_text() == "Result Result Result"


def test_regex_with_groups(tmp_path: Path) -> None:
    """Test regex replacement with capture groups."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Price: $10.50 and $20.75")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files, use_regex=True, replacements=[(r"\$(\d+\.\d+)", r"£\1")])
    replacer()

    assert test_file.read_text() == "Price: £10.50 and £20.75"


def test_ignore_dirs(tmp_path: Path) -> None:
    """Test ignoring specific directories."""
    # Create directory structure
    (tmp_path / "include").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / "include" / "test.txt").write_text("foo")
    (tmp_path / ".git" / "test.txt").write_text("foo")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files, replacements=[("foo", "bar")])
    replacer()

    # Should process file in include but not in .git
    assert (tmp_path / "include" / "test.txt").read_text() == "bar"
    assert (tmp_path / ".git" / "test.txt").read_text() == "foo"


def test_ignore_files(tmp_path: Path) -> None:
    """Test ignoring specific files."""
    (tmp_path / "process.txt").write_text("foo")
    (tmp_path / "ignore.txt").write_text("foo")

    directory = Directory(path=tmp_path, ignore_files=(tmp_path / "ignore.txt",))
    replacer = Replacer(files=directory.selected_files, replacements=[("foo", "bar")])
    replacer()

    assert (tmp_path / "process.txt").read_text() == "bar"
    assert (tmp_path / "ignore.txt").read_text() == "foo"


def test_ignore_extensions(tmp_path: Path) -> None:
    """Test ignoring files by extension."""
    (tmp_path / "test.txt").write_text("foo")
    (tmp_path / "test.log").write_text("foo")

    directory = Directory(path=tmp_path, ignore_extensions=[".log"])
    replacer = Replacer(files=directory.selected_files, replacements=[("foo", "bar")])
    replacer()

    assert (tmp_path / "test.txt").read_text() == "bar"
    assert (tmp_path / "test.log").read_text() == "foo"


def test_include_extensions(tmp_path: Path) -> None:
    """Test processing only specific extensions."""
    (tmp_path / "test.py").write_text("foo")
    (tmp_path / "test.txt").write_text("foo")

    directory = Directory(path=tmp_path, include_extensions=[".py"])
    replacer = Replacer(files=directory.selected_files, replacements=[("foo", "bar")])
    replacer()

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
    replacer = Replacer(files=directory.selected_files, replacements=[("foo", "bar")])
    replacer()

    assert (tmp_path / "file1.txt").read_text() == "bar"
    assert (tmp_path / "dir1" / "file2.txt").read_text() == "bar"
    assert (tmp_path / "dir1" / "dir2" / "file3.txt").read_text() == "bar"


def test_no_replacements(tmp_path: Path) -> None:
    """Test when no replacements are found."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    directory = Directory(path=tmp_path)
    replacer = Replacer(files=directory.selected_files, replacements=[("notfound", "replacement")])
    replacer()

    assert test_file.read_text() == "hello world"


def test_with_include_extensions(tmp_path: Path) -> None:
    """Test with extension filter."""
    (tmp_path / "test.py").write_text("old_name")
    (tmp_path / "test.txt").write_text("old_name")

    directory = Directory(path=tmp_path, include_extensions=[".py"])
    replacer = Replacer(files=directory.selected_files, replacements=[("old_name", "new_name")])
    replacer()

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


def test_replacement_sorting_default(tmp_path: Path) -> None:
    """Test that replacements are sorted by length by default (longest first)."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("abcd ab a")

    directory = Directory(path=tmp_path)
    # Providing in reverse order, but should be sorted by length
    replacer = Replacer(files=directory.selected_files, replacements=[("a", "X"), ("ab", "Y"), ("abcd", "Z")])
    replacer()

    # Should replace longest first: abcd->Z, then ab->Y, then a->X
    assert test_file.read_text() == "Z Y X"


def test_replacement_sorting_disabled(tmp_path: Path) -> None:
    """Test that sorting can be disabled with sort=False."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("abcd ab a")

    directory = Directory(path=tmp_path)
    # With sort=False, replacements happen in the order given
    replacer = Replacer(
        files=directory.selected_files, sort=False, replacements=[("a", "X"), ("ab", "Y"), ("abcd", "Z")]
    )
    replacer()

    # Should replace in order: a->X first (replacing all 'a'), then ab, then abcd
    assert test_file.read_text() == "Xbcd Xb X"


def test_ordered_replacements_property(tmp_path: Path) -> None:
    """Test the ordered_replacements cached property."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    directory = Directory(path=tmp_path)
    replacer = Replacer(
        files=directory.selected_files,
        sort=True,
        replacements=[("a", "X"), ("ab", "Y"), ("abcd", "Z")],
    )

    # Should be sorted by length, longest first
    assert replacer.ordered_replacements == [("abcd", "Z"), ("ab", "Y"), ("a", "X")]


def test_ordered_replacements_no_sort(tmp_path: Path) -> None:
    """Test ordered_replacements property with sort=False."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    directory = Directory(path=tmp_path)
    original_list = [("a", "X"), ("ab", "Y"), ("abcd", "Z")]
    replacer = Replacer(
        files=directory.selected_files,
        sort=False,
        replacements=original_list,
    )

    # Should maintain original order when sort=False
    assert replacer.ordered_replacements == original_list


def test_replacement_sorting_with_regex(tmp_path: Path) -> None:
    """Test that sorting works with regex patterns by string length."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("foobar foo f")

    directory = Directory(path=tmp_path)
    # Different length patterns - should be sorted by pattern string length
    replacer = Replacer(
        files=directory.selected_files,
        use_regex=True,
        sort=True,
        replacements=[(r"f", "X"), (r"foo", "Y"), (r"foobar", "Z")],
    )
    replacer()

    # Should replace longest pattern first: foobar->Z, foo->Y, f->X
    assert test_file.read_text() == "Z Y X"


def test_duplicate_search_terms_different_replacements(tmp_path: Path) -> None:
    """Test that duplicate search terms with different replacements raise ValueError."""
    import pytest

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    directory = Directory(path=tmp_path)

    # Should raise ValueError for duplicate search terms with different replacements
    with pytest.raises(ValueError, match="Duplicate search term.*hello"):
        Replacer(files=directory.selected_files, replacements=[("hello", "hi"), ("hello", "goodbye")])


def test_duplicate_search_terms_same_replacement(tmp_path: Path) -> None:
    """Test that duplicate search terms even with same replacement raise ValueError."""
    import pytest

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    directory = Directory(path=tmp_path)

    # Should raise ValueError even if the replacement is the same (redundant)
    with pytest.raises(ValueError, match="Duplicate search term.*hello"):
        Replacer(files=directory.selected_files, replacements=[("hello", "hi"), ("hello", "hi")])


def test_different_search_terms_same_replacement(tmp_path: Path) -> None:
    """Test that different search terms with same replacement work fine."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    directory = Directory(path=tmp_path)

    # Should NOT raise ValueError for different search terms with same replacement
    replacer = Replacer(files=directory.selected_files, replacements=[("hello", "greeting"), ("world", "greeting")])
    replacer()

    assert test_file.read_text() == "greeting greeting"


def test_multiple_duplicate_search_terms(tmp_path: Path) -> None:
    """Test error message with multiple duplicate search terms."""
    import pytest

    test_file = tmp_path / "test.txt"
    test_file.write_text("foo bar baz")

    directory = Directory(path=tmp_path)

    # Should raise ValueError listing all duplicates
    with pytest.raises(ValueError, match="Duplicate search term.*bar.*foo"):
        Replacer(files=directory.selected_files, replacements=[("foo", "a"), ("bar", "b"), ("foo", "c"), ("bar", "d")])
