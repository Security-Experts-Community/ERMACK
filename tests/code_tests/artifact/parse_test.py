"""Tests for Parsing Artifact file"""

from ermack.entities.artifact import Artifact

file_path = "./tests/code_tests/artifact/standard_artifact.yml"


def test_parse_yaml_file():
    artifact = Artifact.from_file(file_path)
    assert artifact is not None


def test_check_mandatory_fields():
    artifact = Artifact.from_file(file_path)
    mandatory_fields = Artifact.get_mandatory_fields()

    for field in mandatory_fields:
        assert field in artifact.view


def test_expected_parsed_fields():
    artifact = Artifact.from_file(file_path)

    assert artifact.get_title() == "Название артефакта"
    assert artifact.view_get("id") == "A1001"
    assert artifact.get_title_with_id() == "A1001: Название артефакта"
    assert artifact.view_get("description") == "Краткое описание артефакта"
    assert artifact.view_get("author") == "@ERMACK_COMMUNITY"
    assert artifact.view_get("references") == [
        "http://www.example.com",
        "https://d3fend.mitre.org/dao/artifact/d3f:DNSNetworkTraffic/",
    ]
    assert artifact.view_get("mapping") == ["d3f:DNSNetworkTraffic"]
    extended_description = artifact.view_get("extended_description").strip()
    assert extended_description == "Расширенное описание артефакта"
