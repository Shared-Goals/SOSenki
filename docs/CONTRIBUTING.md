# Contributor Guide

Thank you for your interest in SOSenki! We welcome contributions from the community.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a branch** for your change: `git checkout -b feature/your-feature`

## Code Requirements

### Backend (Python/FastAPI)

- Follow [PEP 8](https://pep8.org/)
- Use `black` for formatting: `black .`
- Use `flake8` for linting: `flake8 app/`
- Add tests for new features using `pytest`
- Dependency management: use `pyproject.toml` and `uv` (do not use `requirements.txt` for new features)
  - Install `uv` (macOS): `brew install uv`
  - Install development and test dependencies:

      ```bash
      cd SOSenki
      uv sync --group dev
      ```

  - Run tests:

      ```bash
      uv run --group dev python -m pytest backend/tests/ -v
      ```

### Frontend (JavaScript/Vanilla)

- Use `prettier` for formatting: `prettier --write src/`
- Use `eslint` for linting: `eslint src/`
- Minimize dependencies
- Test compatibility with the Telegram Mini App SDK

## Commit Process

- Write clear, descriptive commit messages in English
- One commit = one logical unit of changes
- Example: `git commit -m "feat: add bill calculation service"`

## Submitting a Pull Request

1. Make sure all tests pass
2. Update documentation if needed
3. Describe your changes in the PR clearly and concisely
4. Reference related Issues if any: `Closes #123`

## License

By submitting code, you agree that it will be distributed under the [Apache License 2.0](LICENSE).
This means all your contributions automatically fall under this license.

## Branching and Versioning

- `main` — production-ready code
- `develop` — active development
- We use [Semantic Versioning](https://semver.org/) (v1.0.0)

## Questions and Issues

- Use **GitHub Issues** to report bugs
- Use **Discussions** for questions and suggestions
- Contact the Shared Goals team chat for urgent questions

## Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/).
Any violations should be reported to the team.

---

**Thank you for helping grow SOSenki!** 🌲
