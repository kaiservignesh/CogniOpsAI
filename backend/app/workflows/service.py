from app.models.situation import Situation
from app.workflows.execution import WorkflowExecution
from app.workflows.model import WorkflowPolicy
from app.workflows.rules import evaluate_condition
from sqlalchemy.orm import Session
from app.actions.dispatcher import ActionDispatcher


class WorkflowPolicyService:
    
    def __init__(self):
        self.dispatcher = ActionDispatcher()

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
        existing_execution = (
            db.query(WorkflowExecution)
            .filter(
                WorkflowExecution.situation_id
                == situation.id,
                WorkflowExecution.policy_id
                == policy.id,
            )
            .order_by(
                WorkflowExecution.created_at.desc()
            )
            .first()
        )

        if existing_execution is not None:
            return existing_execution

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

    def execute_workflow(
        self,
        db: Session,
        execution_id: int,
    ):
        execution = (
            db.query(WorkflowExecution)
            .filter(
                WorkflowExecution.id
                == execution_id
            )
            .first()
        )

        if execution is None:
            return None

        if execution.status != "Pending":
            return execution

        try:
            execution.status = "Running"
            db.commit()
            db.refresh(execution)

            result = self.dispatcher.dispatch(
                action_type=execution.action_type,
                payload=execution.action_payload or {},
            )

            execution.status = "Success"
            execution.result = result

            db.commit()
            db.refresh(execution)

            return execution

        except Exception as exc:
            execution.status = "Failed"
            execution.result = str(exc)

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