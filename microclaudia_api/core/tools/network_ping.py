#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Note: Platform Module Imports
from platform import system
# Note: Socket Module Imports
from socket import (
    gaierror,
    getaddrinfo
)
# Note: Tools Module Imports
from microclaudia_api.core.tools.ping_data import PingData
from microclaudia_api.core.tools.shell_tools import execute_command
from microclaudia_api.core.tools.ping_exceptions import (
    PingCountParseError,
    PingImplicitAddressParseError,
    PingResponseTimeParseError
)
from microclaudia_api.core.tools.shell_exceptions import ExecuteCommandError


# Note: Hard ceiling for a wedged ping process; the -w flag bounds each packet, not total runtime.
_PING_SUBPROCESS_TIMEOUT_SEC: int = 30


def ping(endpoint_address: str, number_of_packets: int = None,
         timeout: int = None, resolve_address: bool = False, suppress_warnings: bool = True) -> PingData:
    """
    This function, will perform a terminal ping execution. Remember that a host may not respond to a ping (ICMP)
    request even if the host name is valid.
    :param endpoint_address: Hostname or IP address to probe.
    :param number_of_packets: Echo requests to send, defaults to 1.
    :param timeout: Milliseconds to wait per packet, converted to seconds on unix.
    :param resolve_address: Resolve the address to a hostname (windows only).
    :param suppress_warnings: Silence the failure warning.
    :return: PingData; reachability comes from the exit code, the rest is best-effort parsing.
    """
    if endpoint_address == '0.0.0.0' or endpoint_address == 'fec0:0:0:ffff::1':
        return PingData(endpoint_address)

    _is_windows = system().lower() == 'windows'
    command = ['ping', '-n' if _is_windows else '-c', f'{number_of_packets if number_of_packets else 1}']

    if timeout is not None:
        command += ['-w', f'{timeout}' if _is_windows else f'{int(timeout / 1000)}']

    if resolve_address:
        command.append('-a')

    command.append(f'{endpoint_address}')

    # TODO: capture _error to tell 'host is down' from 'not allowed to ask'. ICMP can be blocked outright,
    #  and unix prints 'socket: Operation not permitted' while windows fails differently. That is an
    #  independent signal from DNS resolution and belongs in PingData.
    try:
        out, _error, return_code = execute_command(command, timeout=_PING_SUBPROCESS_TIMEOUT_SEC)
    except ExecuteCommandError as error:
        if not suppress_warnings:
            print(f'[~]( Warning ): Unable to perform NetworkTools.ping({endpoint_address}): {error}')
        return PingData(endpoint_address)

    # Note: the exit code is the answer; everything below only enriches it and must never override it.
    _is_reachable: bool = return_code == 0
    _ping_data = PingData(endpoint_address, reachable=_is_reachable)
    _out = out.splitlines()
    if len(_out) < 2:
        # Note: no preamble means ping never got a target ip; ask the resolver directly to say why.
        _ping_data.resolved = is_resolvable(endpoint_address)
        return _ping_data

    _ping_data.resolved = True
    _ping_data.hostname = _out[1].split(' ')[1].strip() if len(_out[1].split(' ')) > 1 else ''

    try:
        _ping_data.ip_address = get_implicit_address(_out)
    except PingImplicitAddressParseError:
        pass

    try:
        _ping_data.packets_sent, _ping_data.packets_received, _ping_data.packets_lost = get_ping_counts(_out)
    except PingCountParseError:
        _ping_data.packets_sent, _ping_data.packets_received, _ping_data.packets_lost = -1, -1, -1

    try:
        _ping_data.min_response_time, _ping_data.max_response_time, _ping_data.avg_response_time = \
            get_response_times(_out)
    except PingResponseTimeParseError:
        pass

    return _ping_data


def is_resolvable(endpoint_address: str) -> bool:
    """
    This function, will ask the OS resolver whether a name maps to an address, regardless of address family.
    :param endpoint_address: Hostname or IP address to resolve.
    :return: True when the resolver returns at least one address.
    """
    try:
        return bool(getaddrinfo(endpoint_address, None))
    except gaierror:
        return False


# TODO: both output parsers below are windows-only and positional. 'Packets:' never appears on linux,
#  which reports '1 packets transmitted, 1 received, 0% packet loss', and get_response_times still keys
#  off lines[-2]/lines[-1]. Not a regression: on linux the counts fall through to -1 and status correctly
#  defers to the exit code.
def get_ping_counts(lines):
    """
    This function, will scan ping output backwards for the packet statistics line.
    :param lines: Ping stdout, split into lines.
    :return: Tuple of (sent, received, lost).
    :raises PingCountParseError: When no statistics line is present or its values are unreadable.
    """
    for line in reversed(lines):
        if 'Packets:' in line:
            try:
                _counts = line.split(':')[1].split(',')[:3]
                _sent, _received, _lost = (int(_count.split('=')[1].split('(')[0].strip()) for _count in _counts)
                return _sent, _received, _lost
            except (IndexError, ValueError):
                raise PingCountParseError
    raise PingCountParseError


def get_response_times(lines):
    """
    This function, will parse min, max, and average round-trip times from Windows ping output.
    :param lines: Ping stdout, split into lines.
    :return: Tuple of (min, max, avg) response times, or (-1, -1, -1) when the timing block is absent.
    :raises PingResponseTimeParseError: When the timing block is present but unreadable.
    """
    try:
        if 'Approximate round trip times in milli-seconds' in lines[-2]:
            avg_response_time = lines[-1].split(',')[2].strip().split(' ')[2][:-2]
            min_response_time = lines[-1].split(',')[0].strip().split(' ')[2][:-2]
            max_response_time = lines[-1].split(',')[1].strip().split(' ')[2][:-2]
            return min_response_time, max_response_time, avg_response_time
        else:
            return -1, -1, -1
    except Exception:
        raise PingResponseTimeParseError


def get_implicit_address(lines):
    """
    This function, will extract the bracketed IP address from a Windows ping preamble line.
    :param lines: Ping stdout, split into lines.
    :return: IP address string found between '[' and ']'.
    :raises PingImplicitAddressParseError: When the preamble has no bracketed address.
    """
    try:
        return lines[1].split('[')[1].split(']')[0]
    except (IndexError, AttributeError):
        raise PingImplicitAddressParseError
