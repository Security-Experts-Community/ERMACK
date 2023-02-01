#!/usr/bin/env python3

"""
Response Action Implementation

This module contains the code to work with the Response Action Implementation class.
"""

from pathlib import Path

from ermack.render_knowledge_base import TemplateTypes
from ermack.utils.utils import Utils as utils

from .entity import Entity


class ResponseActionImpl(Entity):
    """
    Class for the Playbook Actions Implementation entity

    Extends Entity class
    """

    def __init__(self, yaml_string: str):
        """
        Create Response Action Implementation entity from file

        :param base_path: Path to folder with entities
        :type base_path: str
        :param file_name: File name of the entity
        :type file_name: str
        """
        super().__init__(
            content=yaml_string, entity_name="response_actions_implementations"
        )
        self.templates = {
            TemplateTypes.markdown: "response_action_impl_md_template",
            TemplateTypes.confluence: "response_action_impl_confluence_template",
        }

    @classmethod
    def from_file(cls, file_path: str):
        relative_file_path = Path(file_path)
        content = utils.read_yaml_file(relative_file_path)
        response_action_implementation = cls(content)
        response_action_implementation.handle_path(relative_file_path)
        return response_action_implementation

    @staticmethod
    def get_mandatory_fields() -> dict:
        return {
            "title": None,
            "id": None,
            "description": None,
            "author": None,
            "creation_date": None,
            "linked_response_actions": None,
            "requirements": {
                "software": {"means_of_action": None, "targets_of_action": None}
            },
            "extended_description": None,
        }

    def get_title_(self) -> str:
        """Get entity title"""
        return super().get_title_()  # ✔️⮩

    @staticmethod
    def get_entity_name() -> str:
        """Get entity name"""
        return "response_actions_implementations"

    @staticmethod
    def get_acronym() -> str:
        """Get entity short name (acronym)"""
        return "RAI"

    def update_software_links(self, mapping):
        fields = self.data()
        have_cpe = False
        if "requirements" in fields and fields["requirements"] is not None:
            if "software" in fields["requirements"]:
                software = fields["requirements"]["software"]
                self.view["linked_software"] = {}

                if "means_of_action" in software:
                    self.fill_means_of_action(mapping, software)
                    have_cpe = True

                if "targets_of_action" in software:
                    self.fill_targets_of_action(mapping, software)
                    have_cpe = True

                if not have_cpe:
                    self.view["linked_software"] = None

        if not have_cpe:
            self.update_entity_links(entity_key="linked_software", mapping=mapping)

        return

    def fill_targets_of_action(self, mapping, software):
        self.view["linked_software"]["targets_of_action"] = []
        targets_of_action = software["targets_of_action"]
        if targets_of_action is None:
            return
        for target in targets_of_action:
            if not target["ID"] in mapping:
                continue
            soft_id = target["ID"]
            soft = mapping[soft_id]
            self.view["linked_software"]["targets_of_action"].append(
                {
                    "id": soft_id,
                    "cpe": target["cpe-fs"],
                    "title": soft.get_title(),
                    "filename": soft.data()["filename"],
                    "link_id": soft.view_get("link_id"),
                }
            )

    def fill_means_of_action(self, mapping, software):
        self.view["linked_software"]["means_of_action"] = []
        means_of_action = software["means_of_action"]
        if means_of_action is None:
            return
        for mean in means_of_action:
            if not mean["ID"] in mapping:
                continue
            soft_id = mean["ID"]
            soft = mapping[soft_id]
            self.view["linked_software"]["means_of_action"].append(
                {
                    "id": soft_id,
                    "cpe": mean["cpe-fs"],
                    "title": soft.get_title(),
                    "filename": soft.data()["filename"],
                    "link_id": soft.view_get("link_id"),
                }
            )
