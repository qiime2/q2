#!/bin/sh

_q2_restore_var() {
    _q2_name="$1"
    _q2_level="${CONDA_SHLVL:-0}"

    eval "_q2_is_set=\${_Q2_BACKUP_${_q2_name}_ISSET_${_q2_level}:-}"
    if [ "${_q2_is_set}" = "1" ]; then
        eval "_q2_value=\${_Q2_BACKUP_${_q2_name}_VALUE_${_q2_level}}"
        eval "export ${_q2_name}=\"\${_q2_value}\""
    else
        eval "unset ${_q2_name}"
    fi

    eval "unset _Q2_BACKUP_${_q2_name}_ISSET_${_q2_level}"
    eval "unset _Q2_BACKUP_${_q2_name}_VALUE_${_q2_level}"
}

_q2_restore_var MPLBACKEND
_q2_restore_var R_LIBS_USER
_q2_restore_var R_HOME
_q2_restore_var PYTHONNOUSERSITE

unset _q2_restore_var
unset _q2_is_set
unset _q2_level
unset _q2_name
unset _q2_value
