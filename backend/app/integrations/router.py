import os

from app.alerts.service import create_alert
from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.integrations.grafana.service import GrafanaService
from app.integrations.loki.service import LokiService
from app.integrations.newrelic.adapter import NewRelicAdapter
from app.integrations.newrelic.service import NewRelicService
from app.integrations.grafana.adapter import GrafanaAdapter
from app.models.user import User
from app.models.situation import Situation
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    BackgroundTasks,
)
from sqlalchemy.orm import Session
from app.alerts.model import Alert


def _normalize_status(value: object) -> str:
    """Map provider lifecycle values to CogniOpsAI alert statuses."""
    if value is None:
        return "Open"

    status = str(value).strip().lower()

    if status in {"resolved", "closed", "inactive", "ok", "complete", "completed"}:
        return "Resolved"

    if status in {"investigating"}:
        return "Investigating"

    if status in {"firing", "open", "active", "activated", "new", "triggered"}:
        return "Open"

    return "Open"


def _extract_provider_status(data: dict) -> str:
    """Read lifecycle state from custom or standard webhook payloads."""
    explicit_status = (
        data.get("status")
        or data.get("state")
        or data.get("issue_state")
        or data.get("issueState")
        or data.get("alert_state")
        or data.get("alertState")
    )

    if explicit_status is not None:
        return _normalize_status(explicit_status)

    # Some customized webhooks send a boolean closure flag.
    if data.get("closed") is True or data.get("is_closed") is True:
        return "Resolved"

    if data.get("resolved") is True:
        return "Resolved"

    return "Open"


def _resolve_situation_if_all_alerts_resolved(
    db: Session,
    situation_id: int | None,
):
    """Resolve a Situation only when every attached Alert is resolved."""
    if situation_id is None:
        return None

    situation = (
        db.query(Situation)
        .filter(Situation.id == situation_id)
        .first()
    )

    if situation is None:
        return None

    alerts = (
        db.query(Alert)
        .filter(Alert.situation_id == situation_id)
        .all()
    )

    if alerts and all(
        (alert.status or "Open").strip().lower()
        in {"resolved", "closed"}
        for alert in alerts
    ):
        situation.status = "Resolved"

    db.commit()
    db.refresh(situation)
    return situation


def _update_existing_alerts_for_resolution(
    db: Session,
    source: str,
    issue_id: str | None,
) -> list[Alert]:
    """Resolve only the alert with the exact provider issue tag."""
    if not issue_id:
        return []

    expected_tag = f"issue:{issue_id}"

    open_alerts = (
        db.query(Alert)
        .filter(
            Alert.source == source,
            Alert.status != "Resolved",
        )
        .order_by(Alert.created_at.desc())
        .all()
    )

    matching_alert = None

    for alert in open_alerts:
        tags = [
            tag.strip()
            for tag in (alert.tags or "").split(",")
            if tag.strip()
        ]

        if expected_tag in tags:
            matching_alert = alert
            break

    if matching_alert is None:
        return []

    matching_alert.status = "Resolved"

    situation_id = matching_alert.situation_id

    db.commit()
    db.refresh(matching_alert)

    if situation_id is not None:
        _resolve_situation_if_all_alerts_resolved(
            db,
            situation_id,
        )

    return [matching_alert]


router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
)

def process_newrelic_alert(alert_id: int):
    from app.database.database import SessionLocal
    from app.correlation.service import CorrelationService

    db = SessionLocal()

    try:
        correlation_service = CorrelationService()

        correlation_service.correlate_alert(
            db=db,
            alert_id=alert_id,
        )

    except Exception as exc:
        print(
            f"Background New Relic processing failed "
            f"for alert {alert_id}: "
            f"{type(exc).__name__}: {exc}"
        )

    finally:
        db.close()


def process_grafana_alert(alert_id: int):
    from app.correlation.service import CorrelationService
    from app.database.database import SessionLocal

    db = SessionLocal()

    try:
        correlation_service = CorrelationService()

        correlation_service.correlate_alert(
            db=db,
            alert_id=alert_id,
        )

    except Exception as exc:
        print(
            f"Background Grafana processing failed "
            f"for alert {alert_id}: "
            f"{type(exc).__name__}: {exc}"
        )

    finally:
        db.close()

@router.post("/newrelic/ingest")
def ingest_newrelic(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    service = NewRelicService()

    alerts = service.ingest_alerts(db)

    return {
        "source": "New Relic",
        "count": len(alerts),
        "alerts": alerts,
    }


@router.post("/grafana/ingest")
def ingest_grafana(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    service = GrafanaService()

    alerts = service.ingest_alerts(db)

    return {
        "source": "Grafana",
        "count": len(alerts),
        "alerts": alerts,
    }


@router.post("/loki/ingest")
def ingest_loki(
    query: str,
    limit: int = 100,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    service = LokiService()

    alerts = service.ingest_logs(
        db=db,
        query=query,
        limit=limit,
    )

    return {
        "source": "Loki",
        "count": len(alerts),
        "alerts": alerts,
    }

@router.post("/newrelic/webhook")
async def newrelic_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),  # noqa: B008
    authorization: str | None = Header(default=None),
):
    expected_token = os.getenv("NEW_RELIC_WEBHOOK_TOKEN")

    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="NEW_RELIC_WEBHOOK_TOKEN is not configured",
        )

    if authorization != f"Bearer {expected_token}":
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook token",
        )

    payload = await request.json()
    lifecycle_status = _extract_provider_status(payload)

    print("=== NEW RELIC WEBHOOK RECEIVED ===")
    print(payload)
    print(f"New Relic lifecycle status: {lifecycle_status}")

    issue_id = payload.get("issue_id") or payload.get("issueId")

    # A closed/resolved issue updates its existing alert(s) instead of
    # creating a brand-new alert.
    if lifecycle_status == "Resolved":
        resolved_alerts = _update_existing_alerts_for_resolution(
            db=db,
            source="New Relic",
            issue_id=issue_id,
        )

        return {
            "source": "New Relic",
            "status": "resolved",
            "count": len(resolved_alerts),
            "alert_ids": [alert.id for alert in resolved_alerts],
        }

    # Prevent duplicate New Relic firing events.
    if issue_id:
        existing_alert = (
            db.query(Alert)
            .filter(
                Alert.source == "New Relic",
                Alert.tags.contains(f"issue:{issue_id}"),
                Alert.status != "Resolved",
            )
            .order_by(Alert.created_at.desc())
            .first()
        )

        if existing_alert:
            if existing_alert.status != "Open":
                existing_alert.status = "Open"
                db.commit()
                db.refresh(existing_alert)

            if existing_alert.situation_id is not None:
                _resolve_situation_if_all_alerts_resolved(
                    db,
                    existing_alert.situation_id,
                )

            return {
                "source": "New Relic",
                "status": "duplicate_ignored",
                "alert_id": existing_alert.id,
            }

    alert_data = NewRelicAdapter.normalize_webhook(payload)

    alert = create_alert(
        db=db,
        alert=alert_data,
        auto_process=False,
    )

    alert.status = "Open"
    db.commit()
    db.refresh(alert)

    background_tasks.add_task(
        process_newrelic_alert,
        alert.id,
    )

    return {
        "source": "New Relic",
        "status": "accepted",
        "alert_id": alert.id,
    }

@router.post("/grafana/webhook")
async def grafana_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),  # noqa: B008
    authorization: str | None = Header(default=None),
):
    expected_token = os.getenv("GRAFANA_WEBHOOK_TOKEN")

    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="GRAFANA_WEBHOOK_TOKEN is not configured",
        )

    if authorization != f"Bearer {expected_token}":
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook token",
        )

    payload = await request.json()

    print("=== GRAFANA WEBHOOK RECEIVED ===")
    print(payload)

    if "alerts" in payload and isinstance(payload["alerts"], list):
        alerts = payload["alerts"]
    else:
        alerts = [payload]

    accepted_alerts = []

    for grafana_alert in alerts:
        lifecycle_status = _extract_provider_status(grafana_alert)
        issue_id = grafana_alert.get("issue_id")

        print(
            f"Grafana lifecycle status: {lifecycle_status}, "
            f"issue_id={issue_id}"
        )

        # Resolved webhook: update existing occurrences instead of
        # creating another Alert.
        if lifecycle_status == "Resolved":
            resolved_alerts = _update_existing_alerts_for_resolution(
                db=db,
                source="Grafana",
                issue_id=issue_id,
            )

            accepted_alerts.append(
                {
                    "status": "resolved",
                    "alert_ids": [
                        alert.id
                        for alert in resolved_alerts
                    ],
                }
            )
            continue

        # Firing/active event: preserve every genuine occurrence.
        alert_data = GrafanaAdapter.normalize_webhook_alert(
            grafana_alert
        )

        alert = create_alert(
            db=db,
            alert=alert_data,
            auto_process=False,
        )

        alert.status = "Open"
        db.commit()
        db.refresh(alert)

        print(
            f"Grafana alert created: "
            f"id={alert.id}, "
            f"title={alert.title}, "
            f"source={alert.source}, "
            f"severity={alert.severity}, "
            f"policy_name={alert.policy_name}, "
            f"tags={alert.tags}"
        )

        background_tasks.add_task(
            process_grafana_alert,
            alert.id,
        )

        accepted_alerts.append(
            {
                "status": "accepted",
                "alert_id": alert.id,
            }
        )

    return {
        "source": "Grafana",
        "status": "accepted",
        "count": len(accepted_alerts),
        "alerts": accepted_alerts,
    }
