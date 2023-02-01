#!/usr/bin/env python3

"""This module is responsible for the logic of data representationThis module"""

import logging
from enum import Enum

from tqdm import tqdm

logger = logging.getLogger("ermack_logger")


class TemplateTypes(str, Enum):
    """Supported types of templates to render"""

    markdown = "markdown"
    confluence = "confluence"

    def __contains__(cls, item: str) -> bool:
        """Check if enum contains specified value

        :param item: Item to check
        :type item: str
        :return: True if Item in this enum
        :rtype: bool
        """
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True


class DataRenderer:
    """Abstract class for render data logic"""

    def __init__(self, entities_map, data_provider):
        """Creation of abstract class for render data logic"""
        self.data_provider = data_provider
        self.entities_map = entities_map

    def render(self, args):
        """Create knowledge base with specified data provider

        :param args: Command line arguments
        :type args: dict
        :raises Exception: When can't create initial structure
        :raises Exception: When parameter set is ambiguous
        """
        # method list to call for automatic run mode
        self.auto_mode_method_list = [
            "infrastructure_profiles",
            "usecases",
            "response_playbooks",
            "response_actions",
            "response_stages",
            "response_actions_impls",
            "software",
            "artifacts",
        ]

        with_root_pages = args["--debug"]

        # Check if init switch was used
        if args["--init"]:
            if self.data_provider.init_structure(with_root_pages):
                logger.info("[✓] Created initial ERM&CK structure successfully")
            else:
                logger.error("[!] Failed to create initial ERM&CK structure")
                raise Exception("Failed to create initial ERM&CK structure")
        else:
            self.data_provider.load_structure()

        # call all methods in auto mode
        if args["--all-entities"]:
            for method_name in self.auto_mode_method_list:
                self.__call_by_name(method_name)
            return

        # else find correspond method
        # convert argument's format to method name's format
        prepared_args = [
            arg.replace("--", "").replace("-", "_") for arg in args.keys() if args[arg]
        ]

        # filter arguments by method names
        arguments = [
            arg
            for arg in prepared_args
            if arg
            in [function for function in dir(self) if callable(getattr(self, function))]
        ]

        # arguments with method names are mutual exclusive
        if len(arguments) != 1:
            raise Exception("Ambiguous parameter set!")

        # call function for corresponding run mode
        method_name = arguments[0]
        self.__call_by_name(method_name)

    def response_actions(self):
        """Populate Response Actions"""
        response_actions = self.entities_map.get_response_actions()
        for action_id in tqdm(
            response_actions,
            desc="[*] Populating Response Actions",
            position=0,
            leave=False,
        ):
            impls_mapping = self.entities_map.entities_relations_mapping["RA->RAI"]
            response_action = response_actions[action_id]
            response_action.infer_related_entities(
                "response_actions_implementations", impls_mapping
            )
            self.data_provider.write_entity(response_action, title_with_id=True)
        logger.info("[✓] Response Actions populated!")

    def response_actions_impls(self):
        """Populate Response Actions Implementations"""
        response_actions_impls = (
            self.entities_map.get_response_actions_implementations()
        )
        software_map = self.entities_map.get_software()
        response_actions_map = self.entities_map.get_response_actions()
        artifacts_map = self.entities_map.get_artifacts()
        for impl_id in tqdm(
            response_actions_impls,
            desc="[*] Populating Response Actions Implementations",
            position=0,
            leave=False,
        ):
            response_action_implementation = response_actions_impls[impl_id]
            response_action_implementation.update_software_links(software_map)
            response_action_implementation.update_response_actions_links(
                response_actions_map
            )
            response_action_implementation.update_artifacts_links(artifacts_map)
            self.data_provider.write_entity(response_action_implementation)
        logger.info("[✓] Response Actions Implementations populated!")

    def software(self):
        """Populate Software"""
        software = self.entities_map.get_software()
        self.data_provider.render_entities_table(software)
        for software_id in tqdm(
            software, desc="[*] Populating Software", position=0, leave=False
        ):
            rai_mapping = self.entities_map.entities_relations_mapping["SW->RAI"]
            soft = software[software_id]
            soft.infer_related_entities("response_actions_implementations", rai_mapping)
            self.data_provider.write_entity(soft, title_with_id=True)
        logger.info("[✓] Software populated!")

    def artifacts(self):
        """Populate Artifacts"""
        artifacts = self.entities_map.get_artifacts()
        self.data_provider.render_entities_table(artifacts)
        for artifact_id in tqdm(
            artifacts, desc="[*] Populating Artifacts", position=0, leave=False
        ):
            rai_mapping = self.entities_map.entities_relations_mapping["ART->RAI"]
            artifact = artifacts[artifact_id]
            artifact.infer_related_entities(
                "response_actions_implementations", rai_mapping
            )
            self.data_provider.write_entity(artifact, title_with_id=True)
        logger.info("[✓] Artifacts populated!")

    def response_playbooks(self):
        """Populate Response Playbooks"""
        response_playbooks = self.entities_map.get_response_playbooks()
        self.data_provider.render_entities_table(response_playbooks)
        artifacts = self.entities_map.get_artifacts()
        usecases = self.entities_map.get_usecases()
        response_playbooks = self.entities_map.get_response_playbooks()
        for playbook_id in tqdm(
            response_playbooks,
            desc="[*] Populating Response Playbooks",
            position=0,
            leave=False,
        ):
            response_playbook = response_playbooks[playbook_id]
            uc_mapping = self.entities_map.entities_relations_mapping["RP->UC"]
            response_playbook.infer_related_entities("usecases", uc_mapping)
            response_playbook.update_playbooks_links(response_playbooks)
            response_playbook.update_artifacts_links(artifacts)
            response_playbook.update_usecases_links(usecases)
            self.data_provider.write_entity(response_playbook, title_with_id=True)
        logger.info("[✓] Response Playbooks populated!")

    def usecases(self):
        """Populate Usecases"""
        usecases = self.entities_map.get_usecases()
        self.data_provider.render_entities_table(usecases)
        artifacts = self.entities_map.get_artifacts()
        response_playbooks = self.entities_map.get_response_playbooks()
        for usecase_id in tqdm(
            usecases, desc="[*] Populating Usecases", position=0, leave=False
        ):
            usecase = usecases[usecase_id]
            usecase.update_playbooks_links(response_playbooks)
            usecase.update_usecases_links(usecases)
            usecase.update_artifacts_links(artifacts)
            self.data_provider.write_entity(usecase, title_with_id=True)
        logger.info("[✓] Usecases populated!")

    def infrastructure_profiles(self):
        """Populate Infrastructure Configuration"""
        print("[*] Populating Infrastructure Configuration...", end="\r")
        software = self.entities_map.get_software()
        infrastructure_profile = self.entities_map.get_current_infrastructure_profile()
        if infrastructure_profile is not None:
            infrastructure_profile.update_software_links(software)
            self.data_provider.render_infrastructure_profile(infrastructure_profile)
        logger.info("[✓] Infrastructure Configuration populated!")

    def response_stages(self):
        """Populate Response Stages"""
        stages = self.entities_map.get_response_stages()
        self.data_provider.render_entities_table(stages)
        for stage_id in tqdm(
            stages, desc="[*] Populating Response Stages", position=0, leave=False
        ):
            self.data_provider.write_entity(stages[stage_id], title_with_id=True)
        logger.info("[✓] Response Stages populated!")

    def __call_by_name(self, method_name):
        getattr(self, method_name)()
