#!/usr/bin/env python3

"""This module contains the code to work with the Response Playbook class."""

from pathlib import Path

from ermack.render_knowledge_base import TemplateTypes
from ermack.utils.cpe_wrapper import check_applicability_of_impl
from ermack.utils.utils import Utils as utils

from .entity import Entity
from .response_action_implementation import ResponseActionImpl


class ResponsePlaybook(Entity):
    """
    Class for the Response Playbook entity

    Extends Entity class
    """

    def __init__(self, yaml_string: str):
        """
        Create Response Playbook entity from file

        :param base_path: Path to folder with entities
        :type base_path: str
        :param file_name: File name of the entity
        :type file_name: str
        """
        super().__init__(content=yaml_string, entity_name="response_playbooks")
        self.stages = []
        self.templates = {
            TemplateTypes.markdown: "response_playbook_md_template",
            TemplateTypes.confluence: "response_playbook_confluence_template",
        }

        # RE&CT back compatibility
        if "linked_rp" in self.view:
            self.view["linked_response_playbooks"] = self.view["linked_rp"]

    @classmethod
    def from_file(cls, file_path: str):
        relative_file_path = Path(file_path)
        content = utils.read_yaml_file(relative_file_path)
        response_playbook = cls(content)
        response_playbook.handle_path(relative_file_path)
        return response_playbook

    @staticmethod
    def get_mandatory_fields() -> dict:
        return {
            "title": None,
            "id": None,
            "description": None,
            "author": None,
            "creation_date": None,
            "preparation": None,
            "identification": None,
            "containment": None,
            "eradication": None,
            "recovery": None,
            "lessons_learned": None,
            "extended_description": None,
        }

    @staticmethod
    def get_entity_name():
        """Get entity name"""
        return "response_playbooks"

    @staticmethod
    def get_acronym():
        """Get entity short name (acronym)"""
        return "RP"

    def enrich(self, template_type: TemplateTypes):
        """Enrich with information about linked entities

        :param template_type: <Unused>
        :type template_type: SupportedTemplateTypes
        """
        counter = 1
        data = self.data()
        stages = self.entities_map.entities["response_stages"]["instances"]
        response_actions = self.entities_map.entities["response_actions"]["instances"]
        stages_with_titles_as_keys = {
            stages[stage_id]
            .get("title", "en")
            .lower()
            .replace(" ", "_"): stages[stage_id]
            for stage_id in stages
        }
        for field in data:
            if field not in stages_with_titles_as_keys:
                continue
            stage = stages_with_titles_as_keys[field]
            stage_view = {
                "title": stage.get_title(),
                "filename": stage.get("filename"),
                "link_id": counter,
                "response_actions": [],
            }
            counter += 1
            for response_action in data[field]:
                action_id = self.extract_id(response_action)
                response_action = response_actions[action_id]
                response_action_view = {
                    "title": response_action.get_title(),
                    "filename": response_action.get("filename"),
                    "link_id": counter,
                    "implementations": [],
                }
                counter += 1
                mapping = self.entities_map.entities_relations_mapping["RA->RAI"]
                if action_id in mapping:
                    response_action_impls = mapping[action_id]
                    response_action_view["implementations"] = []
                    for impl in response_action_impls:
                        if self.cpe_soft_identification(impl):
                            response_action_view["implementations"].append(
                                {
                                    "title": impl.get_title(),
                                    "filename": impl.get("filename"),
                                    "link_id": counter,
                                }
                            )
                            counter += 1
                stage_view["response_actions"].append(response_action_view)
            self.stages.append(stage_view)
            self.update({"response_stages": self.stages})

    def simple_soft_identification(self, impl: ResponseActionImpl):
        """
        Identify applicability of implementation for current infrastructure profile

        :param impl: Response Action Implementation entity
        :type impl: ResponseActionImpl
        :return: True if applicable
        :rtype: bool
        """
        infrastructure_profile = self.entities_map.get_current_infrastructure_profile()
        if infrastructure_profile is None:
            return True
        soft_profile = infrastructure_profile.get("software_profile")
        available_soft = {soft["id"] for soft in soft_profile}
        required_soft = set(impl.get("linked_software"))
        return required_soft.issubset(available_soft)

    def cpe_soft_identification(self, impl: ResponseActionImpl) -> bool:
        """
        Identify applicability of implementation for current infrastructure profile

        Via Common Platform Enumeration identifier

        :param impl: Response Action Implementation entity
        :type impl: ResponseActionImpl
        :return: True if applicable
        :rtype: bool
        """
        infrastructure_profile = self.entities_map.get_current_infrastructure_profile()
        if infrastructure_profile is None:
            return True
        applicable = check_applicability_of_impl(
            infrastructure_profile=infrastructure_profile, impl=impl
        )
        # if not applicable:
        #     impl_id = impl.view["id"]
        #     print(f"{impl_id} not applicable")
        return applicable
