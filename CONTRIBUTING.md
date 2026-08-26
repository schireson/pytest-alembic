# Contributing

The full guide lives in the documentation:
**[Contributing](https://pytest-alembic.readthedocs.io/en/latest/contributing.html)**
(source: [`docs/source/contributing.rst`](docs/source/contributing.rst)). This file is
the short version, because GitHub shows it when you open an issue or a pull request and
the rendered page is a click away at that moment.

## What you need

- [uv](https://docs.astral.sh/uv/), which manages the environment and the lockfile.
- **Docker**, running. The test suite provisions a real postgres through
  [pytest-mock-resources](https://github.com/schireson/pytest-mock-resources); without
  it a large part of the suite cannot run.

## Getting set up

```bash
make install                 # sync the package and its dev dependencies
uvx pre-commit install       # run the linters on `git commit` (optional, recommended)
```

`make help` lists every target. The ones that gate a pull request:

| Command | Checks |
| --- | --- |
| `make lint` | ruff (lint + format) and mypy |
| `make test` | the suite, with a **100%** coverage floor |
| `make docs-coverage` | docstring coverage, floor **100%** |
| `make docs` | the sphinx build, at zero warnings (`-W`) |
| `make audit` / `make audit-all` | known vulnerabilities |

CI runs all of them, so running `make lint` and `make test` before pushing is the
fastest way to a green pull request. `make format` applies what `make lint` only
reports.

## A note on the three 100% floors

Coverage, docstring coverage and type annotations are each held at 100% rather than at
a threshold below the measured value. That is deliberate: a floor beneath the real
number lets a new untested line, undocumented symbol or unannotated function hide in
the slack. It does mean a new function needs a test, a docstring and annotations in the
same change — which is the point, not an accident.

## Commits

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/);
`CHANGELOG.md` is generated from them with [convco](https://convco.github.io/). Mark a
breaking change with `!` (`chore!: …`), since that is what decides the next version.
