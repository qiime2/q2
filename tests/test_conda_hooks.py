import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVATE_HOOK = REPO_ROOT / "hooks" / "00_activate_qiime2_envs.sh"
DEACTIVATE_HOOK = REPO_ROOT / "hooks" / "00_deactivate_qiime2_envs.sh"


def _run_shell(script: str) -> dict[str, str]:
    completed = subprocess.run(
        ["sh", "-c", script],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    result = {}
    for line in completed.stdout.strip().splitlines():
        key, value = line.split("=", 1)
        result[key] = value
    return result


def test_activate_uses_inner_conda_environment_values():
    values = _run_shell(
        f"""
set -eu

export MPLBACKEND='TkAgg'
export R_LIBS_USER='/baseline/lib/R/library/'
export R_HOME='/baseline/lib/R'
export PYTHONNOUSERSITE=0

CONDA_PREFIX='/env/outer' CONDA_SHLVL=1 . "{ACTIVATE_HOOK}"
CONDA_PREFIX='/env/inner' CONDA_SHLVL=2 . "{ACTIVATE_HOOK}"

printf 'MPLBACKEND=%s\\n' "${{MPLBACKEND-__UNSET__}}"
printf 'R_LIBS_USER=%s\\n' "${{R_LIBS_USER-__UNSET__}}"
printf 'R_HOME=%s\\n' "${{R_HOME-__UNSET__}}"
printf 'PYTHONNOUSERSITE=%s\\n' "${{PYTHONNOUSERSITE-__UNSET__}}"
"""
    )

    assert values == {
        "MPLBACKEND": "Agg",
        "R_LIBS_USER": "/env/inner/lib/R/library/",
        "R_HOME": "/env/inner/lib/R",
        "PYTHONNOUSERSITE": "1",
    }


def test_deactivate_restores_outer_then_original_values():
    values = _run_shell(
        f"""
set -eu

export MPLBACKEND='TkAgg'
unset R_LIBS_USER
export R_HOME='/usr/local/lib/R'
unset PYTHONNOUSERSITE

CONDA_PREFIX='/env/outer' CONDA_SHLVL=1 . "{ACTIVATE_HOOK}"
CONDA_PREFIX='/env/inner' CONDA_SHLVL=2 . "{ACTIVATE_HOOK}"

CONDA_SHLVL=2 . "{DEACTIVATE_HOOK}"
printf 'OUTER_MPLBACKEND=%s\\n' "${{MPLBACKEND-__UNSET__}}"
printf 'OUTER_R_LIBS_USER=%s\\n' "${{R_LIBS_USER-__UNSET__}}"
printf 'OUTER_R_HOME=%s\\n' "${{R_HOME-__UNSET__}}"
printf 'OUTER_PYTHONNOUSERSITE=%s\\n' "${{PYTHONNOUSERSITE-__UNSET__}}"

CONDA_SHLVL=1 . "{DEACTIVATE_HOOK}"
printf 'BASE_MPLBACKEND=%s\\n' "${{MPLBACKEND-__UNSET__}}"
printf 'BASE_R_LIBS_USER=%s\\n' "${{R_LIBS_USER-__UNSET__}}"
printf 'BASE_R_HOME=%s\\n' "${{R_HOME-__UNSET__}}"
printf 'BASE_PYTHONNOUSERSITE=%s\\n' "${{PYTHONNOUSERSITE-__UNSET__}}"
"""
    )

    assert values["OUTER_MPLBACKEND"] == "Agg"
    assert values["OUTER_R_LIBS_USER"] == "/env/outer/lib/R/library/"
    assert values["OUTER_R_HOME"] == "/env/outer/lib/R"
    assert values["OUTER_PYTHONNOUSERSITE"] == "1"

    assert values["BASE_MPLBACKEND"] == "TkAgg"
    assert values["BASE_R_LIBS_USER"] == "__UNSET__"
    assert values["BASE_R_HOME"] == "/usr/local/lib/R"
    assert values["BASE_PYTHONNOUSERSITE"] == "__UNSET__"
