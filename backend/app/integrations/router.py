from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.integrations.grafana.service import GrafanaService
from app.integrations.loki.service import LokiService
from app.integrations.newrelic.service import NewRelicService
from app.models.user import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
)


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