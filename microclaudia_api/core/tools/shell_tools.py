#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Note: Typing Module Imports
from typing import (
    Tuple, List
)
# Note: Subprocess Module Imports
from subprocess import (
    PIPE, Popen, TimeoutExpired
)
# Note: Shell Exceptions Module Imports
from microclaudia_api.core.tools.shell_exceptions import ExecuteCommandError


def execute_command(command: List[str] | str, shell: bool = False, timeout: int | None = None) -> Tuple[str, str, int]:
    """
    This function, will run a command and capture its output.
    :param command: Command argv list, or a single string when shell is True.
    :param shell: Run the command through the system shell.
    :param timeout: Seconds to wait before killing the process.
    :return: Tuple of (stdout, stderr, return code); return code is -1 when the process timed out.
    :raises ExecuteCommandError: When the process cannot be launched.
    """
    try:
        system_subprocess = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=shell)
    except Exception as error:
        raise ExecuteCommandError(command, error) from error

    try:
        _out, _error = system_subprocess.communicate(timeout=timeout)
    except TimeoutExpired:
        system_subprocess.kill()
        _out, _error = system_subprocess.communicate()
        return _out, _error, -1
    return _out, _error, system_subprocess.returncode
