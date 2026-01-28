# Contributing to CAE Digital Twin Platform

Thank you for your interest in contributing to the CAE Digital Twin Platform! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Docker Desktop
- Python 3.10+
- Git
- Basic knowledge of:
  - Python
  - Docker
  - Celery
  - Streamlit

### Setting Up Development Environment

1. **Fork and clone the repository**

```bash
git clone https://github.com/your-username/cadquery-agent-sandbox.git
cd cadquery-agent-sandbox
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Start development services**

```bash
cd docker
docker-compose up -d
```

5. **Verify setup**

```bash
# Run tests
pytest

# Check dashboard
streamlit run dashboard/app.py
```

## 📋 Development Workflow

### 1. Create a Branch

Create a new branch for your feature or bugfix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number
```

### 2. Make Changes

- Write clean, readable code
- Follow the coding standards below
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_specific.py
```

### 4. Code Quality Checks

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy server/

# Run security scan
trivy fs .
```

### 5. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add new mesh generation algorithm"
```

Follow the conventional commits format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Go to GitHub and create a Pull Request with:
- Clear title and description
- Reference related issues
- Include screenshots for UI changes
- List any breaking changes

## 🎨 Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions short and focused
- Use meaningful variable names

```python
from typing import List, Optional

def generate_mesh(
    geometry_file: str,
    mesh_size: float,
    algorithm: str = "delaunay"
) -> Optional[str]:
    """
    Generate a mesh from geometry file.

    Args:
        geometry_file: Path to the geometry file
        mesh_size: Target mesh size
        algorithm: Mesh generation algorithm

    Returns:
        Path to the generated mesh file, or None if failed
    """
    # Implementation
    pass
```

### Code Organization

```
project/
├── module_name/
│   ├── __init__.py
│   ├── main.py           # Main functionality
│   ├── utils.py          # Utility functions
│   └── constants.py      # Constants
├── tests/
│   ├── test_main.py
│   └── test_utils.py
└── README.md
```

### Error Handling

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data: dict) -> bool:
    try:
        # Process data
        return True
    except ValueError as e:
        logger.error(f"Invalid data: {e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise
```

## 🧪 Testing Guidelines

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

def test_mesh_generation():
    # Arrange
    geometry = create_test_geometry()
    expected_elements = 1000

    # Act
    mesh = generate_mesh(geometry)

    # Assert
    assert mesh is not None
    assert len(mesh.elements) == expected_elements
```

### Test Coverage

- Aim for >80% code coverage
- Test edge cases and error conditions
- Mock external dependencies
- Keep tests independent and fast

## 📚 Documentation

### Inline Documentation

```python
def calculate_stress(mesh: Mesh, forces: List[Force]) -> Dict[str, float]:
    """
    Calculate stress distribution on mesh.

    Uses finite element method to compute stress at each node.

    Args:
        mesh: Finite element mesh
        forces: Applied forces on the mesh

    Returns:
        Dictionary mapping node IDs to stress values

    Example:
        >>> mesh = create_mesh()
        >>> forces = [Force(node=0, value=1000)]
        >>> stress = calculate_stress(mesh, forces)
        >>> print(stress[0])
        45.2
    """
    # Implementation
```

### Documentation Updates

When adding new features:
1. Update README.md
2. Add examples to USER_GUIDE.md
3. Update API documentation
4. Add inline code comments

## 🐛 Bug Reporting

When reporting bugs, include:

1. **Description**
   - Clear description of the issue
   - Steps to reproduce
   - Expected vs actual behavior

2. **Environment**
   - OS and version
   - Docker version
   - Python version
   - Browser version (for UI issues)

3. **Logs**
   - Relevant error messages
   - Stack traces
   - Configuration files

4. **Screenshots/Videos**
   - Visual evidence of the issue

## 💡 Feature Requests

Before requesting a feature:

1. Check existing issues and PRs
2. Consider if it fits the project scope
3. Think about implementation complexity
4. Propose a solution approach

When creating a feature request, include:

1. **Problem Statement**
   - What problem does this solve?
   - Who will benefit?

2. **Proposed Solution**
   - Detailed description
   - Potential implementation approach

3. **Alternatives**
   - Other approaches considered
   - Why this solution is better

4. **Additional Context**
   - Examples or mockups
   - Similar features in other projects

## 🤝 Code Review

### For Contributors

- Respond to review comments promptly
- Make requested changes
- Ask questions if anything is unclear
- Keep discussion constructive

### For Reviewers

- Be respectful and constructive
- Focus on the code, not the person
- Explain your reasoning
- Suggest improvements, not just problems

## 🏷️ Labeling and Milestones

### Issue Labels

- `bug` - Bug reports
- `enhancement` - Feature requests
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Need help
- `priority: high` - High priority
- `priority: medium` - Medium priority
- `priority: low` - Low priority

### Pull Request Labels

- `needs-review` - Needs review
- `changes-requested` - Changes needed
- `approved` - Approved
- `work-in-progress` - WIP

## 📅 Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Tag release
4. Create GitHub release
5. Deploy to production

## 🎓 Getting Help

- Read documentation: README.md, USER_GUIDE.md
- Check existing issues
- Join our community chat (optional)
- Contact maintainers

## ⚖️ Code of Conduct

Be respectful, inclusive, and professional. Treat others as you would want to be treated.

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Gracefully accept constructive criticism
- Focus on what is best for the community

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🙌
