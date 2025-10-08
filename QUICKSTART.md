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

# Or install in development mode
uv pip install -e .
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

```bash
# Create a test directory
mkdir test_dir
echo "Hello world, world is great!" > test_dir/test.txt

# Run stringle
stringle test_dir "world:universe"

# Check the result
cat test_dir/test.txt
# Output: Hello universe, universe is great!
```

### 2. Multiple replacements

```bash
stringle test_dir "foo:FOO" "bar:BAR" "baz:BAZ"
```

### 3. Case-insensitive replacement

```bash
echo "Hello HELLO hello" > test_dir/test.txt
stringle test_dir "hello:hi" --ignore-case
cat test_dir/test.txt
# Output: hi hi hi
```

### 4. Regex replacement

```bash
echo "Price: $10.50 and $25.99" > test_dir/prices.txt
stringle test_dir '\$([0-9.]+):£\1' --regex
cat test_dir/prices.txt
# Output: Price: £10.50 and £25.99
```

### 5. Filter by extension

```bash
# Only process Python files
stringle test_dir "old_name:new_name" -e .py -e .pyx
```

### 6. Dry run (preview changes)

```bash
stringle test_dir "search:replace" --dry-run -v
```

### 7. Python API usage

```python
from stringle import replace_in_files

# Simple replacement
stats = replace_in_files(
    'test_dir',
    [('old', 'new'), ('foo', 'bar')]
)

print(f"Modified {stats['files_modified']} files")
print(f"Made {stats['total_replacements']} replacements")
```

## Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=stringle --cov-report=html

# Or use the validation script
python validate.py
```

## Common Use Cases

### Rename variables across a codebase

```bash
stringle src/ "oldVariable:newVariable" -e .py -e .js
```

### Update copyright year

```bash
stringle . "Copyright 2023:Copyright 2024" -e .py -e .js -e .html
```

### Convert old API calls to new ones

```bash
stringle src/ "oldApi\\.method:newApi.method" --regex -e .py
```

### Remove TODO comments

```bash
stringle . "TODO\([^)]+\):DONE" --regex -e .py
```

## Tips

1. **Always use dry run first**: Use `--dry-run -v` to preview changes before applying them
2. **Be specific with extensions**: Use `-e` to limit which files are processed
3. **Use regex for complex patterns**: The `--regex` flag enables powerful pattern matching
4. **Ignore build directories**: Common directories like `.git`, `__pycache__`, `node_modules` are automatically ignored
5. **Check the results**: The verbose flag (`-v`) shows which files were modified

## Troubleshooting

### Binary files are skipped
Stringle automatically skips binary files. You'll see them in the error list if verbose mode is enabled.

### Permission errors
Make sure you have write permissions for the files you want to modify.

### Regex not working as expected
Remember to escape special characters. Use `\\` in the shell to represent a single backslash.
