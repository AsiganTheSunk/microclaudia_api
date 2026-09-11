#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ExecuteCommandError(Exception):
    """A shell command could not be launched."""

    def __init__(self, command, error: Exception):
        self.command = command
        self.error = error
        super().__init__(f'Unable to execute {command!r}: {error}')
