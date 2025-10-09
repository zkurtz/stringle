# stringle

String wrangling for bulk find-and-replace operations

## Installation

```bash
uv sync
```

## Usage

### Basic Example

```python
from stringle import replace_in_files

# Simple replacement
stats = replace_in_files(
    '/path/to/directory',
    [('old_text', 'new_text')]
)

print(f"Modified {stats.files_modified} files")
print(f"Made {stats.total_replacements} replacements")
```

### Advanced Usage

```python
from stringle import Replacer

# Create a replacer with advanced options
replacer = Replacer(
    root_dir='/path/to/directory',
    replacements=[
        ('old_name', 'new_name'),
        ('foo', 'bar'),
    ],
    case_sensitive=False,           # Case-insensitive matching
    use_regex=False,                # Use regex patterns
    ignore_dirs=['.git', 'build'],  # Skip these directories
    ignore_files=['config.local'],  # Skip these files
    ignore_extensions=['.pyc'],     # Skip these extensions
    include_extensions=['.py', '.txt'],  # Only process these extensions
    dry_run=True                    # Preview changes without applying
)

# Run the replacement
stats = replacer.run()

# Check results
for file_path in stats.modified_files:
    print(f"Modified: {file_path}")

if stats.errors:
    print("Errors encountered:")
    for path, error in stats.errors:
        print(f"  {path}: {error}")
```

### Regex Examples

```python
from stringle import replace_in_files

# Replace with regex patterns
stats = replace_in_files(
    '/path/to/directory',
    [
        (r'TODO\(\w+\)', 'DONE'),           # Replace TODO(username)
        (r'\$(\d+\.\d+)', r'£\1'),          # Convert $ to £
        (r'class (\w+):', r'class New\1:'), # Prefix class names
    ],
    use_regex=True,
    include_extensions=['.py']
)
```

## Features

- **Recursive directory traversal** - Process entire directory trees
- **Multiple replacements** - Apply many find-and-replace operations in one pass
- **Case sensitivity control** - Case-sensitive or case-insensitive matching
- **Regex support** - Use regular expressions for complex patterns
- **Flexible filtering**:
  - Ignore specific directories (e.g., `.git`, `node_modules`)
  - Ignore specific files
  - Filter by file extension
- **Dry run mode** - Preview changes before applying them
- **Detailed statistics** - Get reports on files processed and modified

## Use Cases

- Rename variables or functions across a codebase
- Update package names or imports
- Standardize formatting or conventions
- Bulk update copyright notices or documentation
- Convert between different coding styles or patterns

## Development

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=stringle --cov-report=html
```

## License

MIT License - see LICENSE file for details
