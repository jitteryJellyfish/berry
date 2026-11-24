# Berry Repository Instructions

Berry is a Python scientific-computing package for extracting and analyzing
Bloch wavefunctions from Quantum ESPRESSO calculations.

## Project layout

- `berry/`: package source and command-line entry points.
- `docs/`: user documentation and installation notes.
- `requirements.txt`: runtime dependency mirror for requirements-file installs.
- `pyproject.toml`: package metadata, uv development dependencies, and tool configuration.

## Development

- Use `uv sync --group dev` to set up the development environment.
- Run `make test` for pytest, `make quality` for Ruff and mypy, and `make build`
  to build distributions.
- Tests belong under `tests/`; the project does not currently have an
  automated test suite.
- Keep runtime dependencies in `pyproject.toml`; synchronize `requirements.txt`
  when changing them.
- Keep changes compatible with the Python versions declared by the package.

## Domain considerations

- Berry relies on Quantum ESPRESSO executables for its DFT workflow; do not
  assume they are installed or invoke computational workflows as part of
  routine validation.
- Do not run external DFT calculations or modify user calculation data unless
  explicitly requested.
- Preserve the existing command-line interface and scientific behavior when
  changing package code.
