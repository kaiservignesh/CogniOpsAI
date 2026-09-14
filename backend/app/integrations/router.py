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

    # Prevent duplicate New Relic issues
    issue_id = (
        payload.get("issue_id")
        or payload.get("issueId")
    )

    if issue_id:
        existing_alert = (
            db.query(Alert)
            .filter(
                Alert.source == "New Relic",
                Alert.tags.contains(
                    f"issue:{issue_id}"
                ),
            )
            .first()
        )

        if existing_alert:
            return {
                "source": "New Relic",
                "status": "duplicate_ignored",
                "alert_id": existing_alert.id,
            }

    alert_data = NewRelicAdapter.normalize_webhook(
        payload
    )

    alert = create_alert(
        db=db,
        alert=alert_data,
        auto_process=False,
    )

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
        alert_data = GrafanaAdapter.normalize_webhook_alert(
            grafana_alert
        )

        alert = create_alert(
            db=db,
            alert=alert_data,
            auto_process=False,
        )

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