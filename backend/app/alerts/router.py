from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.alerts.schema import (
    AlertCreate,
    AlertResponse,
    AlertUpdate,
)
from app.alerts.service import (
    create_alert,
    delete_alert,
    get_alert_by_id,
    get_all_alerts,
    update_alert,
)
from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.post("/", response_model=AlertResponse)
def add_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return create_alert(db, alert)


@router.get("/", response_model=list[AlertResponse])
def get_alerts(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return get_all_alerts(db)


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return get_alert_by_id(db, alert_id)


@router.put("/{alert_id}", response_model=AlertResponse)
def edit_alert(
    alert_id: int,
    alert: AlertUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return update_alert(db, alert_id, alert)


@router.delete("/{alert_id}")
def remove_alert(
    alert_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return delete_alert(db, alert_id)