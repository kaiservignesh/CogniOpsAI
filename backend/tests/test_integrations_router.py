from types import SimpleNamespace

import pytest

from app.integrations import router as integration_router


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self.rows[0] if self.rows else None

    def all(self):
        return list(self.rows)


class FakeDB:
    def __init__(self, alerts=None, situation=None):
        self.alerts = alerts or []
        self.situation = situation

    def query(self, model):
        if model is integration_router.Alert:
            return FakeQuery(self.alerts)
        if model is integration_router.Situation:
            rows = [self.situation] if self.situation is not None else []
            return FakeQuery(rows)
        raise AssertionError(f"Unexpected model queried: {model}")

    def commit(self):
        pass

    def refresh(self, obj):
        pass


def make_alert(alert_id, source="Grafana", status="Open",
               tags="", situation_id=132):
    return SimpleNamespace(
        id=alert_id,
        source=source,
        status=status,
        tags=tags,
        situation_id=situation_id,
    )


def test_provider_status_normalization():
    assert integration_router._normalize_status("OPEN") == "Open"
    assert integration_router._normalize_status("firing") == "Open"
    assert integration_router._normalize_status("investigating") == "Investigating"
    assert integration_router._normalize_status("RESOLVED") == "Resolved"
    assert integration_router._normalize_status("closed") == "Resolved"


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"status": "firing"}, "Open"),
        ({"state": "resolved"}, "Resolved"),
        ({"issue_state": "closed"}, "Resolved"),
        ({"closed": True}, "Resolved"),
        ({"resolved": True}, "Resolved"),
        ({}, "Open"),
    ],
)
def test_extract_provider_status(payload, expected):
    assert integration_router._extract_provider_status(payload) == expected


def test_resolution_uses_exact_issue_tag():
    alert_248 = make_alert(
        248,
        tags="issue:Prometheus CPU Alert,environment:Production",
    )
    alert_249 = make_alert(
        249,
        tags="issue:Prometheus CPU Alert (copy),environment:Production",
    )

    db = FakeDB(alerts=[alert_248, alert_249])
    resolved_situations = []

    def fake_resolve_situation(db_arg, situation_id):
        resolved_situations.append(situation_id)

    original = integration_router._resolve_situation_if_all_alerts_resolved
    integration_router._resolve_situation_if_all_alerts_resolved = fake_resolve_situation
    try:
        resolved = integration_router._update_existing_alerts_for_resolution(
            db=db,
            source="Grafana",
            issue_id="Prometheus CPU Alert",
        )
    finally:
        integration_router._resolve_situation_if_all_alerts_resolved = original

    assert [alert.id for alert in resolved] == [248]
    assert alert_248.status == "Resolved"
    assert alert_249.status == "Open"
    assert resolved_situations == [132]


def test_situation_stays_open_until_all_alerts_resolved():
    situation = SimpleNamespace(id=132, status="Open")
    alerts = [
        make_alert(248, status="Resolved"),
        make_alert(249, status="Open"),
    ]
    db = FakeDB(alerts=alerts, situation=situation)

    result = integration_router._resolve_situation_if_all_alerts_resolved(
        db=db,
        situation_id=132,
    )

    assert result.status == "Open"


def test_situation_resolves_when_all_alerts_are_resolved():
    situation = SimpleNamespace(id=132, status="Open")
    alerts = [
        make_alert(248, status="Resolved"),
        make_alert(249, status="Resolved"),
    ]
    db = FakeDB(alerts=alerts, situation=situation)

    result = integration_router._resolve_situation_if_all_alerts_resolved(
        db=db,
        situation_id=132,
    )

    assert result.status == "Resolved"


def test_newrelic_uses_same_exact_issue_matching():
    alert_301 = make_alert(
        301,
        source="New Relic",
        tags="issue:NR-CPU,entity:payment-service",
    )
    alert_302 = make_alert(
        302,
        source="New Relic",
        tags="issue:NR-CPU-OLD,entity:payment-service",
    )
    db = FakeDB(alerts=[alert_301, alert_302])

    resolved = integration_router._update_existing_alerts_for_resolution(
        db=db,
        source="New Relic",
        issue_id="NR-CPU",
    )

    assert [alert.id for alert in resolved] == [301]
    assert alert_301.status == "Resolved"
    assert alert_302.status == "Open"
