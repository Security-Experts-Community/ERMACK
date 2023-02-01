"""Tests for Response Playbook Class"""

from ermack.entities.entities_map import EntitiesMap
from ermack.entities.response_playbook import ResponsePlaybook

file_path = "./tests/code_tests/response_playbook/standard_response_playbook.yml"


def test_parse_yaml_file():
    response_playbook = ResponsePlaybook.from_file(file_path)
    assert response_playbook is not None


def test_check_mandatory_fields():
    response_playbook = ResponsePlaybook.from_file(file_path)
    mandatory_fields = ResponsePlaybook.get_mandatory_fields()

    for field in mandatory_fields:
        assert field in response_playbook.view


def test_expected_parsed_fields():
    response_playbook = ResponsePlaybook.from_file(file_path)

    expected_title = "Название сценария реагирования"
    assert response_playbook.get_title() == expected_title
    assert response_playbook.view_get("id") == "RP0001"
    expected_title_with_id = "RP0001: Название сценария реагирования"
    assert response_playbook.get_title_with_id() == expected_title_with_id
    expected_description = "Краткое описание сценария реагирования"
    assert response_playbook.view_get("description").strip() == expected_description
    assert response_playbook.view_get("author") == "@ERMACK_COMMUNITY"
    assert response_playbook.view_get("tags") == [
        "attack.initial_access",
        "attack.t1566.001",
        "attack.t1566.002",
        "phishing",
        "severity.medium",
        "tlp.amber",
        "pap.white",
    ]
    extended_description = response_playbook.view_get("extended_description").strip()
    expected_ext_description = "Расширенное описание сценария реагирования"
    assert extended_description == expected_ext_description
    expected_workflow = "Алгоритм или рекомендации по выполнению стадий реагирования"
    assert response_playbook.view_get("workflow").strip() == expected_workflow


def test_attack():
    response_playbook = ResponsePlaybook.from_file(file_path)

    view = response_playbook.view
    assert view["tactics"] == [["Initial Access", "TA0001"]]
    assert view["techniques"] == [
        ("Spearphishing Attachment", "T1566.001"),
        ("Spearphishing Link", "T1566.002"),
    ]


def test_have_no_empty_stages():
    response_playbook = ResponsePlaybook.from_file(file_path)

    view = response_playbook.view
    assert len(view["preparation"]) > 0
    assert len(view["identification"]) > 0
    assert len(view["containment"]) > 0
    assert len(view["eradication"]) > 0
    assert len(view["recovery"]) > 0
    assert len(view["lessons_learned"]) > 0
