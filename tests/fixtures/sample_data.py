# -*- coding: utf-8 -*-
"""Minimal API payloads that satisfy project JSON schemas."""

from __future__ import annotations

AGENCY_ID = 'b' * 64
AGENT_ID = 'a' * 64
INSTANCE_ID = 'c' * 64
SECTOR_ID = '11111111-1111-4111-8111-111111111111'
TASK_ID = 'task-abc-123'

AUTH_HEADERS = {'authorization': 'Bearer test-token'}

STATS_COUNT_ITEM = {'name': 'example', 'value': 42}
STATS_COUNT_RESPONSE = [STATS_COUNT_ITEM]

PAGINATED_EMPTY = {'total': 0, 'size': 10, 'page': 0, 'collection': []}

AGENTS_PAGE = {
    'total': 1,
    'size': 10,
    'page': 0,
    'collection': [
        {
            'id': AGENT_ID,
            'computerName': 'host01',
            'updatedOn': 1700000000,
            'version': '1.0.0',
            'os': 'Windows 10',
            'ipAddresses': ['10.0.0.1'],
            'tags': [],
            'markedForRemoval': False,
            'mode': 0,
        }
    ],
}

ALERT_ITEM = {
    'id': 'alert-1',
    'createdOn': 1700000000,
    'updatedOn': 1700000001,
    'msg': 'test alert',
    'agent': {'id': 'agent-id-1', 'computerName': 'host01'},
    'vaccine': {'id': 'vac-1', 'name': 'vaccine', 'criticality': 1},
    'agency': {
        'id': AGENCY_ID,
        'name': 'Agency',
        'sector': SECTOR_ID,
        'instanceId': INSTANCE_ID,
    },
    'status': 1,
}

ALERTS_PAGE = {
    'total': 1,
    'size': 10,
    'collection': [ALERT_ITEM],
}

VACCINES_PAGE = {
    'total': 1,
    'size': 10,
    'page': 0,
    'collection': [
        {
            'id': '950b9749-b87f-4997-aed5-99a9f86b856a',
            'expiration': None,
            'updatedOn': 1752127505,
            'name': 'Anubis ransomware',
            'description': 'Vaccine description',
            'type': 'process_monitor',
            'os': '',
            'osFamily': 'windows',
            'visible': True,
            'risk': {'message': '', 'dangerous': False},
            'version': {'dot': '2.6.1'},
            'autorun': False,
            'criticality': 0,
            'category': '',
            'params': [],
            'selects': [],
            'switchers': [],
            'exceptionParams': [],
        }
    ],
}

TAGS_PAGE = {'tags': ['ciberseguridad', 'servidor']}

INSTANCE_RESPONSE = {
    'id': INSTANCE_ID,
    'createdOn': None,
    'updatedOn': None,
    'name': 'Instance',
    'type': 2,
    'manageVaccines': True,
    'server': 'https://microclaudia.example/api',
}

SECTOR_RESPONSE = {
    'id': SECTOR_ID,
    'name': 'Sector',
    'instanceId': INSTANCE_ID,
    'count': 0,
}

GLOBAL_VACCINES_PAGE = VACCINES_PAGE

AGENT_RESPONSE = AGENTS_PAGE['collection'][0]

DEPLOYMENTS_SECTOR_STATS_RESPONSE = STATS_COUNT_RESPONSE

CSV_ROW = (
    'NOMBRE;ORGANISMO;SIST_OPERATIVO;VERSION;ULTIMA_CONEXION;FECHA_ALTA;'
    'TOTAL_VACUNAS_APLICADAS;TOTAL_VACUNAS_PENDIENTES;TOTAL_VACUNAS_ERROR;'
    'IPADDRESS;MACADDRESS;TAGS\n'
    'host01;Org;Windows;1.0;01-06-2024 10:00:00;01-01-2024 10:00:00;'
    '0;0;0;10.0.0.1;aa:bb:cc:dd:ee:ff;tag1\n'
)

TOTAL_STATS = {'agencies': 10, 'agents': 100, 'alerts': 5, 'vaccines': 20}
EVOLUTION_STATS = [
    {
        'updatedOn': 1700000000,
        'agencies': 10,
        'agents': 100,
        'alerts': 5,
        'vaccines': 20,
    }
]

VERSION_RESPONSE = {'version': {'dot': '3.14.2', 'num': 3014002}}

OSES_RESPONSE = {
    'total': 2,
    'size': 2,
    'page': 0,
    'collection': [
        {'name': 'microsoft windows 10'},
        {'name': ' linux'},
    ],
}

USERS_PAGE = {
    'total': 1,
    'size': 50,
    'page': 0,
    'collection': [
        {
            'id': 'user-id-1',
            'username': 'test.user',
            'email': 'test.user@example.com',
            'roles': ['admin'],
        }
    ],
}

USER_ROLES_RESPONSE = [
    {'id': 'admin', 'name': 'Administrator'},
    {'id': 'viewer', 'name': 'Viewer'},
    {'id': 6, 'name': 'Role'},
]

STATS_NEWS_RESPONSE = {
    'total': 1,
    'size': 1,
    'page': 0,
    'collection': [
        {
            'id': '0502c412-05b6-4f87-a3cb-ea883eff897a',
            'createdOn': 1781518441,
            'updatedOn': 1781518441,
            'headline': 'TA505_CLOP Ransomware 1',
            'body': 'Vacuna en espacio Local',
            'readByUser': True,
            'byEmail': False,
        }
    ],
}

AUTH_REFRESH_RESPONSE = {
    'authorization': 'Bearer refreshed-token',
    'refreshToken': 'Bearer refreshed-refresh-token',
}

REFRESH_TOKEN_HEADER = 'Bearer eyJhbGciOiJIUzI1NiJ9.test.refresh.token'

AGENTS_LAST_VERSION_RESPONSE = {'version': '1.2.3'}
