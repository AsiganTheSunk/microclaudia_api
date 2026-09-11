#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Note: DataClass Module Imports
from dataclasses import dataclass


@dataclass
class PingData:
    endpoint_address: str
    hostname: str = ''
    ip_address: str = '0.0.0.0'
    packets_sent: int = 0
    packets_received: int = 0
    packets_lost: int = 0
    avg_response_time: int = -1
    min_response_time: int = -1
    max_response_time: int = -1
    reachable: bool = False
    resolved: bool = False

    @property
    def status(self) -> bool:
        # Note: windows ping can exit 0 on 'Destination host unreachable', so parsed counts win when available.
        return self.packets_received > 0 if self.packets_received >= 0 else self.reachable

    @property
    def jitter(self) -> int:
        # Note: response times are parsed from ping output as strings.
        try:
            return int(self.max_response_time) - int(self.min_response_time)
        except (TypeError, ValueError):
            return -1

    @property
    def missing_packets(self):
        return self.packets_received != self.packets_lost
