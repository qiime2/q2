#!/bin/sh

_q2_backup_var() {
    _q2_name="$1"
    _q2_level="${CONDA_SHLVL:-0}"

    eval "_q2_is_set=\${${_q2_name}+x}"
    if [ "${_q2_is_set}" = "x" ]; then
        eval "_q2_value=\${${_q2_name}}"
        eval "_Q2_BACKUP_${_q2_name}_ISSET_${_q2_level}=1"
        eval "_Q2_BACKUP_${_q2_name}_VALUE_${_q2_level}=\"\${_q2_value}\""
    else
        eval "_Q2_BACKUP_${_q2_name}_ISSET_${_q2_level}=0"
        eval "unset _Q2_BACKUP_${_q2_name}_VALUE_${_q2_level}"
    fi
}

_q2_backup_var MPLBACKEND
_q2_backup_var R_LIBS_USER
_q2_backup_var R_HOME
_q2_backup_var PYTHONNOUSERSITE

export MPLBACKEND='Agg'
export R_LIBS_USER="${CONDA_PREFIX}/lib/R/library/"
export R_HOME="${CONDA_PREFIX}/lib/R"
export PYTHONNOUSERSITE=1

unset _q2_backup_var
unset _q2_is_set
unset _q2_level
unset _q2_name
unset _q2_value
