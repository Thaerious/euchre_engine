## 🛠️ Development Setup

```bash
python -m venv venv
source ./venv/bin/activate # when opening a new terminal
pip install .[dev] # install development libs (project.optional-dependencies)
pip install -e . # install euchre library locally (editable install).

### Running Tests

```bash
pip install pytest
pytest tests
pytest tests/test_name.py
```

### building package
pip install build
python -m build