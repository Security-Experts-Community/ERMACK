#!/usr/bin/env python3

"""Module that handle rendering KB as Confluence pages"""

import logging
import os
import re

from atlassian import Confluence
from jinja2 import Environment, FileSystemLoader
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

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
templates_path = f"{templates_base_dir}/{lang}/confluence"
if not os.path.exists(templates_path):
    raise Exception("Can't find templates directory!")

env = Environment(loader=FileSystemLoader(templates_path))
loc = Localization()
logger = logging.getLogger("ermack_logger")


class ConfluenceProvider(DataProvider):
    """Renders knowledge base as Confluence pages"""

    def __init__(self, entities_map, confluence: Confluence):
        """Create Confluence provider"""
        self.space = config.get("confluence_space_name")
        self.root_name = config.get("confluence_name_of_root_directory")
        self.space_home_page = config.get("confluence_space_home_page_name")
        self.entities_map = entities_map
        self.confluence = confluence

    def init_structure(self, with_root_page=False):
        """Create initial structure of Confluence knowledge base

        :param with_root_page: If True, there will be created a root page.
            It is handy for testing purpose for fast deletion of all pages
            via web UI, defaults to False
        :type with_root_page: bool, optional
        :return: Status of creation
        :rtype: bool
        """
        root_page = None
        if with_root_page is True:
            self.__create_root_page()
            root_page = self.root_name
        else:
            root_page = self.space_home_page

        # last page id for page order
        last_page_id = None

        # creating entities' root pages
        last_page_id = self.__create_intro_page(root_page)
        last_page_id = self.__create_infrastructure_profile_page(
            root_page, last_page_id
        )
        self.__create_entities_root_pages(root_page, last_page_id)

        # create stage -> actions -> actions' implementations pages
        self.create_actions_structure()

        self.__create_entities_pages()

        logger.info("[✓] Initial Confluence page structure created!")

        return True

    def __create_infrastructure_profile_page(self, root_page, last_page_id):
        page_name = loc.get_localization("infrastructure_profiles")
        profile_en = loc.get_localization("infrastructure_profiles", "en")
        print(f"[*] Creating {profile_en} page...", end="\r")
        parent_id, page_id = self.__create_empty_page(page_name, root_page)
        logger.info(f"[✓] Page {profile_en} with ID={page_id} created!")
        result = self.confluence.move_page(
            self.space, page_id, last_page_id, position="below"
        )
        if "successful" not in result or not bool(result["successful"]):
            logger.info(f"[!] Can't set page {page_name} order")
        profiles = self.entities_map.get_entities_by_name("infrastructure_profiles")
        for profile_id in profiles:
            profile = profiles[profile_id]
            profile.update({"parent_id": parent_id, "link_id": page_id})
            profile.set_parent_title(page_name)
        last_page_id = page_id
        return last_page_id

    def __create_intro_page(self, root_page):
        page_name = loc.get_localization("introduction")
        introduction_en = loc.get_localization("introduction", "en")
        print(
            f"[*] Creating {introduction_en} page...",
            end="\r",
        )
        _, page_id = self.__create_empty_page(page_name, root_page)
        logger.info(f"[✓] Page {introduction_en} with ID={page_id} created!")
        last_page_id = page_id
        return last_page_id

    def __create_entities_root_pages(self, root_page, last_page_id):
        root_pages = [
            "usecases",
            "response_playbooks",
            "response_actions",
            "software",
            "artifacts",
        ]
        for root_page_name in root_pages:
            page_name = loc.get_localization(root_page_name)
            page_print_name = loc.get_localization(root_page_name, "en")
            print(f"[*] Creating {page_print_name} page...", end="\r")
            _, page_id = self.__create_empty_page(page_name, root_page)
            logger.info(f"[✓] Page {page_print_name} with ID={page_id} created!")
            result = self.confluence.move_page(
                self.space, page_id, last_page_id, position="below"
            )
            if "successful" not in result or not bool(result["successful"]):
                logging.info(f"[!] Can't set page {page_print_name} order")

            last_page_id = page_id
            if root_page_name in self.entities_map.entities:
                entities = self.entities_map.get_entities_by_name(root_page_name)
                for entity_id in entities:
                    entity = entities[entity_id]
                    entity.update({"parent_id": page_id})
                    entity.set_parent_title(page_name)

    def __create_entities_pages(self):
        response_playbooks = self.entities_map.get_response_playbooks()
        if response_playbooks is not None:
            self.create_entity_pages(response_playbooks)

        # create other entities' pages
        artifacts = self.entities_map.get_artifacts()
        if artifacts is not None:
            self.create_entity_pages(artifacts)

        software = self.entities_map.get_software()
        if software is not None:
            self.create_entity_pages(software)

        usecases = self.entities_map.get_usecases()
        if usecases is not None:
            self.create_entity_pages(usecases)

    def load_structure(self):
        """Load the structure of the pages form confluence.

        :return: Status of loading
        :rtype: bool
        """
        root_pages = ["usecases", "response_playbooks", "software", "artifacts"]

        page_name = loc.get_localization("introduction")
        introduction_en = loc.get_localization("introduction", "en")
        print(
            f"[*] Loading {introduction_en} page...",
            end="\r",
        )
        page = self.confluence.get_page_by_title(space=self.space, title=page_name)
        logger.info(f"[✓] Page {introduction_en} with ID={page['id']} loaded!")

        page_name = loc.get_localization("infrastructure_profiles")
        profile_en = loc.get_localization("infrastructure_profiles", "en")
        print(f"[*] Loading {profile_en} page...", end="\r")
        page = self.confluence.get_page_by_title(space=self.space, title=page_name)
        parent_id = self.confluence.get_parent_content_id(page["id"])
        logger.info(f"[✓] Page {profile_en} with ID={page['id']} loaded!")
        profiles = self.entities_map.get_entities_by_name("infrastructure_profiles")
        for profile_id in profiles:
            profile = profiles[profile_id]
            profile.update({"parent_id": parent_id, "link_id": page["id"]})
            profile.set_parent_title(page_name)

        page_name = loc.get_localization("response_actions")
        en_page_name = loc.get_localization("response_actions", "en")
        print(f"[*] Loading {en_page_name} page...", end="\r")
        page = self.confluence.get_page_by_title(space=self.space, title=page_name)
        print(f"[✓] Page {en_page_name} with ID={page['id']} loaded!")

        for root_page_name in root_pages:
            page_name = loc.get_localization(root_page_name)
            page_print_name = loc.get_localization(root_page_name, "en")
            print(f"[*] Loading {page_print_name} page...", end="\r")
            page = self.confluence.get_page_by_title(space=self.space, title=page_name)
            print(f"[✓] Page {page_print_name} with ID={page['id']} loaded!")

            parent_id = page["id"]
            if root_page_name in self.entities_map.entities:
                entities = self.entities_map.get_entities_by_name(root_page_name)
                for entity_id in entities:
                    entity = entities[entity_id]
                    page = self.confluence.get_page_by_title(
                        space=self.space, title=entity.get_title_with_id()
                    )
                    entity.update({"parent_id": parent_id, "link_id": page["id"]})
                    entity.set_parent_title(page_name)

        self.load_actions_structure()

        print("[✓] Initial Confluence page structure loaded!")
        return True

    def load_actions_structure(self):
        """Load actions' structure from Confluence pages"""
        stages = self.entities_map.get_response_stages()
        actions = self.entities_map.get_response_actions()
        implementations = self.entities_map.get_response_actions_implementations()
        for stage_id in stages:
            stage = stages[stage_id]
            stage_title = stage.get_title_with_id()
            stage.set_parent_title(loc.get_localization("response_actions"))
            page = self.confluence.get_page_by_title(
                space=self.space, title=stage_title
            )
            parent_id = self.confluence.get_parent_content_id(page["id"])
            stage.update({"parent_id": parent_id, "link_id": page["id"]})
            tree = stage.generate_stage_actions_tree(TemplateTypes.markdown)
            with logging_redirect_tqdm():
                title_en = stage.get("title", "en")
                for tree_action in tqdm(
                    tree,
                    desc=f"[*] Loading Response Actions' pages for {title_en} stage",
                    position=0,
                    leave=False,
                ):
                    action = actions[tree_action["id"]]
                    action_title = action.get_title_with_id()
                    action.set_parent_title(stage_title)
                    page = self.confluence.get_page_by_title(
                        space=self.space, title=action_title
                    )
                    parent_id = self.confluence.get_parent_content_id(page["id"])
                    tree_action.update({"parent_id": parent_id, "link_id": page["id"]})
                    action.update({"parent_id": parent_id, "link_id": page["id"]})
                    for tree_action_impl in tree_action["implementations"]:
                        implementation = implementations[tree_action_impl["id"]]
                        implementation_title = implementation.get_title()
                        implementation.set_parent_title(action_title)
                        page = self.confluence.get_page_by_title(
                            space=self.space, title=implementation_title
                        )
                        parent_id = self.confluence.get_parent_content_id(page["id"])
                        tree_action_impl.update(
                            {"parent_id": parent_id, "link_id": page["id"]}
                        )
                        implementation.update(
                            {"parent_id": parent_id, "link_id": page["id"]}
                        )
            stage.update({"actions_tree": tree})

        print("[✓] Actions' pages for all Response Stages has been loaded!")

    def __create_root_page(self):
        print("[*] Creating ERM&CK root page...", end="\r")
        _, page_id = self.__create_empty_page(self.root_name, self.space_home_page)
        logger.info("[✓] ERM&CK root page created!")
        return page_id

    def create_actions_structure(self):
        """Create actions' structure form content files"""
        stages = self.entities_map.get_response_stages()
        actions = self.entities_map.get_response_actions()
        implementations = self.entities_map.get_response_actions_implementations()
        for stage_id in stages:
            stage = stages[stage_id]
            stage_title = stage.get_title_with_id()
            stage.set_parent_title(loc.get_localization("response_actions"))
            parent_id, page_id = self.__create_empty_page(
                stage_title, stage.parent_title
            )
            stage.update({"parent_id": parent_id, "link_id": page_id})
            tree = stage.generate_stage_actions_tree(TemplateTypes.markdown)
            with logging_redirect_tqdm():
                title_en = stage.get("title", "en")
                for tree_action in tqdm(
                    tree,
                    desc=f"[*] Creating Response Actions' pages for {title_en} stage",
                    position=0,
                    leave=False,
                ):
                    action = actions[tree_action["id"]]
                    action_title = action.get_title_with_id()
                    action.set_parent_title(stage_title)
                    parent_id, page_id = self.__create_empty_page(
                        action_title, stage_title
                    )
                    tree_action.update({"parent_id": parent_id, "link_id": page_id})
                    action.update({"parent_id": parent_id, "link_id": page_id})
                    for tree_action_impl in tree_action["implementations"]:
                        implementation = implementations[tree_action_impl["id"]]
                        implementation_title = "⮩" + implementation.get_title()
                        implementation.set_parent_title(action_title)
                        parent_id, page_id = self.__create_empty_page(
                            implementation_title, action_title
                        )
                        tree_action_impl.update(
                            {"parent_id": parent_id, "link_id": page_id}
                        )
                        implementation.update(
                            {"parent_id": parent_id, "link_id": page_id}
                        )
            stage.update({"actions_tree": tree})

        logger.info("[✓] Actions' pages for all Response Stages has been created!")

    def __get_entities_name(self, entities):
        return entities[list(entities.keys())[0]].get_entity_name()

    def create_entity_pages(self, entities):
        """Create Confluence pages for entities

        :param entities: Entities to render
        :type entities: dict
        """
        entity_name = self.__get_entities_name(entities)
        section_name = loc.get_en_name(entity_name)
        with logging_redirect_tqdm():
            for entity_id in tqdm(
                entities,
                desc=f"[*] Creating {section_name} pages",
                position=0,
                leave=False,
            ):
                entity = entities[entity_id]
                entity_title = entity.get_title_with_id()
                entity_parent_id = entity.view_get("parent_id")
                parent_id, page_id = self.__create_page_by_id(
                    entity_title, entity_parent_id, ""
                )
                entity.update({"parent_id": parent_id, "link_id": page_id})
        logger.info(f"[✓] {section_name} pages created!")

    def __create_empty_page(self, page_title, parent_page_title):
        return self.__create_page(page_title, parent_page_title, "")

    def __create_page_by_id(
        self, page_title, parent_id, page_content
    ) -> tuple[str, str]:
        page = self.confluence.update_or_create(
            parent_id=parent_id, title=page_title, body=page_content
        )
        page_id = page["id"]
        return parent_id, page_id

    def __create_page(
        self, page_title, parent_page_title, page_content
    ) -> tuple[str, str]:
        parent_page = self.confluence.get_page_by_title(self.space, parent_page_title)
        return self.__create_page_by_id(
            parent_id=parent_page["id"],
            page_title=page_title,
            page_content=page_content,
        )

    def __attachment_exists(self, page_id, filename):
        attachments = self.confluence.get_attachments_from_content(
            page_id=page_id, filename=filename
        )
        return attachments["size"] != 0

    def __is_equal_size(self, conf_file, fs_file):
        fs_size = os.stat(fs_file).st_size
        conf_size = conf_file["extensions"]["fileSize"]
        return fs_size == conf_size

    def __get_page(self, page_title):
        return self.confluence.get_page_by_title(space=self.space, title=page_title)

    def __get_attachment(self, page_id, filename):
        attachment = self.confluence.get_attachments_from_content(
            page_id=page_id, filename=filename
        )
        if attachment["size"] != 0:
            return attachment["results"][0]
        else:
            return None

    def __upload_file(self, filename, name, page_id):
        return self.confluence.attach_file(
            filename=filename, name=name, page_id=page_id
        )["results"][0]

    def __replace_links(self, file, entity):
        """Convert links to files from MD format to HTML"""
        filename = file["title"]
        display_link = file["_links"]["webui"]
        file_link = file["_links"]["download"]
        img_re = re.compile(rf"!\[(.*?)\]\({filename}\)")
        matches = img_re.findall(entity.content)
        if matches is not None:
            for link_text in matches:
                entity.content = re.sub(
                    pattern=rf"!\[{link_text}\]\({filename}\)",
                    repl=rf"[![{link_text}]({file_link})]({display_link})",
                    string=entity.content,
                )
        return

    def __handle_attachments(self, entity, page_title):
        page = self.__get_page(page_title)
        for img in entity.image_files:
            img_name = os.path.basename(img)
            file = None
            if self.__attachment_exists(page["id"], img_name):
                file = self.__get_attachment(page["id"], img_name)
                if self.__is_equal_size(file, img):
                    continue
            else:
                file = self.__upload_file(img, img_name, page["id"])
            self.__replace_links(file, entity)
        return

    def write_entity(self, entity: Entity, title_with_id=False):
        """Render entity as Confluence page

        :param entity: Entity to render
        :type entity: Entity
        :param title_with_id: If True, then prepend title with ID, defaults to False
        :type title_with_id: bool, optional
        :return: Parent page ID and created entity page ID
        :rtype: tuple[str, str]
        """
        template_type = TemplateTypes.confluence
        template = env.get_template(entity.get_template_name(template_type))
        entity.enrich(template_type)
        entity.render_template(template, template_type)
        page_title = entity.get_title_with_id() if title_with_id else entity.get_title()
        if entity.entity_name == "response_actions_implementations":
            page_title = "⮩" + page_title
        self.__handle_attachments(entity, page_title)
        return self.__create_page_by_id(
            page_title, entity.view_get("parent_id"), entity.content
        )

    def render_entities_table(self, entities: list[Entity]):
        """Update summary page with entities table

        :param entities: Entities to render as table
        :type entities: list[Entity]
        :return: _description_
        :rtype: _type_
        """
        template = env.get_template(config.get("entities_table_confluence_template"))
        entities_list = []

        for entity_id in entities:
            entity = entities[entity_id]
            prefix = ""
            if entity.entity_name == "response_actions_implementations":
                prefix = "⮩"
            entities_list.append(
                {
                    "id": entity.view_get("id"),
                    "title": prefix + entity.get_title(),
                    "filename": entity.view_get("filename"),
                    "description": entity.view_get("description"),
                    "link_id": entity.view_get("link_id"),
                }
            )
            last_entity = entity

        data_to_render = {}
        data_to_render["entities_list"] = entities_list
        data_to_render.update(
            {"confluence_viewpage_url": config.get("confluence_viewpage_url")}
        )
        content = template.render(data_to_render)
        page = self.confluence.get_page_by_id(page_id=last_entity.view_get("parent_id"))
        return self.confluence.update_existing_page(
            page_id=page["id"], title=page["title"], body=content
        )

    def __render_stages_list(self, data_to_render):
        template = env.get_template(
            config.get("response_stages_main_confluence_template")
        )
        data_to_render.update(
            {"confluence_viewpage_url": config.get("confluence_viewpage_url")}
        )
        content = template.render(data_to_render)
        page = self.confluence.get_page_by_title(
            space=self.space, title=loc.get_localization("response_actions")
        )
        return self.confluence.update_existing_page(
            page_id=page["id"], title=page["title"], body=content
        )

    def render_infrastructure_profile(self, infrastructure_profile):
        """Create or update infrastructure profile page

        :param infrastructure_profile: Infrastructure profile entity
        :type infrastructure_profile: Entity
        :return: None
        :rtype: None
        """
        template_type = TemplateTypes.confluence
        template = env.get_template(
            infrastructure_profile.get_template_name(template_type)
        )
        infrastructure_profile.render_template(template, template_type)
        return self.confluence.update_or_create(
            parent_id=infrastructure_profile.view_get("parent_id"),
            title=infrastructure_profile.parent_title,
            body=infrastructure_profile.content,
        )
