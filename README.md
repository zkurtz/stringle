# stringle

String wrangling for bulk find-and-replace operations. Example:

```python
from stringle import Directory, Replacer

replacements = [
    ('old_text', 'new_text'),
    ('another_old', 'another_new'),
]
directory = Directory(path='/path/to/directory')
replacer = Replacer(files=directory.selected_files)
replacer(replacements)
```

## Features

- **Recursive directory traversal** - Process entire directory trees with the Directory class
- **Multiple replacements** - Apply many find-and-replace operations in one pass
- **Case sensitivity control** - Case-sensitive or case-insensitive matching
- **Regex support** - Use regular expressions for complex patterns
- **Flexible filtering**:
  - Ignore specific directories (e.g., `.git`, `.venv`, `node_modules`)
  - Ignore specific files
  - Filter by file extension (ignore or include specific extensions)


## Installation

We're [on pypi](https://pypi.org/project/stringle/), so `uv add stringle`.

If working directly on this repo, consider using the [simplest-possible virtual environment](https://gist.github.com/zkurtz/4c61572b03e667a7596a607706463543).
