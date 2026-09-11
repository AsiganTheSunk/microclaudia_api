# microclaudia_api

Python client for the MicroClaudia HTTP API (`microclaudia.ccn-cert.cni.es`).

## Usage

### Install / import

```bash
pip install -r requirements.txt      # runtime dependencies
pip install -r requirements-dev.txt  # adds pytest and pytest-mock for the test suite
```

```python
from microclaudia_api.core.microclaudia_api import MicroClaudiaAPI
```

### Authenticate

```python
api = MicroClaudiaAPI(username, password)
# stores Bearer + refresh tokens; raises MicroClaudiaAuthError on failure

api.health_status()          # ping + HTTP check → bool
api.auth_refresh()           # refresh session tokens
api.login(username, password)  # re-authenticate explicitly
```

### Typical discovery flow

```python
# 1) agency-scoped data
agency_id = "..."  # hex agency id

agents = api.get_agents_from_agency(
    agency_id, size=50, page=0,
    sort_by="version", order_by="asc",
    filter_by="osFamily:windows",  # optional defaultFilter
)
alerts = api.get_alerts_from_agency(agency_id, size=50, page=0, filter_by="status:1")
vaccines = api.get_vaccines_from_agency(agency_id, size=50, page=0)
tags = api.get_tags_from_agency(agency_id)  # {"tags": [...]}

# 2) discover hierarchy from an alert (or from get_sectors when allowed)
item = alerts["collection"][0]
instance_id = item["agency"]["instanceId"]
sector_id = item["agency"]["sector"]

api.get_instance(instance_id)
api.get_sector(sector_id)
api.get_sectors_from_instance(instance_id, size=100, page=0)
api.get_agencies_from_instance(instance_id, size=200)
api.get_agencies_from_sector(sector_id, size=100, page=0)
```

### Agents

```python
# one page
page = api.get_agents_from_agency(agency_id, size=500, page=0)

# merge pages (TTY shows progress; use max_pages for smoke runs)
all_agents = api.get_all_agents_from_agency(
    agency_id, size=500, max_pages=1, delay=0,
)

agent = api.get_agent(agent_id)
api.get_agents_last_version()
```

### Stats (`groupBy`)

Prefer named helpers for readability; they call shared `get_stats`:

```python
# agency-scoped
api.get_os_agents_stats_from_agency(agency_id, size=10, page=0)
api.get_version_agents_stats_from_agency(agency_id)
api.get_status_agents_stats_from_agency(agency_id)
api.get_computer_stats_from_alerts(agency_id)
api.get_vaccine_stats_from_alerts(agency_id)

# same endpoints via helper
api.get_stats("agents", "os", agency_id=agency_id, size=10, page=0)
api.get_stats("alerts", "computer", agency_id=agency_id)

# global
api.get_os_stats_from_agents()
api.get_versions_stats_from_agents()
api.get_status_stats_from_agents()
api.get_stats("agents", "version")  # global when agency_id omitted

api.get_deployments_sector_stats(size=5)
api.get_total_stats()
api.get_total_stats_evolution(evolution_id=7)
api.get_stats_news()
```

### Alerts & CSV export

```python
api.get_alerts(size=50, page=0, filter_by="status:1")
api.get_alerts_from_agency(agency_id, filter_by="status:0")

# UI-equivalent Alertas.csv export (polls /api/tasks)
api.export_alerts_csv(output_path="Alertas.csv", max_retries=30, pooling_interval=5)
```

### Tags (mutating)

`get_tags_from_agency` returns `{"tags": [...]}` (not a paginated `{total, size, collection}` envelope).

```python
api.get_tags_from_agency(agency_id)  # {"tags": [...]}
api.get_tags_from_agent(agent_id)
api.set_tags_to_agent(agent_id, ["tag-c"])
api.add_tags_to_agent(agent_id, ["tag-a", "tag-b"])
api.remove_tags_from_agent(agent_id, ["tag-a"])
api.clear_tags_from_agent(agent_id)

# bulk variants
api.get_tags_from_agents([agent_id])
api.set_tags_to_agents([agent_id], ["tag-c"])
api.add_tags_to_agents([agent_id], ["tag-a"])
api.remove_tags_from_agents([agent_id], ["tag-a"])
api.clear_tags_from_agents([agent_id])
```

### Catalog / platform

```python
api.get_version()
api.get_oses()
api.get_users(size=50)
api.get_user_roles()
api.get_vaccines(size=50)
api.get_instances(size=50, filter_by="type:2")
api.get_sectors()
```

### Errors & rate limits

- HTTP timeouts → `MicroClaudiaTimeoutError`
- Login / token refresh failures → `MicroClaudiaAuthError`
- 401 after a failed retry → `MicroClaudiaUnauthorizedError`
- 403 → `MicroClaudiaForbiddenError`
- 429 → `MicroClaudiaRateLimitError` (subclass of `MicroClaudiaAPIError`)
- Any other non-2xx → `MicroClaudiaAPIError`
- Schema mismatch → `MicroClaudiaSchemaError`
- Missing identifier → `MicroClaudiaAgencyError`, `MicroClaudiaSectorError`,
  `MicroClaudiaInstanceError`, `MicroClaudiaAgentError`
- Malformed identifier → `MicroClaudiaPatternError`

The client applies `@call_rate_limit(limit_per_minute=12)` to instance methods. Live tests add extra pacing between cases.

## Tests

### Run unit tests (default)

```bash
python -m pytest
```

This runs the unit test suite with the repo defaults from `pytest.ini` (integration tests are deselected).

### Run integration tests (live API)

```bash
python -m pytest tests/integration/test_live_all_api_methods.py -m integration -v
```

Or the full integration folder:

```bash
python -m pytest tests/integration -m integration -v
```

Credentials (required — pick one):

```bash
# env
set MICROCLAUDIA_LIVE_USERNAME=... or $env:MICROCLAUDIA_LIVE_USERNAME = "..."
set MICROCLAUDIA_LIVE_PASSWORD=... or $env:MICROCLAUDIA_LIVE_PASSWORD = "..."
python -m pytest tests/integration/test_live_all_api_methods.py -m integration -v

# pytest CLI flags
python -m pytest tests/integration/test_live_all_api_methods.py -m integration -v --live-user "..." --live-password "..."
```

Notes:
- Requires network access to `microclaudia.ccn-cert.cni.es`.
- Do not hardcode secrets; use env, pytest CLI flags, or the prompt.
- Agency IDs are discovered at runtime (optional overrides: `MICROCLAUDIA_LIVE_AGENCY_EQUIPS` / `MICROCLAUDIA_LIVE_AGENCY_SERVERS`).
- The integration suite includes pacing to reduce HTTP 429 responses. You can tune it with:
  - `MICROCLAUDIA_INTEGRATION_TEST_DELAY` (seconds between integration tests)
  - `MICROCLAUDIA_INTEGRATION_TASK_DELAY` (extra seconds before task-related integration tests)

### Run all tests (unit + integration)

```bash
python -m pytest tests/ -o "addopts=-ra --strict-markers"
```

This overrides the `pytest.ini` default marker expression so integration tests are included.
