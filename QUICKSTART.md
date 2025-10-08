# Quick Start Guide

## Installation with uv

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/zkurtz/stringle.git
cd stringle

# Sync dependencies with uv
uv sync
```

## Installation with pip

```bash
# Clone the repository
git clone https://github.com/zkurtz/stringle.git
cd stringle

# Install in development mode
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Quick Examples

### 1. Basic usage - Replace in a directory

```python
from stringle import replace_in_files

# Simple replacement
stats = replace_in_files(
    'test_dir',
    [('world', 'universe')]
)
print(f"Modified {stats.files_modified} files")
```

### 2. Multiple replacements

```python
from stringle import replace_in_files

stats = replace_in_files(
    'test_dir',
    [('foo', 'FOO'), ('bar', 'BAR'), ('baz', 'BAZ')]
)
```

### 3. Case-insensitive replacement

```python
from stringle import replace_in_files

stats = replace_in_files(
    'test_dir',
    [('hello', 'hi')],
    case_sensitive=False
)
```

### 4. Regex replacement

```python
from stringle import replace_in_files

stats = replace_in_files(
    'test_dir',
    [(r'\$([0-9.]+)', r'£\1')],
    use_regex=True
)
```

### 5. Filter by extension

```python
from stringle import replace_in_files

# Only process Python files
stats = replace_in_files(
    'test_dir',
    [('old_name', 'new_name')],
    include_extensions=['.py', '.pyx']
)
```

### 6. Dry run (preview changes)

```python
from stringle import replace_in_files

stats = replace_in_files(
    'test_dir',
    [('search', 'replace')],
    dry_run=True
)
print(f"Would modify {stats.files_modified} files")
```

### 7. Advanced usage with Replacer class

```python
from stringle import Replacer

replacer = Replacer(
    root_dir='test_dir',
    replacements=[('old', 'new'), ('foo', 'bar')],
    case_sensitive=False,
    use_regex=False,
    include_extensions=['.py', '.txt']
)
stats = replacer.run()

print(f"Modified {stats.files_modified} files")
print(f"Made {stats.total_replacements} replacements")
```

## Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=stringle --cov-report=html

# Or run the demo script
python demo.py
```

## Common Use Cases

### Rename variables across a codebase

```python
from stringle import replace_in_files

stats = replace_in_files(
    'src/',
    [('oldVariable', 'newVariable')],
    include_extensions=['.py', '.js']
)
```

### Update copyright year

```python
from stringle import replace_in_files

stats = replace_in_files(
    '.',
    [('Copyright 2023', 'Copyright 2024')],
    include_extensions=['.py', '.js', '.html']
)
```

### Convert old API calls to new ones

```python
from stringle import replace_in_files

stats = replace_in_files(
    'src/',
    [(r'oldApi\.method', 'newApi.method')],
    use_regex=True,
    include_extensions=['.py']
)
```

### Remove TODO comments

```python
from stringle import replace_in_files

stats = replace_in_files(
    '.',
    [(r'TODO\([^)]+\)', 'DONE')],
    use_regex=True,
    include_extensions=['.py']
)
```

## Tips

1. **Always use dry run first**: Use `dry_run=True` to preview changes before applying them
2. **Be specific with extensions**: Use `include_extensions` to limit which files are processed
3. **Use regex for complex patterns**: Set `use_regex=True` for powerful pattern matching
4. **Ignore build directories**: Common directories like `.git`, `__pycache__`, `node_modules` are automatically ignored
5. **Check the results**: Access `stats.modified_files` to see which files were changed

## Troubleshooting

### Binary files are skipped
Stringle automatically skips binary files. You'll see them in `stats.errors` if any errors occur.

### Permission errors
Make sure you have write permissions for the files you want to modify.

### Regex not working as expected
Remember to escape special characters properly in Python strings. Use raw strings (`r"pattern"`) for regex patterns.
