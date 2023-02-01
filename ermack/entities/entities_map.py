#!/usr/bin/env python3

# Others
import os
import sys
import traceback

from ermack.utils.localization import stages_mapping
from ermack.utils.utils import Utils as utils

from .artifact import Artifact
from .infrastructure_profile import InfrastructureProfile
from .response_action import ResponseAction
from .response_action_implementation import ResponseActionImpl
from .response_playbook import ResponsePlaybook
from .response_stage import ResponseStage
from .software import Software
from .usecases import Usecase

config = utils.load_config("config.yml")


class EntitiesMap:
    def __init__(self) -> None:
        self.entities = {
            "artifacts": {"class": Artifact, "instances": {}},
            "software": {"class": Software, "instances": {}},
            "usecases": {"class": Usecase, "instances": {}},
            "response_playbooks": {"class": ResponsePlaybook, "instances": {}},
            "response_stages": {"class": ResponseStage, "instances": {}},
            "response_actions": {"class": ResponseAction, "instances": {}},
            "response_actions_implementations": {
                "class": ResponseActionImpl,
                "instances": {},
            },
            "infrastructure_profiles": {
                "class": InfrastructureProfile,
                "instances": {},
            },
        }

        self.entities_relations_mapping = {}

        for entity_name in self.entities:
            base_data_dir = config.get("data_base_dir")
            loc_list = os.listdir(base_data_dir)
            lang = config.get("default_localization_lang")
            if lang not in loc_list:
                lang = "en"
            e_dir = config.get(f"{entity_name}_dir")
            e_list = [
                f.name
                for f in os.scandir(f"{base_data_dir}/{lang}/{e_dir}")
                if f.is_dir()
            ]

            for e_file in e_list:
                try:
                    e = self.entities[entity_name]["class"].from_file(
                        f"{base_data_dir}/{lang}/{e_dir}/{e_file}/{e_file}.yml"
                    )
                    e.set_file_path(e_file)
                    e.set_entity_mapping(self)
                    self.entities[entity_name]["instances"][e.get("id")] = e
                except Exception as e:
                    print(e_file + " failed\n\n%s\n\n" % e)
                    print("Err message: %s" % e)
                    print("-" * 60)
                    traceback.print_exc(file=sys.stdout)
                    print("-" * 60)

        # response_actions->response_actions_impls entity relation mapping
        self.create_relations_mapping(ResponseAction, ResponseActionImpl)

        # software->response_actions_impls entity relation mapping
        self.create_relations_mapping(Software, ResponseActionImpl)

        # artifacts->response_actions_impls entity relation mapping
        self.create_relations_mapping(Artifact, ResponseActionImpl)

        # stages->response_actions entity relation mapping
        self.create_relations_mapping(ResponseStage, ResponseAction, link_is_id=False)

        # usecases->response_playbooks entity relation mapping
        self.create_relations_mapping(ResponsePlaybook, Usecase)

    def create_relations_mapping(self, source_entity, target_entity, link_is_id=True):
        source_entity_name = source_entity.get_entity_name()
        target_entity_name = target_entity.get_entity_name()
        mapping_name = f"{source_entity.get_acronym()}->{target_entity.get_acronym()}"

        self.entities_relations_mapping[mapping_name] = {}
        mapping = self.entities_relations_mapping[mapping_name]

        target_entities = self.get_entities_by_name(target_entity_name)
        source_entities = self.get_entities_by_name(source_entity_name)

        special_name = target_entity.have_special_link_name_for(source_entity_name)
        if special_name is not None:
            links_to_source = special_name
        else:
            links_to_source = f"linked_{source_entity_name}"

        for target_id in target_entities:
            data = target_entities[target_id].data()
            if links_to_source not in data:
                continue

            if isinstance(data[links_to_source], list):
                for entity_link in data[links_to_source]:
                    if links_to_source == "stage" and not link_is_id:
                        entity_link = stages_mapping[entity_link]
                    # If the entity is not linked by ID, but by Title
                    if not link_is_id:
                        title = entity_link
                        if source_entities is None:
                            raise Exception(
                                "Can't convert id to title. Target entity is None!"
                            )

                        for entity_id in source_entities:
                            source_entity = source_entities[entity_id]
                            if (
                                source_entity.get("title", "en")
                                .lower()
                                .replace(" ", "_")
                                == title
                            ):
                                source_id = source_entity.get("id")
                                if source_id not in mapping:
                                    mapping[source_id] = []
                                mapping[source_id].append(target_entities[target_id])
                    else:
                        # TODO: Check other entity links formats
                        entity_link = entity_link.split("_")[0]
                        if entity_link not in mapping:
                            mapping[entity_link] = []
                        mapping[entity_link].append(target_entities[target_id])
            else:
                if links_to_source == "stage" and not link_is_id:
                    link_is_id = True

                if not link_is_id:
                    title = data[links_to_source]
                    if source_entities is None:
                        raise Exception(
                            "Can't convert id to title. Target entity is None!"
                        )
                    for entity_id in source_entities:
                        target_entity = source_entities[entity_id]
                        if (
                            target_entity.get("title", "en").lower().replace(" ", "_")
                            == title
                        ):
                            source_id = target_entity.get("id")
                            if source_id not in mapping:
                                mapping[source_id] = []
                            mapping[source_id].append(target_entities[target_id])
                else:
                    if links_to_source == "stage":
                        field_value = stages_mapping[data["stage"]]
                    else:
                        field_value = data[links_to_source].split("_")[0]
                    if field_value not in mapping:
                        mapping[field_value] = []
                    mapping[field_value].append(target_entities[target_id])
        return

    def get_response_actions(self):
        return self.get_entities_by_name("response_actions")

    def get_response_actions_implementations(self):
        return self.get_entities_by_name("response_actions_implementations")

    def get_response_stages(self):
        return self.get_entities_by_name("response_stages")

    def get_response_playbooks(self):
        return self.get_entities_by_name("response_playbooks")

    def get_software(self):
        return self.get_entities_by_name("software")

    def get_artifacts(self):
        return self.get_entities_by_name("artifacts")

    def get_usecases(self):
        return self.get_entities_by_name("usecases")

    def get_entities_by_name(self, entity_name):
        if entity_name not in self.entities:
            return None

        entities = self.entities[entity_name]["instances"]
        if len(entities.keys()) == 0:
            return None
        else:
            return entities

    def get_infrastructure_profiles(self):
        return self.get_entities_by_name("infrastructure_profiles")

    def get_current_infrastructure_profile(self):
        profiles = self.get_infrastructure_profiles()
        profile_id = config.get("default_infrastructure_profile")
        if profile_id not in profiles:
            print("[!] Can't find default infrastructure profile!")
            return None
        return profiles[profile_id]
