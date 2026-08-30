from app.alerts.model import Alert
from app.database.database import SessionLocal
from app.models.situation import Situation
from app.workflows.service import WorkflowPolicyService


def main():
    db = SessionLocal()

    try:
        situation = (
            db.query(Situation)
            .filter(
                Situation.service == "payment-api",
                Situation.environment == "production",
                Situation.severity == "Critical",
            )
            .first()
        )

        if situation is None:
            print("No matching Situation found.")
            return

        print(
            f"Using Situation: "
            f"{situation.id} - {situation.title}"
        )

        service = WorkflowPolicyService()

        matched_policies = service.evaluate_policies(
            db,
            situation,
        )

        print(
            f"\nMatched Policies: "
            f"{len(matched_policies)}\n"
        )

        for policy in matched_policies:
            print(
                f"- {policy.id}: {policy.name}"
            )

        executions = (
            service.evaluate_and_create_executions(
                db,
                situation,
            )
        )

        print(
            f"\nWorkflow Executions: "
            f"{len(executions)}\n"
        )

        for execution in executions:
            print(
                f"ID: {execution.id}\n"
                f"Policy ID: {execution.policy_id}\n"
                f"Situation ID: "
                f"{execution.situation_id}\n"
                f"Status: {execution.status}\n"
                f"Action Type: "
                f"{execution.action_type}\n"
                f"Target: "
                f"{execution.action_target}\n"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()