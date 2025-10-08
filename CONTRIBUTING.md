# Contributing to Stringle

Thank you for your interest in contributing to Stringle!

## Development Setup

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/zkurtz/stringle.git
cd stringle

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/zkurtz/stringle.git
cd stringle

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=stringle --cov-report=html

# Run specific test file
pytest tests/test_replacer.py

# Run specific test
pytest tests/test_replacer.py::TestReplacer::test_simple_replacement

# Run validation script
python validate.py
```

## Code Structure

```
stringle/
├── src/stringle/
│   ├── __init__.py      # Package exports
│   ├── replacer.py      # Core replacement logic
│   └── cli.py           # Command-line interface
├── tests/
│   ├── __init__.py
│   └── test_replacer.py # Unit tests
├── pyproject.toml       # Package configuration
├── README.md            # User documentation
├── QUICKSTART.md        # Quick start guide
└── validate.py          # Manual validation script
```

## Making Changes

1. **Fork the repository** and clone your fork
2. **Create a new branch** for your feature or bug fix
3. **Make your changes** with clear, focused commits
4. **Add tests** for any new functionality
5. **Run the test suite** to ensure nothing is broken
6. **Update documentation** if needed
7. **Submit a pull request** with a clear description

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write clear docstrings for public APIs
- Keep functions focused and reasonably sized
- Add comments for complex logic

## Testing Guidelines

- Write tests for new features
- Ensure tests are independent and can run in any order
- Use descriptive test names that explain what is being tested
- Test edge cases and error conditions
- Aim for high test coverage

## Adding New Features

When adding new features:

1. **Discuss first**: Open an issue to discuss the feature before implementing
2. **Keep it focused**: Each PR should address a single feature or bug
3. **Update docs**: Add examples to README.md or QUICKSTART.md
4. **Add tests**: Ensure the new feature is well-tested
5. **Update CLI**: If the feature should be accessible via CLI, update cli.py

## Bug Reports

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any error messages or stack traces

## Feature Requests

When requesting features:

- Describe the use case
- Explain why it would be useful
- Suggest a possible implementation approach
- Consider backward compatibility

## Questions?

If you have questions, feel free to:

- Open an issue for discussion
- Check existing issues and documentation
- Review the code and tests for examples

## License

By contributing to Stringle, you agree that your contributions will be licensed under the MIT License.
