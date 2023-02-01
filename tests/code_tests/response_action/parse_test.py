"""Tests for Parsing Response Action file"""

from ermack.entities.response_action import ResponseAction

file_path = "./tests/code_tests/response_action/standard_response_action.yml"


def test_parse_yaml_file():
    response_action = ResponseAction.from_file(file_path)
    assert response_action is not None


def test_check_mandatory_fields():
    response_action = ResponseAction.from_file(file_path)
    mandatory_fields = ResponseAction.get_mandatory_fields()

    for field in mandatory_fields:
        assert field in response_action.view
        if field == "requirements":
            requirements = mandatory_fields[field]
            actual_requirements = response_action.view["requirements"]
            assert "software" in actual_requirements
            for soft_requirement in requirements["software"]:
                assert soft_requirement in actual_requirements["software"]
            assert "actions" in actual_requirements
            assert len(actual_requirements["actions"]) > 0


def test_expected_parsed_fields():
    response_action = ResponseAction.from_file(file_path)

    assert response_action.get_title() == "Название действия реагирования"
    assert response_action.view_get("id") == "RA0000"
    assert (
        response_action.get_title_with_id() == "RA0000: Название действия реагирования"
    )
    expected_description = "Краткое описание действия реагирования"
    assert response_action.view_get("description").strip() == expected_description
    assert response_action.view_get("author") == "@ERMACK_COMMUNITY"
    assert response_action.view_get("references") == [
        "https://example.com",
    ]
    extended_description = response_action.view_get("extended_description").strip()
    assert extended_description == "Расширенное описание действия реагирования"


def test_required_actions():
    response_action = ResponseAction.from_file(file_path)
    actual_requirement_actions = response_action.get_requirement_actions()
    assert actual_requirement_actions == [{"ID": "RA0001"}]
