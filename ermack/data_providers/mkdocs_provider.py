#!/usr/bin/env python3

"""Module that handle rendering KB as mkdocs site"""

import os
import shutil
from collections import OrderedDict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ermack.data_providers.markdown_provider import MarkdownProvider
from ermack.render_knowledge_base import TemplateTypes
from ermack.utils.localization import Localization
from ermack.utils.utils import Utils as utils
from ermack.utils.visual import (
    material_icons_style,
    material_search_html,
    material_search_js,
)

config = utils.load_config("config.yml")

templates_base_dir = config.get("templates_base_dir")
default_lang = config.get("default_localization_lang")

lang_list = os.listdir(templates_base_dir)
lang = config.get("default_localization_lang")
if lang not in lang_list:
    lang = "en"
templates_path = f"{templates_base_dir}/{lang}/markdown"
if not os.path.exists(templates_path):
    raise Exception("Can't find templates directory!")

env = Environment(loader=FileSystemLoader(templates_path))
loc = Localization()


class MkdocsProvider(MarkdownProvider):
    """Renders knowledge base as mkdocs site"""

    def __init__(self, entities_map: dict):
        """Create mkdocs renderer"""
        super().__init__()

        self.template = env.get_template(config.get("mkdocs_template"))
        self.entities_map = entities_map

    def init_structure(self, with_root_page) -> bool:
        """Create initial folder layout and required files

        :param with_root_page: <Unused>
        :type with_root_page: bool
        :return: Status of initialization
        :rtype: bool
        """
        super().init_structure(with_root_page)
        docs_dir = Path(self.docs_dir)
        root_folder = Path(self.root_folder)
        theme = config.get("mkdocs_theme")
        if theme == "material":
            (docs_dir / "stylesheets").mkdir(parents=True, exist_ok=True)
            style_path = "stylesheets/extra.css"
            utils.write_file(docs_dir / style_path, self.__get_style())

            (docs_dir / "assets/javascripts").mkdir(parents=True, exist_ok=True)
            js_search_path = "assets/javascripts/iframe-worker.js"
            utils.write_file(docs_dir / js_search_path, self.__get_search_js())

            (root_folder / "theme").mkdir(parents=True, exist_ok=True)
            html_search_path = "theme/main.html"
            utils.write_file(root_folder / html_search_path, self.__get_search_html())

        return self.__create_mkdocs_config()

    def __get_value(self, arr, idx, field):
        value = arr[idx].get(field)
        if isinstance(value, dict):
            if "value" in value:
                return value["value"]
        return value

    def __get_entity_view(self, entity_name):
        entities = self.entities_map.entities[entity_name]["instances"]
        result = []
        for entity_id in sorted(
            entities, key=lambda id, e=entities: self.__get_value(e, id, "title")
        ):
            result.append(
                (
                    self.__get_value(entities, entity_id, "title"),
                    self.__get_value(entities, entity_id, "filename"),
                    self.__get_value(entities, entity_id, "tags"),
                )
            )
        return result

    def __create_mkdocs_config(self):
        data_to_render = {}
        data_to_render.update(
            {"stage_actions_trees": self.generate_stage_actions_trees()}
        )

        entities_names = ["software", "artifacts", "usecases", "response_playbooks"]

        for entity_name in entities_names:
            data_to_render.update({entity_name: self.__get_entity_view(entity_name)})

        other_data = ["introduction", "infrastructure_profiles", "stages"]
        for name in other_data:
            data_to_render[name] = None

        data_to_render.update(loc.get_localizable_fields(data_to_render))

        theme = config.get("mkdocs_theme")
        data_to_render.update(
            {"theme": "material" if theme == "material" else "default"}
        )

        content = self.template.render(data_to_render)
        try:
            base_output_dir = config.get("base_output_dir")
            utils.write_file(f"{base_output_dir}mkdocs.yml", content)
            print("[✓] Created mkdocs.yml")
            return True
        except OSError:
            print("[!] Failed to create mkdocs.yml")
            return False

    # def get_stage_view(self, stage, counter):
    #     return {
    #         "title": stage.get_title(),
    #         "filename": stage.get("filename"),
    #         "link_id": counter,
    #         "response_actions": [],
    #     }

    # def get_action_view(self, action, counter):
    #     return {
    #         "title": action.get_title(),
    #         "filename": action.get("filename"),
    #         "link_id": counter,
    #         "implementations": [],
    #     }

    # def get_implementation_view(self, implementation, counter):
    #     return {
    #         "title": implementation.get_title(),
    #         "filename": implementation.get("filename"),
    #         "link_id": counter,
    #     }

    def generate_stage_actions_trees(self):
        """Generate actions' tree. Actions grouped by stages

        :return: Generated tree
        :rtype: dict
        """
        counter = 1
        tree = []
        stages = self.entities_map.get_response_stages()
        for stage_id in OrderedDict(sorted(stages.items())):
            stage = stages[stage_id]
            stage_view = {
                "title": stage.get_title(),
                "filename": stage.get("filename"),
                "link_id": counter,
                "response_actions": [],
            }
            counter += 1
            correspond_response_actions = self.entities_map.entities_relations_mapping[
                "RS->RA"
            ][stage_id]
            correspond_response_actions.sort(key=lambda x: x.view["id"])
            for response_action in correspond_response_actions:
                response_action_view = {
                    "title": response_action.get_title(),
                    "filename": response_action.get("filename"),
                    "link_id": counter,
                    "implementations": [],
                }
                counter += 1
                action_id = response_action.get("id")
                relations_mapping = self.entities_map.entities_relations_mapping[
                    "RA->RAI"
                ]
                if action_id in relations_mapping:
                    response_action_impls = relations_mapping[action_id]
                    response_action_impls.sort(key=lambda x: x.view["id"])
                    response_action_view["implementations"] = [
                        {
                            "title": impl.get_title(),
                            "filename": impl.get("filename"),
                            "link_id": counter,
                        }
                        for impl in response_action_impls
                    ]
                    counter += 1
                stage_view["response_actions"].append(response_action_view)
            tree.append(stage_view)
        return tree

    def write_entity(self, entity, title_with_id=False):
        """Write entity to a markdown file

        :param entity: Entity to render
        :type entity: Entity
        :param title_with_id: <Unused>
        :type title_with_id: bool, optional
        :return: Status of operation
        :rtype: bool
        """
        theme = config.get("mkdocs_theme")
        entity.update({"theme": "material" if theme == "material" else "default"})
        template_type = TemplateTypes.markdown
        template = env.get_template(entity.get_template_name(template_type))
        entity.enrich(template_type)
        entity.render_template(template, template_type)
        base = os.path.basename(entity.yaml_file)
        file_name = os.path.splitext(base)[0]
        os.makedirs(f"{self.docs_dir}/{entity.entity_name}/{file_name}", exist_ok=True)
        for img in entity.image_files:
            img_name = Path(img)._parts[-1]
            shutil.copyfile(
                src=img,
                dst=f"{self.docs_dir}/{entity.entity_name}/{file_name}/{img_name}",
            )
        return self.save_markdown_file(
            "entity", f"{entity.entity_name}/{file_name}", entity.content
        )

    def render_entities_table(self, entitites):
        """Create summary page with entities table

        :param entities: Entities to render as table
        :type entities: list[Entity]
        :return: Status of file creation
        :rtype: bool
        """
        return super().render_entities_table(entitites)

    def __get_style(self):
        return material_icons_style

    def __get_search_html(self):
        return material_search_html

    def __get_search_js(self):
        return material_search_js

    def render_infrastructure_profile(self, profile):
        """Render infrastructure profile as mkdocs page

        :param profile: Profile to render
        :type profile: Entity
        :return: Status of file creation
        :rtype: bool
        """
        theme = config.get("mkdocs_theme")
        profile.update({"theme": "material" if theme == "material" else "default"})
        return super().render_infrastructure_profile(profile)

    def enrich(self, entity):
        """Enrich entity

        :param entity: Entity to enrich
        :type entity: Entity
        :return: None
        :rtype: None
        """
        return super().enrich(entity)
