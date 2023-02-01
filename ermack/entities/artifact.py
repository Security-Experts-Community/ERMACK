#!/usr/bin/env python3

from pathlib import Path

from ermack.render_knowledge_base import TemplateTypes
from ermack.utils.utils import Utils as utils

from .entity import Entity


class Artifact(Entity):
    """Class for the Artifact entity"""

    def __init__(self, yaml_string: str):
        super().__init__(yaml_string, entity_name="artifacts")
        self.templates = {
            TemplateTypes.markdown: "artifact_md_template",
            TemplateTypes.confluence: "artifact_confluence_template",
        }

    @staticmethod
    def get_mandatory_fields() -> dict:
        return {
            "title": None,
            "id": None,
            "description": None,
            "author": None,
            "creation_date": None,
        }

    @classmethod
    def from_file(cls, file_path: str):

        relative_file_path = Path(file_path)
        content = utils.read_yaml_file(relative_file_path)
        artifact = cls(content)
        artifact.handle_path(relative_file_path)
        return artifact

    @staticmethod
    def get_entity_name():
        return "artifacts"

    @staticmethod
    def get_acronym():
        return "ART"
