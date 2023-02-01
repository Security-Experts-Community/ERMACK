#!/usr/bin/env python3

"""This module contains the code to work with an abstract Entity class."""

import re
from glob import glob
from pathlib import Path

from jinja2 import Template

from ermack.render_knowledge_base import TemplateTypes
from ermack.utils.attack_mapping import ta_mapping, te_mapping
from ermack.utils.localization import Localization
from ermack.utils.utils import Utils as utils

config = utils.load_config("config.yml")
localization = Localization()


class Entity:
    """Class for an abstract entity"""

    def __init2__(self, base_path: str, file_name: str, entity_name: str):
        """
         Create Entity from a file

        :param base_path: Path to folder with entities
        :type base_path: str
        :param file_name: File name of the entity
        :type file_name: str
        :param entity_name: Entity name
        :type entity_name: str
        """
        self.yaml_file = f"{base_path}/{file_name}/{file_name}.yml"
        self.file_name = file_name
        self.config = config
        self.utils = utils
        self.entity_name = entity_name

        # NOTE: If you would like to add extra extensions
        # do not forget to add new file type to git lfs
        types = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg")
        image_file_patterns = [f"{base_path}/{file_name}/{ext}" for ext in types]
        self.image_files = []
        for pattern in image_file_patterns:
            self.image_files.extend(glob(pattern))

        # The name of the directory containing future markdown Response_Stages
        self.parent_title = self.entity_name

        self.parse_into_fields(self.yaml_file)
        self.set_file_path(self.yaml_file)

        self.view = self.parsed_file.copy()

        # self.env = env
        self.entities_map = {}
        self.templates = {}
        self.update({"summary": None})
        self.process_tags()

        self.localization_mapping = localization.localization_mapping

        fields_names = self.localization_mapping.keys()
        tmp = {}
        for key in fields_names:
            tmp[f"linked_{key}"] = self.localization_mapping[key]
        self.localization_mapping.update(tmp)

    def handle_path(self, relative_file_path: str) -> None:
        self.yaml_file = str(relative_file_path.absolute())
        self.file_name = relative_file_path.name

        # NOTE: If you want to add extra extensions
        # do not forget to add new file type to git lfs
        types = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg")
        parent_folder = str(relative_file_path.parent)
        image_file_patterns = [f"{parent_folder}/{ext}" for ext in types]
        self.image_files = []
        for pattern in image_file_patterns:
            self.image_files.extend(glob(pattern))
        self.set_file_path(file_path=self.file_name)

    @classmethod
    def from_file(cls, file_path: Path, entity_name: str) -> None:
        relative_file_path = Path(file_path)
        content = utils.read_yaml_file(relative_file_path)
        EntityClass = cls.__bases__[0]
        entity = EntityClass(content=content, entity_name=entity_name)
        entity.yaml_file = str(relative_file_path.absolute())
        entity.file_name = relative_file_path.name

        # NOTE: If you want to add extra extensions
        # do not forget to add new file type to git lfs
        types = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg")
        parent_folder = str(relative_file_path.parent)
        image_file_patterns = [f"{parent_folder}/{ext}" for ext in types]
        entity.image_files = []
        for pattern in image_file_patterns:
            entity.image_files.extend(glob(pattern))

        entity.set_file_path(file_path=entity.file_name)
        return entity

    def __init__(self, content: dict, entity_name: str):
        if not isinstance(content, dict):
            raise TypeError(
                f"Can't create entity from {type(content).__name__} type.\
                     Expected type: dict"
            )
        self.config = config
        self.utils = utils
        self.entity_name = entity_name
        self.parent_title = self.entity_name
        self.parsed_file = content
        # self.parse_from_string(content)
        self.view = self.parsed_file.copy()
        self.entities_map = {}
        self.templates = {}
        self.update({"summary": None})
        self.process_tags()
        self.localization_mapping = localization.localization_mapping
        fields_names = self.localization_mapping.keys()
        extra_fields = {}
        for key in fields_names:
            extra_fields[f"linked_{key}"] = self.localization_mapping[key]
        self.localization_mapping.update(extra_fields)

    def set_parent_title(self, parent_title):
        self.parent_title = parent_title

    def enrich(self, template_type: TemplateTypes):
        pass

    @staticmethod
    def get_entity_name():
        raise Exception("Method not implemented!")

    @staticmethod
    def get_acronym():
        raise Exception("Method not implemented!")

    @staticmethod
    def have_special_link_name_for(entity_class):
        return None

    def get_title_(self):
        lang = config.get("default_localization_lang")
        title = self.parsed_file.get("title")
        if title is None:
            return None
        if "type" in title and title["type"] == "text":
            if lang in title:
                return title[lang]
            else:
                return title["en"]
        title_re = re.compile(r"(?:[A-Z]{1,3}_?\d{4}_)(\w+)")
        if title_re.match(title):
            result = title_re.search(title)
            return result.group(1).replace("_", " ").title()
        else:
            return title

    def get_title(self):
        title = self.get_title_()
        if title is not None:
            title = self.utils.normalize_react_title(
                title, self.config.get("titlefmtrules")
            )
        return title

    def get_title_with_id(self):
        title = self.get_title_()
        if title is not None:
            title = self.utils.normalize_react_title(
                title, self.config.get("titlefmtrules")
            )
        return f"{self.get('id')}: {title}"

    def set_entity_mapping(self, mapping):
        self.entities_map = mapping

    def extract_id(self, string_starts_with_id):
        id_re = re.compile(r"(([A-Z]{1,3})_?\d{4})(_\w+)?")
        if id_re.match(string_starts_with_id):
            result = id_re.search(string_starts_with_id)
            return result.group(1).replace("_", "")
        else:
            return ""

    def update_response_actions_links(self, mapping):
        self.update_entity_links(entity_key="linked_response_actions", mapping=mapping)
        return

    def update_artifacts_links(self, mapping):
        self.update_entity_links(entity_key="linked_artifacts", mapping=mapping)
        return

    def update_usecases_links(self, mapping):
        self.update_entity_links(entity_key="linked_usecases", mapping=mapping)
        return

    def update_playbooks_links(self, mapping):
        self.update_entity_links(
            entity_key="linked_response_playbooks", mapping=mapping
        )
        return

    def update_software_links(self, mapping):
        self.update_entity_links(entity_key="linked_software", mapping=mapping)
        return

    def update_entity_links(
        self, entity_key, mapping, get_id=lambda id: id, enrich=lambda view, data: view
    ):
        if entity_key not in self.view:
            return
        e = []
        entities = self.view_get(entity_key)
        if isinstance(entities, list):
            for entity in self.view_get(entity_key):
                entity_id = get_id(entity)
                if entity_id in mapping:
                    view = {
                        "id": entity_id,
                        "title": mapping[entity_id].get_title(),
                        "filename": mapping[entity_id].view_get("filename"),
                        "link_id": mapping[entity_id].view_get("link_id"),
                    }
                    view = enrich(view, entity)
                    e.append(view)
            self.update({entity_key: e})
        else:
            entity_id = self.view_get(entity_key)
            if entity_id is not None:
                view = {
                    "id": entity_id,
                    "title": mapping[entity_id].get_title(),
                    "filename": mapping[entity_id].view_get("filename"),
                    "link_id": mapping[entity_id].view_get("link_id"),
                }
                view = enrich(view, entity_key)
                e.append(view)
                self.update({entity_key: e})
        return

    def infer_related_entities(self, related_entity_name, relation_mapping):
        related_entities_views = []
        entity_id = self.view["id"]
        if entity_id in relation_mapping:
            related_entities = relation_mapping[entity_id]
            for related_entity in related_entities:
                related_entities_views.append(
                    {
                        "id": related_entity.view_get("id"),
                        "title": related_entity.get_title(),
                        "filename": related_entity.view_get("filename"),
                        "link_id": related_entity.view_get("link_id"),
                    }
                )
            self.update({related_entity_name: related_entities_views})
        return

    def process_tags(self):
        if "tags" not in self.parsed_file:
            return

        # MITRE ATT&CK Tactics and Techniques
        tactic = []
        tactic_re = re.compile(r"attack\.\w\D+$")
        technique = []
        technique_re = re.compile(r"attack\.t\d{4}(\.\d{3})?$")

        generic_tag_format = re.compile(r"(\w+)\.(\w+)(?:\|\((.*?)\))?")

        other_tags = []

        tags = self.get("tags")
        if tags is not None:
            for tag in tags:
                if tactic_re.match(tag):
                    tactic.append(ta_mapping.get(tag))
                elif technique_re.match(tag):
                    te = tag.upper()[7:]
                    technique.append((te_mapping.get(te), te))
                else:
                    if generic_tag_format.match(tag):
                        result = generic_tag_format.search(tag)
                        tag_view = {
                            "type": result.group(1).title(),
                            "value": result.group(2).title(),
                        }
                        if result.group(3):
                            tag_view["link"] = result.group(3)
                        other_tags.append(tag_view)
                    else:
                        other_tags.append(
                            {"type": "Other", "value": tag.replace("_", " ").title()}
                        )

            if len(tactic) > 0:
                self.update({"tactics": tactic})
            if len(technique) > 0:
                self.update({"techniques": technique})
            if len(other_tags) > 0:
                self.update({"other_tags": other_tags})

    def get(self, field, lang=None):
        if lang is None:
            lang = config.get("default_localization_lang")
        entity = self.parsed_file.get(field)
        if entity is None:
            return None

        if "type" in entity and entity["type"] == "text":
            if lang in entity:
                return entity[lang]
            return entity["en"]
        return entity

    # def update(self, kv_pairs):
    #     lang = config.get("default_localization_lang")
    #     for key in kv_pairs:
    #         if key not in self.view:
    #             self.view[key] = kv_pairs[key]
    #             continue
    #         entity = self.view.get(key)
    #         if entity is not None and "type" in entity and entity["type"] == "text":
    #             self.view[key][lang] = kv_pairs[key]
    #         else:
    #             self.view[key] = kv_pairs[key]
    #     return

    def update(self, updated_values):
        for key in updated_values:
            self.view[key] = updated_values[key]
        return

    def data(self):
        return self.parsed_file.copy()

    def set_file_path(self, file_path):
        self.parsed_file["filepath"] = file_path
        self.parsed_file["filename"] = (
            file_path.split("/")[-1].split("\\")[-1].replace(".yml", "")
        )
        self.view["filepath"] = self.parsed_file["filepath"]
        self.view["filename"] = self.parsed_file["filename"]

    def parse_into_fields(self, yaml_file):
        """Description"""

        self.parsed_file = utils.read_yaml_file(yaml_file)

    def parse_from_string(self, yaml_content):
        self.parsed_file = utils.parse_yaml_from_string(yaml_content)

    def view_get(self, field, lang=None):
        if lang is None:
            lang = config.get("default_localization_lang")
        entity = self.view.get(field)
        if entity is None:
            return None
        if "type" in entity and entity["type"] == "text":
            if lang in entity:
                return entity[lang]
            return entity["en"]
        return entity

    def get_localized_view(self):
        view = {}
        for entity in self.view:
            view[entity] = self.view_get(entity)
        return view

    def get_localizable_fields(self, entities):
        lang = config.get("default_localization_lang")
        l = {}
        for field in entities:
            value = entities[field]
            if (
                field in self.localization_mapping
                or f"linked_{field}" in self.localization_mapping
            ):
                if lang in self.localization_mapping[field]:
                    l[field] = {
                        "field_name": self.localization_mapping[field][lang],
                        "value": value,
                    }
                else:
                    l[field] = {
                        "field_name": self.localization_mapping[field]["en"],
                        "value": value,
                    }
            else:
                l[field] = value
        return l

    def get_template_name(self, template_type: TemplateTypes):
        """Get template file name by template type for this entity

        :param template_type: Type of template to query
        :type template_type: SupportedTemplateTypes
        :return: Template file name
        :rtype: str
        """
        return self.config.get(self.templates[template_type])

    def render_template(self, template: Template, template_type: TemplateTypes):
        """Fill compiled jinja2 template with entity fields

        :param template: Compiled jinja2 template
        :type template: Template
        :param template_type: Template type
        :type template_type: SupportedTemplateTypes
        :raises Exception: If template_type is unsupported
        :raises Exception: If current entity have no specified template type
        """
        if template_type not in TemplateTypes:
            raise Exception(f"Bad template_type: {template_type}")

        if "description" in self.view:
            self.update({"description": self.get("description").strip()})

        self.update({"title": self.get_title()})

        self.update(
            {"entity": {"field_name": localization.get_localization(self.entity_name)}}
        )

        if template_type not in self.templates:
            raise Exception(
                f"There is no {template_type} template for {self.entity_name} entity"
            )

        if template_type is TemplateTypes.confluence:
            self.update(
                {"confluence_viewpage_url": self.config.get("confluence_viewpage_url")}
            )

        self.content = template.render(self.view)
