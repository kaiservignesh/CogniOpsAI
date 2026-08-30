from app.models.situation import Situation
from app.workflows.execution import WorkflowExecution
from app.workflows.model import WorkflowPolicy
from app.workflows.rules import evaluate_condition
from sqlalchemy.orm import Session


class WorkflowPolicyService:
    def create_policy(
        self,
        db: Session,
        policy_data,
    ):
        policy = WorkflowPolicy(
            **policy_data.model_dump()
        )

        db.add(policy)
        db.commit()
        db.refresh(policy)

        return policy

    def get_all_policies(
        self,
        db: Session,
    ):
        return (
            db.query(WorkflowPolicy)
            .order_by(
                WorkflowPolicy.created_at.desc()
            )
            .all()
        )

    def get_policy_by_id(
        self,
        db: Session,
        policy_id: int,
    ):
        return (
            db.query(WorkflowPolicy)
            .filter(
                WorkflowPolicy.id == policy_id
            )
            .first()
        )

    def update_policy(
        self,
        db: Session,
        policy_id: int,
        policy_data,
    ):
        policy = self.get_policy_by_id(
            db,
            policy_id,
        )

        if policy is None:
            return None

        update_data = policy_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                policy,
                field,
                value,
            )

        db.commit()
        db.refresh(policy)

        return policy

    def evaluate_policies(
        self,
        db: Session,
        situation: Situation,
    ):
        policies = (
            db.query(WorkflowPolicy)
            .filter(
                WorkflowPolicy.enabled.is_(True)
            )
            .all()
        )

        matched_policies = []

        for policy in policies:
            if evaluate_condition(
                situation,
                policy.condition,
            ):
                matched_policies.append(policy)

        return matched_policies

    def create_execution(
        self,
        db: Session,
        situation: Situation,
        policy: WorkflowPolicy,
    ):
        action = policy.action or {}

        execution = WorkflowExecution(
            situation_id=situation.id,
            policy_id=policy.id,
            status="Pending",
            action_type=action.get("type"),
            action_target=action.get("target"),
            action_payload=action,
        )

        db.add(execution)
        db.commit()
        db.refresh(execution)

        return execution

    def evaluate_and_create_executions(
        self,
        db: Session,
        situation: Situation,
    ):
        matched_policies = self.evaluate_policies(
            db,
            situation,
        )

        executions = []

        for policy in matched_policies:
            execution = self.create_execution(
                db,
                situation,
                policy,
            )

            executions.append(execution)

        return executions