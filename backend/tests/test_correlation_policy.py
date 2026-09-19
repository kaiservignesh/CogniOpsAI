from types import SimpleNamespace

from app.correlation.policy_service import CorrelationPolicyService


def make_policy(policy_id, rules, match="all", enabled=True):
    return SimpleNamespace(
        id=policy_id,
        enabled=enabled,
        condition={"match": match, "rules": rules},
    )


def test_value_matches_supported_operators():
    service = CorrelationPolicyService

    assert service._value_matches("Grafana", "equals", "Grafana")
    assert service._value_matches(
        "Prometheus CPU Alert", "contains", "Prometheus"
    )
    assert service._value_matches("CPU", "not_equals", "Memory")

    assert not service._value_matches("Grafana", "equals", "New Relic")
    assert not service._value_matches("CPU", "contains", "Memory")


def test_specific_policy_scores_higher_than_generic_policy():
    generic = make_policy(
        2,
        [{
            "field": "policy_name",
            "operator": "contains",
            "value": "Prometheus",
        }],
    )
    specific = make_policy(
        1,
        [{
            "field": "source",
            "operator": "equals",
            "value": "Grafana",
        }, {
            "field": "policy_name",
            "operator": "contains",
            "value": "Prometheus CPU",
        }],
    )

    assert (
        CorrelationPolicyService.specificity_score(specific)
        > CorrelationPolicyService.specificity_score(generic)
    )


def test_equals_is_more_specific_than_contains():
    equals_policy = make_policy(
        1,
        [{
            "field": "policy_name",
            "operator": "equals",
            "value": "Prometheus CPU Alert",
        }],
    )
    contains_policy = make_policy(
        2,
        [{
            "field": "policy_name",
            "operator": "contains",
            "value": "Prometheus",
        }],
    )

    assert (
        CorrelationPolicyService.specificity_score(equals_policy)
        > CorrelationPolicyService.specificity_score(contains_policy)
    )
