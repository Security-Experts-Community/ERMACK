#!/usr/bin/env python3

"""This module contains the code to work with the Infrastructure Profile class."""

from pathlib import Path

from ermack.render_knowledge_base import TemplateTypes
from ermack.utils.utils import Utils as utils

from .entity import Entity


class InfrastructureProfile(Entity):
    """
    Class for the Infrastructure Configuration

    Extends Entity class
    """

    def __init__(self, yaml_string: str):
        """
        Create Infrastructure Profile entity from file

        :param base_path: Path to folder with entities
        :type base_path: str
        :param file_name: File name of the entity
        :type file_name: str
        """
        super().__init__(content=yaml_string, entity_name="infrastructure_profiles")
        self.update({"configuration_name": self.get("filename")})
        self.templates = {
            TemplateTypes.markdown: "infrastructure_profile_md_template",
            TemplateTypes.confluence: "infrastructure_profile_confluence_template",
        }

    @classmethod
    def from_file(cls, file_path: str):

        relative_file_path = Path(file_path)
        content = utils.read_yaml_file(relative_file_path)
        profile = cls(content)
        profile.handle_path(relative_file_path)
        return profile

    @staticmethod
    def get_entity_name() -> str:
        """Get entity name"""
        return "infrastructure_profiles"

    @staticmethod
    def get_acronym() -> str:
        """Get entity short name (acronym)"""
        return "IP"

    def update_software_links(self, mapping):
        """Create linked entities mapping

        :param mapping: Mapping dictionary
        :type mapping: dict
        """
        # __set_cpe = lambda view, entity: (view["cpe"] = entity["cpe"] if "cpe" in entity else "")

        self.update_entity_links(
            entity_key="software_profile",
            mapping=mapping,
            get_id=lambda soft_entry: soft_entry["id"],
            enrich=set_cpe,
        )
        return


def set_cpe(view: dict, entity: dict) -> dict:
    view["cpe"] = entity["cpe-fs"] if "cpe-fs" in entity else ""
    return view
