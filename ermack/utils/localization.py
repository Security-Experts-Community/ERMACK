"""Module for multilingual localization support"""

from .utils import Utils as utils

config = utils.load_config("config.yml")

stages_mapping = {
    "preparation": "RS0001",
    "identification": "RS0002",
    "containment": "RS0003",
    "eradication": "RS0004",
    "recovery": "RS0005",
    "lessons_learned": "RS0006",
}

stages_names_mapping = {
    "RS0001": ["preparation", "подготовка"],
    "RS0002": ["identification", "идентификация"],
    "RS0003": ["containment", "сдерживание"],
    "RS0004": ["eradication", "ликвидация"],
    "RS0005": ["recovery", "восстановление"],
    "RS0006": ["lessons_learned", "выводы"],
}


class Localization:
    """
    Localization class

    contains all supported language mappings
    """

    def __init__(self):
        """Create localization class"""
        self.localization_mapping = {
            # root labels
            "introduction": {"ru": "Введение", "en": "Getting started"},
            "infrastructure_profiles": {
                "ru": "Профиль Инфраструктуры",
                "en": "Infrastructure Profile",
            },
            "usecases": {"ru": "Угрозы", "en": "Usecases"},
            "response_playbooks": {
                "ru": "Сценарии Реагирования",
                "en": "Response Playbooks",
            },
            "stage_actions_trees": {
                "ru": "Действия Реагирования",
                "en": "Response Actions",
            },
            "response_actions": {
                "ru": "Действия Реагирования",
                "en": "Response Actions",
            },
            "response_stages": {"ru": "Стадии Реагирования", "en": "Response Stages"},
            "stages": {"ru": "Стадии Реагирования", "en": "Response Stages"},
            "software": {"ru": "Продукты", "en": "Software"},
            "artifacts": {"ru": "Артефакты", "en": "Artifacts"},
            # entity fields
            "title": {"ru": "Название", "en": "Title"},
            "id": {"ru": "Идентификатор", "en": "ID"},
            "author": {"ru": "Автор", "en": "Author"},
            "creation_date": {"ru": "Дата создания", "en": "Creation Date"},
            "modification_date": {
                "ru": "Дата последнего изменения",
                "en": "Modification Date",
            },
            "other_tags": {"ru": "Метки", "en": "Tags"},
            "description": {"ru": "Описание", "en": "Description"},
            "workflow": {"ru": "Последовательность действий", "en": "Workflow"},
            "summary": {"ru": "Общие Сведения", "en": "Summary"},
            "configuration_name": {
                "ru": "Название Конфигурации",
                "en": "Configuration Name",
            },
            "company": {"ru": "Название Компании", "en": "Company Name"},
            "software_profile": {"ru": "Доступные Продукты", "en": "Software Profile"},
            "response_actions_implementations": {
                "ru": "Реализации Действий Реагирования",
                "en": "Response Actions Implementations",
            },
            "references": {"ru": "Ссылки", "en": "References"},
            "requirements": {"ru": "Требования", "en": "Requirements"},
            "tactics": {"ru": "Тактики ATT&amp;CK", "en": "ATT&amp;CK Tactics"},
            "techniques": {"ru": "Техники ATT&amp;CK", "en": "ATT&amp;CK Techniques"},
        }

        linked_locs = {}
        for mapping_id in self.localization_mapping:
            linked_locs[f"linked_{mapping_id}"] = {
                "ru": f"Связанные {self.localization_mapping[mapping_id]['ru']}",
                "en": f"Linked {self.localization_mapping[mapping_id]['en']}",
            }

    def get_en_name(self, term_name: str) -> str:
        """Get english localization of specified term

        :param term_name: Term to localize
        :type term_name: str
        :return: English localization of the term
        :rtype: str
        """
        if term_name in self.localization_mapping:
            return self.localization_mapping[term_name]["en"]

    def get_localization(self, term_name: str, lang: str = None) -> str:
        """Try to localize term based on default language

        If there is no default language configuration,
        english localization returns

        :param term_name: Term to localize
        :type term_name: str
        :param lang: Desired localization language, defaults to None
        :type lang: str, optional
        :return: Localized term
        :rtype: str
        """
        if term_name in self.localization_mapping:
            if lang is None:
                default_lang = config.get("default_localization_lang")
                if default_lang in self.localization_mapping[term_name]:
                    return self.localization_mapping[term_name][default_lang]
                else:
                    return self.localization_mapping[term_name]["en"]
            else:
                if lang in self.localization_mapping[term_name]:
                    return self.localization_mapping[term_name][lang]
                else:
                    return self.localization_mapping[term_name]["en"]
        else:
            return term_name

    def get_localizable_fields(self, entities):
        localized_fields = {}
        for field in entities:
            value = entities[field]
            localized = self.get_localization(field)
            if localized == field:
                localized_fields[field] = value
            else:
                localized_fields[field] = {"field_name": localized, "value": value}
        return localized_fields
