"""InfluxDB write/query helpers for the PMVB orchestration layer.

All measurement data flows through these helpers. Wraps the influxdb-client SDK
with conventions specific to PMVB:

- Token read once at call time from /etc/pmvb/influx.token (fallback to
  PMVB_INFLUX_TOKEN env var).
- Org and bucket default to `pmvb` / `measurements` per SDD §10.2.
- Tag taxonomy enforced: instrument, channel, dut, run_id, measurement_type.

The token-file location, URL, org, and bucket are all overridable via env vars
so the same code path works on the bench host, in CI, and against a test
InfluxDB.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = os.environ.get("PMVB_INFLUX_URL", "http://localhost:8086")
INFLUX_ORG = os.environ.get("PMVB_INFLUX_ORG", "pmvb")
INFLUX_BUCKET = os.environ.get("PMVB_INFLUX_BUCKET", "measurements")
INFLUX_TOKEN_PATH = os.environ.get("PMVB_INFLUX_TOKEN_PATH", "/etc/pmvb/influx.token")


def _read_token() -> str:
    """Read the InfluxDB token from disk, with env-var fallback."""
    env_token = os.environ.get("PMVB_INFLUX_TOKEN")
    if env_token:
        return env_token
    path = Path(INFLUX_TOKEN_PATH)
    if not path.exists():
        raise FileNotFoundError(
            f"InfluxDB token not found at {path} and PMVB_INFLUX_TOKEN env not set"
        )
    return path.read_text().strip()


def get_client() -> InfluxDBClient:
    """Construct a configured InfluxDBClient. Caller owns the connection lifecycle.

    Typical usage::

        with get_client() as client:
            ...
    """
    return InfluxDBClient(url=INFLUX_URL, token=_read_token(), org=INFLUX_ORG)


def write_measurement(
    *,
    measurement: str,
    instrument: str,
    channel: str | int,
    dut: str,
    run_id: str,
    measurement_type: str,
    value: float,
    extra_fields: dict[str, Any] | None = None,
    timestamp: datetime | None = None,
    bucket: str = INFLUX_BUCKET,
) -> None:
    """Write one measurement point with the SDD §10.2 tag taxonomy.

    All keyword-only to prevent argument-order mistakes that would otherwise
    silently produce mis-tagged records.
    """
    point = (
        Point(measurement)
        .tag("instrument", str(instrument))
        .tag("channel", str(channel))
        .tag("dut", dut)
        .tag("run_id", run_id)
        .tag("measurement_type", measurement_type)
        .field("value", float(value))
    )
    if extra_fields:
        for k, v in extra_fields.items():
            point = point.field(k, v)
    if timestamp is None:
        timestamp = datetime.now(tz=timezone.utc)
    point = point.time(timestamp)

    with get_client() as client:
        with client.write_api(write_options=SYNCHRONOUS) as write_api:
            write_api.write(bucket=bucket, record=point)


def query_run(run_id: str, *, bucket: str = INFLUX_BUCKET, lookback: str = "-30d") -> list[dict]:
    """Query all measurements for a given run_id. Returns list of flat dicts.

    The default 30-day lookback is generous; tighten it via the `lookback`
    keyword if a query is slow on a busy bucket.
    """
    flux = f'''
from(bucket: "{bucket}")
  |> range(start: {lookback})
  |> filter(fn: (r) => r.run_id == "{run_id}")
'''
    with get_client() as client:
        tables = client.query_api().query(flux)
        results = []
        for table in tables:
            for record in table.records:
                results.append(
                    dict(
                        time=record.get_time(),
                        measurement=record.get_measurement(),
                        value=record.get_value(),
                        field=record.get_field(),
                        instrument=record.values.get("instrument"),
                        channel=record.values.get("channel"),
                        dut=record.values.get("dut"),
                        run_id=record.values.get("run_id"),
                        measurement_type=record.values.get("measurement_type"),
                    )
                )
        return results
