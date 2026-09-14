from app.actions.dispatcher import ActionDispatcher
from app.models.situation import Situation
from app.workflows.email_formatter import (
    build_situation_email,
)
from app.workflows.execution import WorkflowExecution
from app.workflows.model import WorkflowPolicy
from app.workflows.rules import evaluate_condition
from sqlalchemy.orm import Session


class WorkflowPolicyService:

    def __init__(self):
        self.dispatcher = ActionDispatcher()

    # =========================================================
    # Policy CRUD
    # =========================================================

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

    # =========================================================
    # Policy evaluation
    # =========================================================

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
                matched_policies.append(
                    policy
                )

        return matched_policies

    # =========================================================
    # Execution creation
    # =========================================================

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

    # =========================================================
    # Workflow execution
    # =========================================================

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
            # -------------------------------------------------
            # Load Situation
            # -------------------------------------------------

            situation = (
                db.query(Situation)
                .filter(
                    Situation.id
                    == execution.situation_id
                )
                .first()
            )

            if situation is None:
                raise ValueError(
                    "Situation not found for workflow execution"
                )

            # -------------------------------------------------
            # Refresh Situation from database
            # -------------------------------------------------

            db.refresh(situation)

            # -------------------------------------------------
            # Mark execution as Running
            # -------------------------------------------------

            execution.status = "Running"

            db.commit()
            db.refresh(execution)

            # -------------------------------------------------
            # Copy action payload
            # -------------------------------------------------

            action_payload = dict(
                execution.action_payload
                or {}
            )

            # -------------------------------------------------
            # Dynamic email body
            # -------------------------------------------------

            if (
                execution.action_type
                and execution.action_type.lower()
                == "email"
            ):
                custom_message = (
                    action_payload.get(
                        "body"
                    )
                )

                action_payload["body"] = (
                    build_situation_email(
                        situation=situation,
                        execution=execution,
                        custom_message=custom_message,
                    )
                )

                # Save the generated email body
                # into workflow execution.
                execution.action_payload = (
                    action_payload
                )

                db.commit()
                db.refresh(execution)

                print(
                    f"CogniOpsAI email generated "
                    f"for Situation {situation.id}: "
                    f"AI status="
                    f"{situation.ai_status}"
                )

            # -------------------------------------------------
            # Dispatch action
            # -------------------------------------------------

            result = self.dispatcher.dispatch(
                action_type=execution.action_type,
                payload=action_payload,
            )

            # -------------------------------------------------
            # Mark success
            # -------------------------------------------------

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

            print(
                f"Workflow execution "
                f"{execution.id} failed: "
                f"{type(exc).__name__}: {exc}"
            )

            return execution

    # =========================================================
    # Evaluate + create executions
    # =========================================================

    def evaluate_and_create_executions(
        self,
        db: Session,
        situation: Situation,
    ):
        matched_policies = (
            self.evaluate_policies(
                db,
                situation,
            )
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