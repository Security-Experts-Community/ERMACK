#!/usr/bin/env python3

"""This module contains the code to work with the Usecase class."""

from pathlib import Path

from ermack.render_knowledge_base import TemplateTypes
from ermack.utils.utils import Utils as utils

from .entity import Entity


class Usecase(Entity):
    """
    Class for the Software entity

    Extends Entity class
    """

    def __init__(self, yaml_string: str):
        """
        Create Usecase entity from file

        :param base_path: Path to folder with entities
        :type base_path: str
        :param file_name: File name of the entity
        :type file_name: str
        """
        super().__init__(content=yaml_string, entity_name="usecases")
        self.templates = {
            TemplateTypes.markdown: "usecase_md_template",
            TemplateTypes.confluence: "usecase_confluence_template",
        }

    @classmethod
    def from_file(cls, file_path: str):
        relative_file_path = Path(file_path)
        content = utils.read_yaml_file(relative_file_path)
        usecase = cls(content)
        usecase.handle_path(relative_file_path)
        return usecase

    def get_mandatory_fields() -> dict:
        return {
            "title": None,
            "id": None,
            "description": None,
            "author": None,
            "creation_date": None,
            "linked_artifacts": None,
            "extended_description": None,
        }

    @staticmethod
    def get_entity_name() -> str:
        """Get entity name"""
        return "usecases"

    @staticmethod
    def get_acronym() -> str:
        """Get entity short name (acronym)"""
        return "UC"
