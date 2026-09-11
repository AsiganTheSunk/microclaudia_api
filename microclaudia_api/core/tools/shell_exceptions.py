#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ExecuteCommandError(Exception):
    """A shell command could not be launched."""

    def __init__(self, command, error: Exception):
        """
        This function, will build an error for a command that failed to start.
        :param command: Command that could not be launched.
        :param error: Underlying exception raised by the process launcher.
        """
        self.command = command
        self.error = error
        super().__init__(f'Unable to execute {command!r}: {error}')
