#!/usr/bin/env python3
# -*- coding: utf-8 -*-


ALERTS_FROM_AGENCY_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {"type": "integer"},
        "size": {"type": "integer"},
        "collection": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "createdOn": {"type": ["integer", "null"]},
                    "updatedOn": {"type": ["integer", "null"]},
                    "msg": {"type": "string"},
                    "agent": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "computerName": {"type": "string"}
                        },
                        "required": ["id", "computerName"]
                    },
                    "vaccine": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "criticality": {"type": "integer"}
                        },
                        "required": ["id", "name", "criticality"]
                    },
                    "agency": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "sector": {"type": "string"},
                            "instanceId": {"type": "string"}
                        },
                        "required": ["id", "name", "sector", "instanceId"]
                    },
                    "status": {"type": "integer"}
                },
                "required": ["id", "createdOn", "updatedOn", "msg", "agent", "vaccine", "agency", "status"]
            }
        }
    }
}

STATS_COUNT_SCHEMA: dict = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "integer"}
        },
        "required": ["name", "value"]
    }
}


AGENTS_FROM_AGENCY_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {
            "type": "integer"
        },
        "size": {
            "type": "integer"
        },
        "collection": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "computerName": {
                        "type": "string"
                    },
                    "updatedOn": {
                        "type": "integer"
                    },
                    "version": {
                        "type": "string"
                    },
                    "os": {
                        "type": "string"
                    },
                    "ipAddresses": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "vaccineInfo": {
                        "type": "object",
                        "properties": {
                            "notAppliedNotRequired": {
                                "type": "integer"
                            },
                            "notAppliedRequired": {
                                "type": "integer"
                            },
                            "appliedNotRequired": {
                                "type": "integer"
                            },
                            "appliedRequired": {
                                "type": "integer"
                            },
                            "pendingNotRequired": {
                                "type": "integer"
                            },
                            "pendingRequired": {
                                "type": "integer"
                            },
                            "appliedWithErrorNotRequired": {
                                "type": "integer"
                            },
                            "appliedWithErrorRequired": {
                                "type": "integer"
                            },
                            "totalApplied": {
                                "type": "integer"
                            },
                            "total": {
                                "type": "integer"
                            }
                        }
                    },
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "markedForRemoval": {
                        "type": "boolean"
                    },
                    "mode": {
                        "type": "integer"
                    }
                },
                "required": [
                    "id",
                    "computerName"
                ]
            }
        },
        "page": {
            "type": "integer"
        }
    },
    "required": [
        "total",
        "size",
        "collection",
        "page"
    ]
}


VACCINES_FROM_AGENCY_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {"type": "integer"},
        "size": {"type": "integer"},
        "page": {"type": "integer"},
        "collection": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                    "type": {"type": ["string", "null"]},
                    "os": {"type": ["string", "null"]},
                    "osFamily": {"type": ["string", "null"]},
                    "expiration": {"type": ["integer", "null"]},
                    "createdOn": {"type": ["integer", "null"]},
                    "updatedOn": {"type": ["integer", "null"]},
                    "visible": {"type": "boolean"},
                    "autorun": {"type": "boolean"},
                    "criticality": {"type": "integer"},
                    "category": {"type": ["string", "null"]},
                    "risk": {
                        "type": "object",
                        "properties": {
                            "message": {"type": ["string", "null"]},
                            "dangerous": {"type": "boolean"},
                        },
                    },
                    "version": {
                        "type": "object",
                        "properties": {
                            "dot": {"type": ["string", "null"]},
                        },
                    },
                    "params": {"type": "array"},
                    "selects": {"type": "array"},
                    "switchers": {"type": "array"},
                    "exceptionParams": {"type": "array"},
                },
                "required": ["id", "name"],
            },
        },
    },
    "required": ["total", "size", "collection"],
}


TAGS_FROM_AGENCY_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "tags": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["tags"]
}


SECTORS_FROM_INSTANCE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {"type": "integer"},
        "size": {"type": "integer"},
        "collection": {
            "type": "array",
            "items": {}
        },
        "page": {"type": "integer"}
    },
    "required": ["total", "size", "collection", "page"]
}


INSTANCES_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {"type": "integer"},
        "size": {"type": "integer"},
        "collection": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "createdOn": {"type": ["integer", "null"]},
                    "updatedOn": {"type": ["integer", "null"]},
                    "name": {"type": "string"},
                    "type": {"type": "integer"},
                    "manageVaccines": {"type": "boolean"},
                    "server": {"type": "string", "format": "uri"}
                },
                "required": ["id", "createdOn", "name", "type", "manageVaccines", "server"]
            }
        },
        "page": {"type": "integer"}
    },
    "required": ["total", "size", "collection", "page"]
}


SECTORS_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {"type": "integer"},
        "size": {"type": "integer"},
        "collection": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "instanceId": {"type": "string"},
                    "count": {"type": "integer"}
                },
                "required": ["id", "name", "instanceId", "count"]
            }
        },
        "page": {"type": "integer"}
    },
    "required": ["total", "size", "collection", "page"]
}


INSTANCES_RESPONSE_SCHEMA: dict = {
    "anyOf": [
        INSTANCES_SCHEMA,
        {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                },
                "required": ["id"],
            },
        },
    ]
}


SECTORS_RESPONSE_SCHEMA: dict = {
    "anyOf": [
        SECTORS_SCHEMA,
        {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                },
                "required": ["id"],
            },
        },
    ]
}


AGENCIES_FROM_SECTOR_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {"type": "integer"},
        "size": {"type": "integer"},
        "page": {"type": "integer"},
        "collection": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "vaccineInfo": {
                        "type": "object",
                        "properties": {
                            "windows": {
                                "type": "object",
                                "properties": {
                                    "notAppliedNotRequired": {"type": "integer"},
                                    "notAppliedRequired": {"type": "integer"},
                                    "applied": {"type": "integer"},
                                    "totalApplied": {"type": "integer"},
                                    "total": {"type": "integer"}
                                }
                            },
                            "linux": {
                                "type": "object",
                                "properties": {
                                    "notAppliedNotRequired": {"type": "integer"},
                                    "notAppliedRequired": {"type": "integer"},
                                    "applied": {"type": "integer"},
                                    "totalApplied": {"type": "integer"},
                                    "total": {"type": "integer"}
                                }
                            }
                        }
                    },
                    "totalComputers": {"type": "integer"},
                    "dates": {
                        "type": "object",
                        "properties": {
                            "expiration": {"type": ["integer", "null"]},
                            "updatedOn": {"type": ["integer", "null"]}
                        }
                    },
                    "relationship": {
                        "type": "object",
                        "properties": {
                            "parentId": {"type": "string"},
                            "parentName": {"type": "string"},
                            "department": {"type": "boolean"},
                            "instanceId": {"type": "string"},
                            "hasChildren": {"type": "boolean"}
                        }
                    },
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "licences": {"type": "integer"},
                            "sectorId": {"type": "string"},
                            "autorun": {"type": "boolean"},
                            "expired": {"type": "boolean"},
                            "receiveUnconnectedAlerts": {"type": "boolean"},
                            "receiveUninstalledAlerts": {"type": "boolean"},
                            "supportEmail": {"type": "string"},
                            "status": {"type": "integer"}
                        }
                    },
                    "instanceInfo": {
                        "type": "object",
                        "properties": {
                            "instanceName": {"type": "string"},
                            "instanceType": {"type": "integer"}
                        }
                    },
                    "agentsConfig": {
                        "type": "object",
                        "properties": {
                            "notifications": {"type": "boolean"},
                            "telemetry": {"type": "boolean"},
                            "version": {"type": "string"}
                        }
                    },
                    "externalConfig": {"type": "array"},
                    "hasLinux": {"type": "boolean"}
                },
                "required": ["id", "name"]
            }
        }
    },
    "required": ["total", "size", "collection", "page"]
}


TOTAL_STATS_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "agencies": {"type": "integer"},
        "alerts": {"type": "integer"},
        "agents": {"type": "integer"},
        "vaccines": {"type": "integer"}
    },
    "required": ["agencies", "alerts", "agents", "vaccines"]
}


TOTAL_STATS_FORM_EVOLUTION_SCHEMA: dict = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "updatedOn": {"type": ["integer", "null"]},
            "agencies": {"type": "integer"},
            "alerts": {"type": "integer"},
            "agents": {"type": "integer"},
            "vaccines": {"type": "integer"}
        },
        "required": ["updatedOn", "agencies", "alerts", "agents", "vaccines"]
    }
}


ALERTS_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {"type": "integer"},
        "size": {"type": "integer"},
        "collection": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "createdOn": {"type": ["integer", "null"]},
                    "updatedOn": {"type": ["integer", "null"]},
                    "msg": {"type": "string"},
                    "agent": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "computerName": {"type": "string"}
                        },
                        "required": ["id", "computerName"]
                    },
                    "vaccine": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "criticality": {"type": "integer"}
                        },
                        "required": ["id", "name", "criticality"]
                    },
                    "agency": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "sector": {"type": "string"},
                            "instanceId": {"type": "string"}
                        },
                        "required": ["id", "name", "sector", "instanceId"]
                    },
                    "status": {"type": "integer"}
                },
                "required": ["id", "createdOn", "updatedOn", "msg", "agent", "vaccine", "agency", "status"]
            }
        }
    }
}


CSV_AGENTS_SCHEMA: dict = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "NOMBRE": {"type": "string"},
            "ORGANISMO": {"type": "string"},
            "SIST_OPERATIVO": {"type": "string"},
            "VERSION": {"type": "string"},
            "ULTIMA_CONEXION": {"type": "string", "format": "date-time"},
            "FECHA_ALTA": {"type": "string", "format": "date-time"},
            "TOTAL_VACUNAS_APLICADAS": {"type": "string"},
            "TOTAL_VACUNAS_PENDIENTES": {"type": "string"},
            "TOTAL_VACUNAS_ERROR": {"type": "string"},
            "IPADDRESS": {
                "anyOf": [
                    {"type": "string"},
                    {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    }
                ]
            },
            "MACADDRESS": {
                "anyOf": [
                    {"type": "string"},
                    {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    }
                ]
            },
            "TAGS": {"type": "string"}
        },
        "required": [
            "NOMBRE",
            "ORGANISMO",
            "SIST_OPERATIVO",
            "VERSION",
            "ULTIMA_CONEXION",
            "FECHA_ALTA",
            "TOTAL_VACUNAS_APLICADAS",
            "TOTAL_VACUNAS_PENDIENTES",
            "TOTAL_VACUNAS_ERROR",
            "IPADDRESS",
            "MACADDRESS",
            "TAGS"
        ]
    }
}


VERSION_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "version": {
            "type": "object",
            "properties": {
                "dot": {"type": "string"},
                "num": {"type": "integer"},
            },
            "required": ["dot", "num"],
        },
    },
    "required": ["version"],
}

OSES_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {"type": "integer"},
        "size": {"type": "integer"},
        "page": {"type": "integer"},
        "collection": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
        },
    },
    "required": ["total", "size", "collection", "page"],
}

USERS_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {"type": "integer"},
        "size": {"type": "integer"},
        "page": {"type": "integer"},
        "collection": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "username": {"type": "string"},
                },
                "required": ["id"],
            },
        },
    },
    "required": ["total", "size", "collection"],
}

USER_ROLES_SCHEMA: dict = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": ["integer", "string"]},
            "name": {"type": "string"},
        },
        "required": ["id"],
    },
}

STATS_NEWS_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {"type": "integer"},
        "size": {"type": "integer"},
        "page": {"type": "integer"},
        "collection": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "createdOn": {"type": ["integer", "null"]},
                    "updatedOn": {"type": ["integer", "null"]},
                    "headline": {"type": "string"},
                    "body": {"type": "string"},
                    "readByUser": {"type": "boolean"},
                    "byEmail": {"type": "boolean"},
                },
                "required": ["id"],
            },
        },
    },
    "required": ["total", "size", "collection", "page"],
}

AUTH_REFRESH_SCHEMA: dict = {
    "type": "object",
}


PREPARE_CSV_TASK_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "task": {"type": "string"},
    },
    "minProperties": 1,
}


AGENTS_LAST_VERSION_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
    },
    "required": ["version"],
}


INSTANCE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "createdOn": {"type": ["integer", "null"]},
        "updatedOn": {"type": ["integer", "null"]},
        "name": {"type": "string"},
        "type": {"type": "integer"},
        "manageVaccines": {"type": "boolean"},
        "server": {"type": "string"},
    },
    "required": ["id", "name", "type", "manageVaccines"],
}


SECTOR_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "instanceId": {"type": "string"},
        "count": {"type": "integer"},
    },
    "required": ["id", "name", "instanceId", "count"],
}


VACCINES_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "total": {"type": "integer"},
        "size": {"type": "integer"},
        "collection": {"type": "array"},
        "page": {"type": "integer"},
    },
    "required": ["total", "size", "collection"],
}


AGENT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "computerName": {"type": "string"},
        "updatedOn": {"type": ["integer", "null"]},
        "version": {"type": "string"},
        "os": {"type": "string"},
        "ipAddresses": {"type": "array"},
        "tags": {"type": "array"},
        "markedForRemoval": {"type": "boolean"},
        "mode": {"type": "integer"},
    },
    "required": ["id"],
}