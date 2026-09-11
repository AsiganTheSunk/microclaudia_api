#!/usr/bin/env python
# -*- coding: utf-8 -*-


class PingCountParseError(Exception):
    """Ping packet statistics could not be parsed from command output."""
    pass


class PingResponseTimeParseError(Exception):
    """Ping round-trip times could not be parsed from command output."""
    pass


class PingImplicitAddressParseError(Exception):
    """Ping target IP could not be parsed from command output."""
    pass
