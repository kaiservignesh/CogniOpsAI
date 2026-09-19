from datetime import datetime

from app.correlation.model import CorrelationPolicy
from sqlalchemy.orm import Session


class CorrelationPolicyService:
    FIELD_NAMES = {
        "source",
        "policy_name",
        "service",
        "environment",
        "severity",
        "title",
    }

    def create_policy(self, db: Session, policy_data):
        policy = CorrelationPolicy(
            name=policy_data.name,
            description=policy_data.description,
            enabled=policy_data.enabled,
            condition=policy_data.condition,
            time_window_minutes=policy_data.time_window_minutes,
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    def get_all_policies(self, db: Session):
        return (
            db.query(CorrelationPolicy)
            .order_by(CorrelationPolicy.created_at.desc())
            .all()
        )

    def get_policy_by_id(self, db: Session, policy_id: int):
        return (
            db.query(CorrelationPolicy)
            .filter(CorrelationPolicy.id == policy_id)
            .first()
        )

    def update_policy(self, db: Session, policy_id: int, policy_data):
        policy = self.get_policy_by_id(db, policy_id)
        if policy is None:
            return None

        for field, value in policy_data.model_dump(exclude_unset=True).items():
            setattr(policy, field, value)

        db.commit()
        db.refresh(policy)
        return policy

    @classmethod
    def _value_matches(cls, value, operator: str, expected) -> bool:
        if value is None or expected is None:
            return False

        actual = str(value).strip().lower()
        expected_text = str(expected).strip().lower()

        if operator in {"equals", "eq"}:
            return actual == expected_text

        if operator in {"contains", "contains_text"}:
            return expected_text in actual

        if operator in {"not_equals", "ne"}:
            return actual != expected_text

        return False

    @staticmethod
    def _alert_has_tag(alert, expected: str) -> bool:
        raw_tags = getattr(alert, "tags", None) or ""
        tags = {
            tag.strip().lower()
            for tag in raw_tags.split(",")
            if tag.strip()
        }
        return expected.strip().lower() in tags

    @staticmethod
    def _within_window(alert_1, alert_2, minutes: int) -> bool:
        created_1 = getattr(alert_1, "created_at", None)
        created_2 = getattr(alert_2, "created_at", None)

        if not isinstance(created_1, datetime) or not isinstance(created_2, datetime):
            return False

        return abs((created_1 - created_2).total_seconds()) <= max(minutes, 0) * 60

    def matches(
        self,
        alert_1,
        alert_2,
        policy: CorrelationPolicy,
    ) -> bool:
        if not policy.enabled:
            return False

        if not self._within_window(
            alert_1,
            alert_2,
            policy.time_window_minutes,
        ):
            return False

        condition = policy.condition or {}
        rules = condition.get("rules", [])
        match_mode = str(condition.get("match", "all")).lower()

        if not rules:
            return True

        results = []

        for rule in rules:
            field = rule.get("field")
            operator = rule.get("operator", "equals")
            expected = rule.get("value")

            if field == "tag":
                if not isinstance(expected, str):
                    results.append(False)
                    continue
                results.append(
                    self._alert_has_tag(alert_1, expected)
                    and self._alert_has_tag(alert_2, expected)
                )
                continue

            if field not in self.FIELD_NAMES:
                results.append(False)
                continue

            value_1 = getattr(alert_1, field, None)
            value_2 = getattr(alert_2, field, None)

            results.append(
                self._value_matches(value_1, operator, expected)
                and self._value_matches(value_2, operator, expected)
            )

        return any(results) if match_mode == "any" else all(results)

    @classmethod
    def specificity_score(cls, policy: CorrelationPolicy) -> tuple[int, int, int, int]:
        """
        Rank matching policies deterministically.

        Higher values are more specific. The ranking prefers:
        1. more restrictive operators (equals > contains > not_equals),
        2. longer expected values for contains rules,
        3. more rules when match mode is all.

        Policy creation order is intentionally not used as a business priority.
        """
        condition = policy.condition or {}
        rules = condition.get("rules", [])
        match_mode = str(condition.get("match", "all")).lower()

        if not rules:
            return (0, 0, 0, 0)

        operator_weight = {
            "equals": 300,
            "eq": 300,
            "contains": 200,
            "contains_text": 200,
            "not_equals": 100,
            "ne": 100,
        }

        rule_scores: list[int] = []
        expected_lengths: list[int] = []

        for rule in rules:
            operator = str(
                rule.get("operator", "equals")
            ).strip().lower()
            expected = rule.get("value")

            base = operator_weight.get(operator, 0)
            length = len(str(expected).strip()) if expected is not None else 0

            rule_scores.append(base + min(length, 100))
            expected_lengths.append(length)

        strongest_rule = max(rule_scores, default=0)
        total_rule_score = sum(rule_scores)
        total_expected_length = sum(expected_lengths)
        rule_count = len(rules) if match_mode == "all" else 1

        return (
            strongest_rule,
            total_rule_score,
            rule_count,
            total_expected_length,
        )

    def matching_policies(
        self,
        db: Session,
        alert_1,
        alert_2,
    ) -> list[CorrelationPolicy]:
        policies = (
            db.query(CorrelationPolicy)
            .filter(CorrelationPolicy.enabled.is_(True))
            .all()
        )

        matches = [
            policy
            for policy in policies
            if self.matches(alert_1, alert_2, policy)
        ]

        # Evaluate every matching policy, then rank the matches so a more
        # specific rule is preferred over a broader rule.
        matches.sort(
            key=lambda policy: (
                self.specificity_score(policy),
                -policy.id,
            ),
            reverse=True,
        )

        return matches

    def matches_alert(
        self,
        alert,
        policy: CorrelationPolicy,
    ) -> bool:
        """
        Check whether a single alert belongs to a
        correlation policy.

        Time window is intentionally not checked here,
        because a time window only makes sense when
        comparing two alerts.
        """

        if not policy.enabled:
            return False

        condition = policy.condition or {}

        rules = condition.get(
            "rules",
            [],
        )

        match_mode = str(
            condition.get(
                "match",
                "all",
            )
        ).lower()

        if not rules:
            return True

        results = []

        for rule in rules:
            field = rule.get("field")
            operator = rule.get(
                "operator",
                "equals",
            )
            expected = rule.get("value")

            if field == "tag":
                if not isinstance(
                    expected,
                    str,
                ):
                    results.append(False)
                    continue

                results.append(
                    self._alert_has_tag(
                        alert,
                        expected,
                    )
                )
                continue

            if field not in self.FIELD_NAMES:
                results.append(False)
                continue

            actual_value = getattr(
                alert,
                field,
                None,
            )

            results.append(
                self._value_matches(
                    actual_value,
                    operator,
                    expected,
                )
            )

        if match_mode == "any":
            return any(results)

        return all(results)

    def policies_for_alert(
        self,
        db: Session,
        alert,
    ) -> list[CorrelationPolicy]:
        policies = (
            db.query(CorrelationPolicy)
            .filter(
                CorrelationPolicy.enabled.is_(True)
            )
            .all()
        )

        matches = [
            policy
            for policy in policies
            if self.matches_alert(
                alert,
                policy,
            )
        ]

        matches.sort(
            key=lambda policy: (
                self.specificity_score(
                    policy
                ),
                -policy.id,
            ),
            reverse=True,
        )

        return matches


    def select_policy_for_alert(
        self,
        db: Session,
        alert,
    ) -> CorrelationPolicy | None:
        matches = self.policies_for_alert(
            db,
            alert,
        )

        return matches[0] if matches else None
