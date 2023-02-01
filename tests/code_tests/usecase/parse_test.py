"""Tests for Parsing Usecase file"""

from ermack.entities.usecases import Usecase

file_path = "./tests/code_tests/usecase/standard_usecase.yml"


def test_parse_yaml_file():
    """Parse Usecase YAML file"""
    usecase = Usecase.from_file(file_path)
    assert usecase is not None


def test_check_mandatory_fields():
    """Check Usecase mandatory fields"""
    usecase = Usecase.from_file(file_path)
    mandatory_fields = Usecase.get_mandatory_fields()

    for field in mandatory_fields:
        assert field in usecase.view


def test_expected_parsed_fields():
    """Check Usecase fields values after parsing"""
    usecase = Usecase.from_file(file_path)

    assert usecase.get_title() == "Usecase Title"
    assert usecase.view_get("id") == "UC0000"
    assert usecase.get_title_with_id() == "UC0000: Usecase Title"
    expected_description = "Usecase Description"
    assert usecase.view_get("description").strip() == expected_description
    assert usecase.view_get("author") == "@ERMACK_COMMUNITY"
    assert usecase.view_get("tags") == [
        "attack.credential_access",
        "attack.t1110.003",
        "brute",
    ]
    assert usecase.view_get("tactics") == [["Credential Access", "TA0006"]]
    assert usecase.view_get("techniques") == [("Password Spraying", "T1110.003")]
    assert usecase.view_get("linked_response_playbooks") == ["RP0000"]
    assert usecase.view_get("linked_artifacts") == ["A1001", "A1006"]
    actual_extended_description = usecase.view_get("extended_description").strip()
    assert actual_extended_description == "Usecase Extended Description"
