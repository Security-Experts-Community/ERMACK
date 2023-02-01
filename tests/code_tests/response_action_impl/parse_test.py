"""Tests for Response Action Implementation Class"""

from ermack.entities.entities_map import EntitiesMap
from ermack.entities.response_action_implementation import ResponseActionImpl

file_path = "./tests/code_tests/response_action_impl/standard_response_action_impl.yml"


def test_parse_yaml_file():
    response_action_impl = ResponseActionImpl.from_file(file_path)
    assert response_action_impl is not None


def test_check_mandatory_fields():
    response_action_impl = ResponseActionImpl.from_file(file_path)
    mandatory_fields = ResponseActionImpl.get_mandatory_fields()

    for field in mandatory_fields:
        assert field in response_action_impl.view
        if field == "requirements":
            requirements = mandatory_fields[field]
            actual_requirements = response_action_impl.view["requirements"]
            assert "software" in actual_requirements
            for soft_requirement in requirements["software"]:
                assert soft_requirement in actual_requirements["software"]


def test_expected_parsed_fields():
    response_action_impl = ResponseActionImpl.from_file(file_path)

    expected_title = "Название реализации действия реагирования"
    assert response_action_impl.get_title() == expected_title
    assert response_action_impl.view_get("id") == "RAI_4201_0002"
    expected_title_with_id = "RAI_4201_0002: Название реализации действия реагирования"
    assert response_action_impl.get_title_with_id() == expected_title_with_id
    expected_description = "Краткое описание реализации действия реагирования"
    assert response_action_impl.view_get("description").strip() == expected_description
    assert response_action_impl.view_get("author") == "@ERMACK_COMMUNITY"
    assert response_action_impl.view_get("linked_response_actions") == "RA4201"
    assert response_action_impl.view_get("category") == "Email"
    assert response_action_impl.view_get("tags") == ["email.delete"]
    assert response_action_impl.view_get("references") == [
        "https://example.com",
    ]
    extended_description = response_action_impl.view_get("extended_description").strip()
    expected_ext_description = (
        "Подробное описание. Инструкции, алгоритмы, скриншоты и т.п."
    )
    assert extended_description == expected_ext_description


def test_update_software_links():
    entity_map = EntitiesMap()
    response_action_impl = ResponseActionImpl.from_file(file_path)

    response_action_impl.update_software_links(entity_map.get_software())
    view = response_action_impl.view
    actual_identifier = view["linked_software"]["targets_of_action"][0]["id"]
    assert actual_identifier == "S3002"


def test_parse_cpe():
    entity_map = EntitiesMap()
    response_action_impl = ResponseActionImpl.from_file(file_path)

    response_action_impl.update_software_links(entity_map.get_software())
    view = response_action_impl.view
    assert "linked_software" in view
    assert "means_of_action" in view["linked_software"]
    assert len(view["linked_software"]["means_of_action"]) > 0
    assert "cpe" in view["linked_software"]["means_of_action"][0]
    actual_cpe_name = view["linked_software"]["means_of_action"][0]["cpe"]
    assert actual_cpe_name == "cpe:2.3:o:linux:*:*:*:*:*:*:*:*:*"
