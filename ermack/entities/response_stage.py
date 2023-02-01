#!/usr/bin/env python3

"""This module contains the code to work with the Response Stage class."""

from pathlib import Path

from jinja2 import Template

from ermack.render_knowledge_base import TemplateTypes
from ermack.utils.utils import Utils as utils

from .entity import Entity


class ResponseStage(Entity):
    """
    Class for the Response Stage entity

    Extends Entity class
    """

    def __init__(self, yaml_string: str):
        """
        Create Response Stage entity from file

        :param base_path: Path to folder with entities
        :type base_path: str
        :param file_name: File name of the entity
        :type file_name: str
        """
        super().__init__(content=yaml_string, entity_name="response_stages")
        self.response_actions = []
        self.update({"response_actions": ""})
        self.templates = {
            TemplateTypes.markdown: "response_stage_md_template",
            TemplateTypes.confluence: "response_stage_confluence_template",
        }

    @classmethod
    def from_file(cls, file_path: str):
        relative_file_path = Path(file_path)
        content = utils.read_yaml_file(relative_file_path)
        response_stage = cls(content)
        response_stage.handle_path(relative_file_path)
        return response_stage

    @staticmethod
    def get_entity_name() -> str:
        """Get entity name"""
        return "response_stages"

    @staticmethod
    def get_acronym() -> str:
        """Get entity short name (acronym)"""
        return "RS"

    def __get_correspond_entities(
        self, mapping: dict, relation: str, class_id: str
    ) -> dict:
        return mapping[relation][class_id]

    def generate_stage_actions_tree(self, template_type: TemplateTypes) -> list[dict]:
        """Generate actions' tree for current stage

        :return: Generated tree
        :rtype: list[dict]
        """
        counter = 1
        tree = []
        correspond_response_actions = self.__get_correspond_entities(
            self.entities_map.entities_relations_mapping, "RS->RA", self.get("id")
        )
        for response_action in correspond_response_actions:
            response_action_view = {
                "id": response_action.get("id"),
                "title": response_action.get_title(),
                "filename": response_action.get("filename"),
                "description": response_action.get("description"),
                "link_id": counter
                if template_type is TemplateTypes.markdown
                else str(
                    self.utils.confluence_get_page_id(
                        self.apipath, self.auth, self.space, response_action.get_title()
                    )
                ),
                "implementations": [],
            }
            counter += 1
            action_id = response_action.get("id")
            if action_id in self.entities_map.entities_relations_mapping["RA->RAI"]:
                response_action_impls = self.__get_correspond_entities(
                    self.entities_map.entities_relations_mapping, "RA->RAI", action_id
                )
                response_action_view["implementations"] = []
                for impl in response_action_impls:
                    response_action_view["implementations"].append(
                        {
                            "id": impl.get("id"),
                            "title": impl.get_title(),
                            "filename": impl.get("filename"),
                            "description": impl.get("description"),
                            "link_id": counter
                            if template_type == "markdown"
                            else str(
                                self.utils.confluence_get_page_id(
                                    self.apipath,
                                    self.auth,
                                    self.space,
                                    impl.get_title(),
                                )
                            ),
                        }
                    )
                    counter += 1
            tree.append(response_action_view)
        return tree

    def render_template(self, template: Template, template_type: TemplateTypes):
        """Render template with entity's fields

        :param template: Template object to render
        :type template: Template
        :param template_type: Template type
        :type template_type: SupportedTemplateTypes
        """
        if template_type is TemplateTypes.markdown:
            self.update(
                {
                    "actions_tree": self.generate_stage_actions_tree(
                        TemplateTypes.markdown
                    )
                }
            )

        super().render_template(template, template_type)
