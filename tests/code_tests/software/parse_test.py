"""Tests for Parsing Software file"""

from ermack.entities.software import Software

file_path = "./tests/code_tests/software/standard_software.yml"


def test_parse_yaml_file():
    software = Software.from_file(file_path)
    assert software is not None


def test_check_mandatory_fields():
    software = Software.from_file(file_path)
    mandatory_fields = Software.get_mandatory_fields()

    for field in mandatory_fields:
        assert field in software.view


def test_expected_parsed_fields():
    software = Software.from_file(file_path)

    assert software.get_title() == "Название ПО"
    assert software.view_get("id") == "S0002"
    assert software.get_title_with_id() == "S0002: Название ПО"
    expected_description = "Краткое описание продукта или решения"
    assert software.view_get("description").strip() == expected_description
    assert software.view_get("author") == "@ERMACK_COMMUNITY"
    assert software.view_get("references") == [
        "http://www.example.com",
    ]
