
"""Demo of stringle functionality.

This script creates a test directory structure and demonstrates all features.
"""

import tempfile
from pathlib import Path

from stringle import Replacer


def setup_test_files(base_dir):
    """Create a test directory structure with various files."""
    base = Path(base_dir)
    
    # Create directory structure
    (base / "src").mkdir()
    (base / "src" / "utils").mkdir()
    (base / "tests").mkdir()
    (base / ".git").mkdir()
    (base / "build").mkdir()
    
    # Create Python files
    (base / "src" / "main.py").write_text("""
def old_function():
    \"\"\"This is the old function.\"\"\"
    print("Hello World")
    return old_variable

def another_old_function():
    return OLD_CONSTANT
""")
    
    (base / "src" / "utils" / "helpers.py").write_text("""
class OldClass:
    def old_method(self):
        pass

old_var = "old_value"
""")
    
    # Create test files
    (base / "tests" / "test_main.py").write_text("""
def test_old_function():
    result = old_function()
    assert result == old_variable
""")
    
    # Create documentation
    (base / "README.md").write_text("""
# Old Project

This project uses old_function and old_variable.

## Old API

The old API is deprecated.
""")
    
    # Create config files
    (base / "config.json").write_text('{"old_setting": "old_value"}')
    
    # Create files that should be ignored
    (base / ".git" / "config").write_text("old_function")
    (base / "build" / "output.txt").write_text("old_function")
    
    print(f"Created test structure in {base}")
    return base


def demo_basic_replacement(base_dir):
    """Demo 1: Basic replacement."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Replacement")
    print("="*70)
    
    print("\nReplacing 'old_function' with 'new_function' in all files...")
    replacer = Replacer(directory=base_dir, dry_run=False)
    stats = replacer([("old_function", "new_function")])
    
    print(f"✓ Processed {stats.files_processed} files")
    print(f"✓ Modified {stats.files_modified} files")
    print(f"✓ Made {stats.total_replacements} replacements")
    
    # Show a sample file
    sample_file = Path(base_dir) / "src" / "main.py"
    print(f"\nSample modified file ({sample_file.name}):")
    print("-" * 70)
    print(sample_file.read_text()[:200] + "...")


def demo_case_insensitive(base_dir):
    """Demo 2: Case-insensitive replacement."""
    print("\n" + "="*70)
    print("DEMO 2: Case-Insensitive Replacement")
    print("="*70)
    
    print("\nReplacing 'old' with 'new' (case-insensitive) in all files...")
    replacer = Replacer(directory=base_dir, case_sensitive=False)
    stats = replacer([("old", "new")])
    
    print(f"✓ Processed {stats.files_processed} files")
    print(f"✓ Modified {stats.files_modified} files")
    print(f"✓ Made {stats.total_replacements} replacements")


def demo_regex(base_dir):
    """Demo 3: Regex replacement."""
    print("\n" + "="*70)
    print("DEMO 3: Regex Replacement")
    print("="*70)
    
    # Add some test content
    test_file = Path(base_dir) / "src" / "data.txt"
    test_file.write_text("Price: $10.50 and $25.99 total $36.49")
    
    print("\nConverting dollar amounts to pounds using regex...")
    replacer = Replacer(directory=base_dir, use_regex=True, include_extensions=[".txt"])
    stats = replacer([(r'\$(\d+\.\d+)', r'£\1')])
    
    print(f"✓ Modified {stats.files_modified} files")
    print(f"✓ Made {stats.total_replacements} replacements")
    print(f"\nResult: {test_file.read_text()}")


def demo_filtering(base_dir):
    """Demo 4: File filtering."""
    print("\n" + "="*70)
    print("DEMO 4: File Filtering")
    print("="*70)
    
    # Reset a file
    py_file = Path(base_dir) / "src" / "main.py"
    md_file = Path(base_dir) / "README.md"
    
    py_file.write_text("TEST_CONSTANT = 'value'")
    md_file.write_text("TEST_CONSTANT should not change")
    
    print("\nReplacing 'TEST_CONSTANT' only in Python files...")
    replacer = Replacer(directory=base_dir, include_extensions=[".py"])
    stats = replacer([("TEST_CONSTANT", "PRODUCTION_CONSTANT")])
    
    print(f"✓ Processed {stats.files_processed} files")
    print(f"✓ Modified {stats.files_modified} files")
    print(f"\nPython file now contains: {py_file.read_text()}")
    print(f"Markdown file unchanged: {md_file.read_text()}")


def demo_dry_run(base_dir):
    """Demo 5: Dry run mode."""
    print("\n" + "="*70)
    print("DEMO 5: Dry Run Mode")
    print("="*70)
    
    test_file = Path(base_dir) / "src" / "main.py"
    original = test_file.read_text()
    
    print("\nDry run: Would replace 'value' with 'data'...")
    replacer = Replacer(directory=base_dir, dry_run=True)
    stats = replacer([("value", "data")])
    
    print(f"✓ Would process {stats.files_processed} files")
    print(f"✓ Would modify {stats.files_modified} files")
    print(f"✓ Would make {stats.total_replacements} replacements")
    
    after = test_file.read_text()
    print(f"\n✓ File unchanged: {original == after}")


def demo_ignore_dirs():
    """Demo 6: Ignoring directories."""
    print("\n" + "="*70)
    print("DEMO 6: Ignoring Directories")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / "src").mkdir()
        (base / ".git").mkdir()
        (base / "build").mkdir()
        
        (base / "src" / "file.txt").write_text("test")
        (base / ".git" / "file.txt").write_text("test")
        (base / "build" / "file.txt").write_text("test")
        
        print("\nReplacing 'test' with 'replaced'...")
        print("(Default ignores: .git, build, __pycache__, etc.)")
        
        replacer = Replacer(directory=base)
        stats = replacer([("test", "replaced")])
        
        print(f"✓ Processed {stats.files_processed} file(s)")
        print(f"✓ .git/ and build/ were automatically ignored")
        print(f"\nFiles in src/: {(base / 'src' / 'file.txt').read_text()}")
        print(f"Files in .git/: {(base / '.git' / 'file.txt').read_text()}")
        print(f"Files in build/: {(base / 'build' / 'file.txt').read_text()}")


def main():
    """Run all demos."""
    print("╔" + "="*68 + "╗")
    print("║" + " " * 15 + "STRINGLE COMPREHENSIVE DEMO" + " " * 24 + "║")
    print("╚" + "="*68 + "╝")
    
    # Create temporary directory for demos
    with tempfile.TemporaryDirectory() as tmp_dir:
        base_dir = setup_test_files(tmp_dir)
        
        demo_basic_replacement(base_dir)
        demo_case_insensitive(base_dir)
        demo_regex(base_dir)
        demo_filtering(base_dir)
        demo_dry_run(base_dir)
    
    # This demo needs its own temp dir
    demo_ignore_dirs()
    
    print("\n" + "="*70)
    print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nStringle is ready to use!")
    print("\nTry it yourself:")
    print("  from stringle import Replacer")
    print("  replacer = Replacer(directory='/path/to/dir')")
    print("  stats = replacer([('old', 'new')])")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
