#!/usr/bin/env -S uv run --script

# /// script
# dependencies = ["nox>=2025.11.12"]
# ///

import nox

# Tags:
#   lint         - lint-only session
#   activation   - conda hook activation/deactivation tests
#   alias-matrix - alias tests across Python versions


# [*((python-version), [*tags])]
MATRIX = [
    ("3.10", ["alias-matrix"]),
    ("3.12", ["alias-matrix"]),
    ("3.14", ["alias-matrix"]),
]


def setup_uv(session: nox.Session) -> None:
    """Sync the project environment with UV dev dependencies."""
    session.run_install(
        "uv",
        "sync",
        "--group=dev",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )


@nox.session(venv_backend="uv", tags=["lint"])
def lint(session: nox.Session) -> None:
    """Run the linters."""
    setup_uv(session)
    session.run("ruff", "check", *session.posargs)


@nox.session(venv_backend="uv", tags=["activation"])
def test_activation(session: nox.Session) -> None:
    """Run the conda activation/deactivation hook tests."""
    setup_uv(session)
    session.run("pytest", "-q", "tests/test_conda_hooks.py")


@nox.session(venv_backend="uv")
@nox.parametrize(
    "python",
    [x[0] for x in MATRIX],
    ids=["py" + x[0] for x in MATRIX],
    tags=[x[1] for x in MATRIX],
)
def test_alias(session: nox.Session) -> None:
    """Run alias compatibility tests across supported Python versions."""
    setup_uv(session)
    session.run("pytest", "-q", "tests/test_alias.py")
