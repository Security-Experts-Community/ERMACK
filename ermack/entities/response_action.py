#!/usr/bin/env python3

"""This module contains the code to work with the Response Action class."""

from pathlib import Path

from jinja2 import Template

from ermack.render_knowledge_base import TemplateTypes
from ermack.utils.localization import stages_mapping
from ermack.utils.utils import Utils as utils

from .entity import Entity


class ResponseAction(Entity):
    """
    Class for the Playbook Actions entity

    Extends Entity class
    """

    def __init__(self, yaml_string: str):
        """
        Create Response Action entity from file

        :param base_path: Path to folder with entities
        :type base_path: str
        :param file_name: File name of the entity
        :type file_name: str
        """
        super().__init__(content=yaml_string, entity_name="response_actions")
        self.templates = {
            TemplateTypes.markdown: "response_action_md_template",
            TemplateTypes.confluence: "response_action_confluence_template",
        }

    @classmethod
    def from_file(cls, file_path: str):
        relative_file_path = Path(file_path)
        content = utils.read_yaml_file(relative_file_path)
        response_action = cls(content)
        response_action.handle_path(relative_file_path)
        return response_action

    @staticmethod
    def get_mandatory_fields() -> dict:
        return {
            "title": None,
            "id": None,
            "description": None,
            "author": None,
            "creation_date": None,
            "stage": None,
            "requirements": {
                "software": {"means_of_action": None, "targets_of_action": None},
                "actions": None,
            },
            "extended_description": None,
        }

    @staticmethod
    def get_entity_name() -> str:
        """Get entity name"""
        return "response_actions"

    @staticmethod
    def get_acronym() -> str:
        """Get entity short name (acronym)"""
        return "RA"

    @staticmethod
    def have_special_link_name_for(entity_name: str) -> str | None:
        """When create entity mapping we need return some special names for entities

        :param entity_name: Entity name
        :type entity_name: str
        :return: Special name for entity or None
        :rtype: str | None
        """
        if entity_name == "response_stages":
            return "stage"
        return None

    def get_requirement_actions(self) -> list:
        return self.view["requirements"]["actions"]

    def render_template(self, template: Template, template_type: TemplateTypes) -> None:
        """Specific rendering logic for Response Action object

        :param template: Compiled jinja2 template
        :type template: Template
        :param template_type: Template type to render
        :type template_type: SupportedTemplateTypes
        :raises Exception: If the template type is unsupported
        """
        if template_type not in TemplateTypes:
            raise Exception(f"Bad template_type {template_type}.")

        self.update({"description": self.get("description").strip()})
        self.update({"title": self.get_title()})

        stage_name = self.get("stage")
        stage_id = stages_mapping[stage_name]
        stages = self.entities_map.get_response_stages()
        stage = stages[stage_id]
        # stages = {
        #     stages[stage_id]
        #     .get("title", "en")
        #     .lower()
        #     .replace(" ", "_"): stages[stage_id]
        #     for stage_id in stages
        # }

        if template_type is TemplateTypes.markdown:
            self.update(
                {
                    "response_stages": {
                        "title": stage.get_title(),
                        "filename": stage.view_get("filename"),
                        # "title": stages[stage_name].get_title(),
                        # "filename": stages[stage_name].get("filename"),
                    }
                }
            )

        elif template_type is TemplateTypes.confluence:
            self.update(
                {
                    "response_stages": {
                        "title": self.parent_title,
                        "link_id": self.view_get("parent_id"),
                    },
                    "confluence_viewpage_url": self.config.get(
                        "confluence_viewpage_url"
                    ),
                }
            )

        self.content = template.render(self.view)
