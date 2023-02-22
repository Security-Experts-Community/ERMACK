#!/usr/bin/env python3

"""Module that handle rendering KB as local markdown files"""

import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ermack.data_providers.data_provider import DataProvider
from ermack.entities.entity import Entity
from ermack.render_knowledge_base import TemplateTypes
from ermack.utils.localization import Localization
from ermack.utils.utils import Utils as utils

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


class MarkdownProvider(DataProvider):
    """Renders knowledge base as local markdown files"""

    def __init__(self):
        """Create markdown renderer"""
        self.root_folder = config.get("base_output_dir")
        self.docs_dir = self.root_folder + config.get("md_name_of_root_directory")

    def __copy_descriptions_files(self, base_dir: str) -> None:
        files = [
            "README.md",
            "INSTALLATION.md",
            "VISION.md",
            "CONTRIBUTION.md",
        ]

        for file in files:
            content = utils.read_text_file(file)
            utils.write_file(f"{base_dir}/{file}", content)

        return

    def init_structure(self, with_root_page: bool):
        """Create initial folders layout

        :param with_root_page: Unused
        :type with_root_page: bool
        """
        Path(self.docs_dir).mkdir(parents=True, exist_ok=True)
        base_dir = Path(self.docs_dir)
        target_dir_list = [
            "response_actions",
            "response_actions_implementations",
            "software",
            "artifacts",
            "response_playbooks",
            "usecases",
            "response_stages",
        ]
        for item in target_dir_list:
            (base_dir / item).mkdir(parents=True, exist_ok=True)
        self.__create_unimplemented_stubs(base_dir)
        self.__copy_descriptions_files(base_dir)

        return

    def __create_unimplemented_stubs(self, base_dir):
        target_dir_list = [
            "response_actions",
            "software",
            "artifacts",
            "response_playbooks",
            "usecases",
        ]

        for item in target_dir_list:
            folder = base_dir / item / "unimplemented"
            folder.mkdir(parents=True, exist_ok=True)
            entity_name = item if not item.endswith("s") else item[0:-1]
            entity_name = entity_name.replace("_", " ")

            utils.write_file(
                folder / "entity.md",
                f"""# Unimplemented {entity_name}
Sorry, this {entity_name} is not implemented yet!""",
            )

    # TODO: refactor code to remove unused methods
    def create_actions_structure(self):
        """Create structure of actions

        Implemented for interface compatibility
        """
        pass

    def write_entity(self, entity: Entity, title_with_id=False) -> bool:
        """Render entity as markdown file

        :param entity: Entity to render
        :type entity: Entity
        :param title_with_id: Unused
        :type title_with_id: bool, optional
        :return: Status of file creation
        :rtype: bool
        """
        template_type = TemplateTypes.markdown
        template = env.get_template(entity.get_template_name(template_type))
        entity.enrich(template_type)
        entity.render_template(template, template_type)
        base = os.path.basename(entity.yaml_file)
        file_name = os.path.splitext(base)[0]
        return self.save_markdown_file(file_name, entity.entity_name, entity.content)

    def save_markdown_file(self, file_name, parent_dir, content) -> bool:
        """Write content (md template filled with data) to a file"""
        file_path = f"{self.docs_dir}/{parent_dir}/{file_name}.md"
        return utils.write_file(file_path, content)

    def __get_entities_name(self, entities):
        return entities[list(entities.keys())[0]].get_entity_name()

    def render_entities_table(self, entities):
        """Create summary file with entities table

        :param entities: Entities to render as table
        :type entities: list[Entity]
        :return: Status of file creation
        :rtype: bool
        """
        template = env.get_template(config.get("entities_table_md_template"))
        entity_name = self.__get_entities_name(entities)
        entities_list = []
        for entity_id in entities:
            entity = entities[entity_id]
            if entity.view_get(
                "tags"
            ) is not None and "sub-playbook" in entity.view_get("tags"):
                continue

            entities_list.append(
                {
                    "id": entity.view_get("id"),
                    "title": entity.get_title(),
                    "filename": f"{entity.view_get('filename')}/entity",
                    "description": entity.view_get("description"),
                    "link_id": len(entities_list) + 1,
                    "parent_title": entity.entity_name,
                }
            )

        data_to_render = {}
        data_to_render["entity_name"] = loc.get_localization(entity_name)
        data_to_render["entities_list"] = entities_list
        content = template.render(data_to_render)
        self.save_markdown_file(entity_name, "", content)

    def render_sub_table(self, entities):
        """Create summary file with entities table

        :param entities: Entities to render as table
        :type entities: list[Entity]
        :return: Status of file creation
        :rtype: bool
        """
        template = env.get_template(config.get("entities_table_md_template"))
        entity_name = self.__get_entities_name(entities)
        entities_list = []
        for entity_id in entities:
            entity = entities[entity_id]
            if entity.view_get(
                "tags"
            ) is not None and "sub-playbook" not in entity.view_get("tags"):
                continue
            entities_list.append(
                {
                    "id": entity.view_get("id"),
                    "title": entity.get_title(),
                    "filename": f"{entity.view_get('filename')}/entity",
                    "description": entity.view_get("description"),
                    "link_id": len(entities_list) + 1,
                    "parent_title": entity.entity_name,
                }
            )

        data_to_render = {}
        data_to_render["entity_name"] = loc.get_localization(entity_name)
        data_to_render["entities_list"] = entities_list
        content = template.render(data_to_render)
        self.save_markdown_file("sub_" + entity_name, "", content)

    def render_infrastructure_profile(self, infrastructure_profile):
        """Create infrastructure profile file

        :param infrastructure_profile: Infrastructure profile entity
        :type infrastructure_profile: Entity
        :return: Status of file creation
        :rtype: bool
        """
        template_type = TemplateTypes.markdown
        template = env.get_template(
            infrastructure_profile.get_template_name(template_type)
        )
        infrastructure_profile.render_template(template, template_type)
        return self.save_markdown_file(
            file_name="infrastructure_profile.md",
            parent_dir="",
            content=infrastructure_profile.content,
        )

    def enrich(self, entity):
        """Enrich entity

        :param entity: Entity to enrich
        :type entity: Entity
        """
        entity.enrich(TemplateTypes.markdown)
