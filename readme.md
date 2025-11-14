## 🛠️ Development Setup

```bash
python -m venv venv
source ./venv/bin/activate # when opening a new terminal
pip install .[dev]         # install development libs (project.optional-dependencies)
pip install -e .           # install euchre library locally (editable install).
```

### Running Tests

```bash
pip install pytest
pytest tests
pytest tests/test_name.py
```

### Running Tests with Coverage

```bash
pip install coverage
coverage run -m pytest tests
coverage report # text view
coverage html # html view
wslview htmlcov/index.html
```

#### Clear Coverage Files
```bash
rm .coverage
rm -r htmlcov
```
### building package
pip install build
python -m build


---

### Helpful Test Flags

```bash
-x    # Exit on first failure
-k    # Run tests that match a keyword expression
-v    # Verbose output
-s    # Print stdout during test runs
```